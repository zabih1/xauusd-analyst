# XAUUSD Analyst — React Dashboard

## 🚀 Quick Start

```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

> Make sure the **backend is running** at `http://localhost:8000` first!

---

## 🎨 Dashboard Panels

| Panel | Description |
|-------|-------------|
| **Header** | Live XAU/USD price (polls every 2s), MT5 status, session clock, RUN ANALYSIS button |
| **⬡ Trade Setup** | Core panel — AI-generated bias, entry zone, SL, TP, R:R, reasoning, invalidation |
| **◈ Technical** | Support/resistance levels, trend, momentum, key observations |
| **◉ Sentiment** | News sentiment score, DXY outlook, macro factors, live headlines |
| **◎ Chart Vision** | Drag & drop chart screenshot → Gemini pattern recognition |
| **⊛ Risk Calculator** | Lot size calculator with auto-fill from current analysis |
| **⌨ Manual Price** | Set price manually when MT5 is offline |
| **◫ Analysis Log** | Full metadata of last analysis run |

---

## ⚙️ Configuration

Default backend URL: `http://localhost:8000`

To change it, create a `.env` file in the `frontend/` directory:
```
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔄 Workflow

1. Backend auto-refreshes analysis every 5 minutes
2. Click **⚡ RUN ANALYSIS** for immediate fresh analysis
3. Price ticker updates every 2 seconds from MT5 (or manual)
4. Drop a chart screenshot into **Chart Vision** anytime for pattern analysis
5. Use **Auto-Fill** in Risk Calculator to pull levels from latest analysis

---

## 📁 Components

```
src/
├── App.jsx              ← Main layout, state management
├── api.js               ← All backend API calls
├── index.css            ← Black & gold design system
└── components/
    ├── Header.jsx        ← Price ticker, status, run button
    ├── AnalystFeed.jsx   ← Trade setup (main panel)
    ├── TechnicalPanel.jsx← S/R levels, trend, observations
    ├── NewsSentiment.jsx ← News + macro sentiment
    ├── ChartVision.jsx   ← Screenshot upload + analysis
    ├── RiskCalculator.jsx← Lot size calculator
    └── ManualPrice.jsx   ← Manual price input
```
