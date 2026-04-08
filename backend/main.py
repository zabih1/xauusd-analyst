"""
XAUUSD AI Analyst — FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
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
    MT5Status, ManualPriceInput, PriceTick
)
from services import mt5_bridge
from services.utils import get_current_session, calculate_risk
from agents.technical import analyze_technical
from agents.synthesizer import synthesize

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ── In-memory cache for latest analysis ──────────────────────
latest_analysis: Optional[FullAnalysis] = None
scheduler = AsyncIOScheduler()


# ── Analysis pipeline ─────────────────────────────────────────
async def run_full_analysis() -> FullAnalysis:
    global latest_analysis
    logger.info("🔍 Running full analysis pipeline...")

    # 1. Get current price
    tick = mt5_bridge.get_tick()
    if tick is None:
        raise HTTPException(status_code=503, detail="No price data available. Connect MT5 or set manual price.")
    current_price = (tick.bid + tick.ask) / 2

    # 2. Fetch candles (multi-timeframe)
    candles_by_tf = mt5_bridge.get_multi_timeframe_candles()

    # 3. Run agents
    technical = await analyze_technical(candles_by_tf)

    # 4. Synthesize final trade plan
    session = get_current_session()
    setup = await synthesize(current_price, technical, session)

    # 5. Build result
    total_candles = sum(len(v) for v in candles_by_tf.values())
    analysis = FullAnalysis(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(timezone.utc),
        current_price=current_price,
        session=session,
        technical=technical,
        setup=setup,
        candles_used=total_candles,
        source=tick.source,
    )
    latest_analysis = analysis
    logger.info("✅ Analysis complete — Bias: %s | Confidence: %d%%", setup.bias, setup.confidence)
    return analysis




# ── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("🚀 XAUUSD Analyst starting up...")
    if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
        mt5_bridge.initialize(settings.MT5_LOGIN, settings.MT5_PASSWORD, settings.MT5_SERVER)
    else:
        logger.warning("MT5 credentials not set — running in manual price mode.")

    # schedule auto-refresh
    scheduler.add_job(
        run_full_analysis,
        "interval",
        seconds=settings.ANALYSIS_INTERVAL_SECONDS,
        id="auto_analysis",
    )
    scheduler.start()
    logger.info("⏱ Auto-analysis every %ds", settings.ANALYSIS_INTERVAL_SECONDS)

    yield

    # shutdown
    scheduler.shutdown()
    mt5_bridge.shutdown()
    logger.info("👋 Shutdown complete.")


# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="XAUUSD AI Analyst",
    description="Real-time Gold trading analysis powered by AI agents",
    version="1.0.0",
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
    return {"status": "online", "service": "XAUUSD AI Analyst", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    tick = mt5_bridge.get_tick()
    return {
        "status": "ok",
        "mt5": mt5_bridge.get_status().dict(),
        "has_price": tick is not None,
        "has_analysis": latest_analysis is not None,
        "session": get_current_session(),
    }


# ── Price ─────────────────────────────────────────────────────

@app.get("/price", response_model=PriceTick, tags=["Price"])
async def get_price():
    """Get current XAUUSD tick price."""
    tick = mt5_bridge.get_tick()
    if tick is None:
        raise HTTPException(status_code=503, detail="No price data. Connect MT5 or POST to /price/manual")
    return tick


@app.post("/price/manual", response_model=PriceTick, tags=["Price"])
async def set_manual_price(data: ManualPriceInput):
    """Manually set current price when MT5 is not connected."""
    mt5_bridge.set_manual_price(data.bid, data.ask)
    tick = mt5_bridge.get_tick()
    return tick


# ── MT5 ───────────────────────────────────────────────────────

@app.get("/mt5/status", response_model=MT5Status, tags=["MT5"])
async def mt5_status():
    return mt5_bridge.get_status()


# ── Analysis ─────────────────────────────────────────────────

@app.get("/analysis", response_model=FullAnalysis, tags=["Analysis"])
async def get_latest_analysis():
    """Return cached latest analysis (no API call)."""
    if latest_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis yet. POST to /analysis/run to generate one.")
    return latest_analysis


@app.post("/analysis/run", response_model=FullAnalysis, tags=["Analysis"])
async def trigger_analysis():
    """Trigger a fresh full analysis pipeline (calls LLM agents)."""
    return await run_full_analysis()





# ── Risk Calculator ───────────────────────────────────────────

@app.post("/risk/calculate", response_model=RiskOutput, tags=["Risk"])
async def risk_calculator(data: RiskInput):
    """Calculate lot size and risk metrics for a trade setup."""
    if data.risk_percent <= 0 or data.risk_percent > 10:
        raise HTTPException(status_code=400, detail="Risk percent must be between 0 and 10.")
    return calculate_risk(data)
