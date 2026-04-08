"""
XAUUSD AI Analyst — FastAPI Backend (Multi-Timeframe Scalper Edition)
Run with: uvicorn main:app --reload --port 8000

Pipeline:
  MT5 Data (M1/M5/M15/H1) → 4 TF Agents (parallel) → Scalper Synthesizer → Trade Plan
"""
import uuid
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from models.schemas import (
    FullAnalysis, RiskInput, RiskOutput,
    MT5Status, PriceTick,
    TechnicalAnalysis, TimeframeAnalysis,
)
from services import mt5_bridge
from services.utils import get_current_session, calculate_risk
from agents.tf_agents import analyze_all_timeframes
from agents.scalper_synthesizer import synthesize_scalp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── In-memory cache ───────────────────────────────────────────
latest_analysis: Optional[FullAnalysis] = None
scheduler = AsyncIOScheduler()


# ── Helper: build legacy TechnicalAnalysis from MTF results ──
def _build_legacy_technical(tf_results: dict) -> Optional[TechnicalAnalysis]:
    """Build a legacy TechnicalAnalysis from M5 (primary) for UI backwards compat."""
    primary: Optional[TimeframeAnalysis] = tf_results.get("M5") or tf_results.get("M15")
    if primary is None:
        return None
    return TechnicalAnalysis(
        trend=primary.trend,
        strength=primary.strength,
        support_levels=primary.support_levels,
        resistance_levels=primary.resistance_levels,
        momentum=primary.momentum,
        key_observations=primary.key_observations,
    )


# ── Main analysis pipeline ────────────────────────────────────
async def run_full_analysis() -> FullAnalysis:
    global latest_analysis
    logger.info("🔍 Running MTF scalper analysis pipeline...")

    # 1. Get current price
    tick = mt5_bridge.get_tick()
    if tick is None:
        raise HTTPException(
            status_code=503,
            detail="No price data. MT5 connection required."
        )
    current_price = (tick.bid + tick.ask) / 2

    # 2. Fetch scalper candles (M1, M5, M15, H1 in one call)
    candles_by_tf = mt5_bridge.get_scalper_candles()
    total_candles = sum(len(v) for v in candles_by_tf.values())

    # 3. Run 4 TF agents concurrently
    logger.info("⚡ Launching M1/M5/M15/H1 agents in parallel...")
    tf_results = await analyze_all_timeframes(candles_by_tf)

    # 4. Scalper synthesizer — produces final trade plan
    session = get_current_session()
    setup = await synthesize_scalp(current_price, tf_results, session)

    # 5. Build legacy technical for UI panels that haven't migrated yet
    legacy_technical = _build_legacy_technical(tf_results)

    # 6. Serialise tf_results for JSON response
    tf_dict = {}
    for tf, res in tf_results.items():
        tf_dict[tf] = res.dict() if res is not None else None

    # 7. Build and cache result
    analysis = FullAnalysis(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(timezone.utc),
        current_price=current_price,
        session=session,
        timeframe_analyses=tf_dict,
        setup=setup,
        technical=legacy_technical,
        candles_used=total_candles,
        source=tick.source,
    )
    latest_analysis = analysis
    logger.info(
        "✅ Scalper analysis complete — Bias:%s | Confidence:%d%% | Primary TF:%s",
        setup.bias, setup.confidence, setup.primary_timeframe
    )
    return analysis


# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 XAUUSD Scalper Analyst starting up...")
    if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
        mt5_bridge.initialize(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER)
    else:
        logger.warning("MT5 credentials not set.")

    scheduler.add_job(
        run_full_analysis,
        "interval",
        seconds=settings.ANALYSIS_INTERVAL_SECONDS,
        id="auto_analysis",
    )
    scheduler.start()
    logger.info("⏱ Auto-analysis every %ds", settings.ANALYSIS_INTERVAL_SECONDS)

    yield

    scheduler.shutdown()
    mt5_bridge.shutdown()
    logger.info("👋 Shutdown complete.")


# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="XAUUSD Scalper AI Analyst",
    description="Multi-timeframe Gold scalping analysis — M1/M5/M15/H1 agents + synthesizer",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "XAUUSD Scalper AI Analyst",
        "version": "2.0.0",
        "pipeline": "M1 + M5 + M15 + H1 agents → Scalper Synthesizer",
    }


@app.get("/health", tags=["Health"])
async def health():
    tick = mt5_bridge.get_tick()
    return {
        "status": "ok",
        "mt5": mt5_bridge.get_status().dict(),
        "has_price": tick is not None,
        "has_analysis": latest_analysis is not None,
        "session": get_current_session(),
        "pipeline": "MTF_SCALPER_V2",
    }


# ── Price ─────────────────────────────────────────────────────

@app.get("/price", response_model=PriceTick, tags=["Price"])
async def get_price():
    tick = mt5_bridge.get_tick()
    if tick is None:
        raise HTTPException(status_code=503, detail="No price data available.")
    return tick


# ── MT5 ───────────────────────────────────────────────────────

@app.get("/mt5/status", response_model=MT5Status, tags=["MT5"])
async def mt5_status():
    return mt5_bridge.get_status()


# ── Analysis ──────────────────────────────────────────────────

@app.get("/analysis", response_model=FullAnalysis, tags=["Analysis"])
async def get_latest_analysis():
    if latest_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis yet. POST to /analysis/run to generate one."
        )
    return latest_analysis


@app.post("/analysis/run", response_model=FullAnalysis, tags=["Analysis"])
async def trigger_analysis():
    """Run full MTF scalper pipeline: M1 + M5 + M15 + H1 agents → synthesize."""
    return await run_full_analysis()


# ── Per-TF endpoints (new) ────────────────────────────────────

@app.get("/analysis/timeframes", tags=["Analysis"])
async def get_timeframe_analyses():
    """Return the individual per-timeframe analyses from the latest run."""
    if latest_analysis is None or latest_analysis.timeframe_analyses is None:
        raise HTTPException(status_code=404, detail="No analysis yet.")
    return {
        "timeframes": latest_analysis.timeframe_analyses,
        "session": latest_analysis.session,
        "current_price": latest_analysis.current_price,
        "timestamp": latest_analysis.timestamp,
    }


@app.get("/analysis/timeframes/{tf}", tags=["Analysis"])
async def get_single_timeframe(tf: str):
    """Return analysis for a single timeframe (M1, M5, M15, H1)."""
    tf = tf.upper()
    if tf not in ["M1", "M5", "M15", "H1"]:
        raise HTTPException(status_code=400, detail="Valid timeframes: M1, M5, M15, H1")
    if latest_analysis is None or latest_analysis.timeframe_analyses is None:
        raise HTTPException(status_code=404, detail="No analysis yet.")
    result = latest_analysis.timeframe_analyses.get(tf)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No data for {tf}")
    return result


# ── Risk Calculator ───────────────────────────────────────────

@app.post("/risk/calculate", response_model=RiskOutput, tags=["Risk"])
async def risk_calculator(data: RiskInput):
    if data.risk_percent <= 0 or data.risk_percent > 10:
        raise HTTPException(status_code=400, detail="Risk percent must be between 0 and 10.")
    return calculate_risk(data)