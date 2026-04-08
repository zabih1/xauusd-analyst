# XAUUSD AI Analyst — Backend Setup Guide

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

> ⚠️ **MetaTrader5 Python package only works on Windows.**
> On Mac/Linux, the system will run in disconnected mode.

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your keys:
```

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx   # Required
MT5_LOGIN=12345678                          # Your MT5 account number
MT5_PASSWORD=yourpassword
MT5_SERVER=YourBroker-Live                  # e.g. ICMarkets-Live01
ANALYSIS_INTERVAL_SECONDS=300              # Auto-refresh every 5 min
```

### 3. Run the server
```bash
uvicorn main:app --reload --port 8000
```

Server starts at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server + MT5 status |
| GET | `/price` | Live XAUUSD tick |
| GET | `/mt5/status` | MT5 connection details |
| POST | `/analysis/run` | 🔥 Trigger fresh AI analysis |
| GET | `/analysis` | Get cached latest analysis |
| GET | `/analysis/timeframes` | Per-timeframe analysis results |
| GET | `/analysis/timeframes/{tf}` | Single timeframe (M1, M5, M15, H1) |
| POST | `/risk/calculate` | Calculate lot size / risk |

---

## 🤖 AI Analysis Pipeline

```
MT5 Data (M1/M5/M15/H1) → 4 TF Agents (parallel) → Scalper Synthesizer → Trade Plan
```

**Models used:**
- `openai/gpt-4.1-nano` — Technical analysis & Synthesis

---

## 🔌 MT5 Connection

The backend uses the **official MetaTrader5 Python library** (Windows only).

If MT5 is not available:
1. Start the server normally — it detects and skips MT5
2. Analysis still works if another data source provides candles

**To enable live candles without MT5 Python lib**, you can also use the ZeroMQ EA bridge (advanced — ask for setup guide).

---

## 📁 Project Structure

```
backend/
├── main.py              ← FastAPI app + all routes
├── config.py            ← Settings from .env
├── requirements.txt
├── .env.example
├── agents/
│   ├── technical.py     ← LLM: candle analysis
│   ├── tf_agents.py     ← Multi-timeframe parallel agents
│   ├── synthesizer.py   ← LLM: final trade plan
│   └── scalper_synthesizer.py ← Scalper-specific synthesis
├── services/
│   ├── openrouter.py    ← OpenRouter LLM API client
│   ├── mt5_bridge.py    ← MT5 data fetcher
│   └── utils.py         ← Session clock, risk calculator
└── models/
    └── schemas.py       ← All Pydantic data models
```

---

## 🧪 Test Without MT5

```bash
# 1. Run full analysis
curl -X POST http://localhost:8000/analysis/run

# 2. Get the result
curl http://localhost:8000/analysis
```

---

## 🎯 Next Steps

- **Trade journal** with AI performance coaching
- **Advanced risk management** tooling