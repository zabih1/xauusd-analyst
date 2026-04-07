# XAUUSD AI Analyst — Backend Setup Guide

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

> ⚠️ **MetaTrader5 Python package only works on Windows.**
> On Mac/Linux, the system runs in manual price mode automatically.

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your keys:
```

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx   # Required
NEWS_API_KEY=xxxxxxxxxxxxxx                 # Optional (free at newsapi.org)
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
| POST | `/price/manual` | Set price manually `{"bid": 3285.0, "ask": 3285.5}` |
| GET | `/mt5/status` | MT5 connection details |
| POST | `/analysis/run` | 🔥 Trigger fresh AI analysis |
| GET | `/analysis` | Get cached latest analysis |
| POST | `/vision/analyze` | Upload chart screenshot for AI analysis |
| GET | `/news` | Latest gold news headlines |
| POST | `/risk/calculate` | Calculate lot size / risk |

---

## 🤖 AI Analysis Pipeline

```
MT5 Data (OHLCV) ──┐
                    ├──→ Technical Agent (Gemini Flash)  ──┐
News Headlines  ────┤                                      ├──→ Synthesizer (Gemini Pro) → Trade Plan
                    └──→ Fundamental Agent (Gemini Flash) ─┘
```

**Models used:**
- `google/gemini-2.5-flash` — Technical & Fundamental analysis (fast, cheap)
- `google/gemini-2.5-pro` — Final synthesis & chart vision (powerful)

---

## 🔌 MT5 Connection

The backend uses the **official MetaTrader5 Python library** (Windows only).

If MT5 is not available:
1. Start the server normally — it detects and skips MT5
2. Use `POST /price/manual` to feed current price
3. Analysis still works — just without live candle data

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
│   ├── technical.py     ← Gemini Flash: candle analysis
│   ├── fundamental.py   ← Gemini Flash: news/macro analysis
│   ├── synthesizer.py   ← Gemini Pro: final trade plan
│   └── vision.py        ← Gemini Pro Vision: chart screenshot
├── services/
│   ├── openrouter.py    ← OpenRouter/Gemini API client
│   ├── mt5_bridge.py    ← MT5 data fetcher
│   ├── news_fetcher.py  ← RSS + NewsAPI aggregator
│   └── utils.py         ← Session clock, risk calculator
└── models/
    └── schemas.py       ← All Pydantic data models
```

---

## 🧪 Test Without MT5

```bash
# 1. Set a manual price
curl -X POST http://localhost:8000/price/manual \
  -H "Content-Type: application/json" \
  -d '{"bid": 3285.40, "ask": 3285.90}'

# 2. Run full analysis
curl -X POST http://localhost:8000/analysis/run

# 3. Get the result
curl http://localhost:8000/analysis
```

---

## 🎯 Next Steps

- **Phase 2**: React dashboard (black & gold theme) consuming these APIs
- **Phase 3**: Chart vision panel with drag-and-drop upload
- **Phase 4**: News sentiment panel with live feed
- **Phase 5**: Trade journal with Gemini performance coaching