import { useState, useEffect, useCallback } from 'react';
import './index.css';
import { api } from './api';
import Header         from './components/Header';
import AnalystFeed    from './components/AnalystFeed';
import TechnicalPanel from './components/TechnicalPanel';
import NewsSentiment  from './components/NewsSentiment';
import ChartVision    from './components/ChartVision';
import RiskCalculator from './components/RiskCalculator';
import ManualPrice    from './components/ManualPrice';

export default function App() {
  const [analysis, setAnalysis]   = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [mt5Connected, setMt5]    = useState(false);

  // Load cached analysis on mount
  useEffect(() => {
    api.getAnalysis()
      .then(setAnalysis)
      .catch(() => {}); // 404 is expected if no analysis yet

    api.mt5Status()
      .then(s => setMt5(s.connected))
      .catch(() => {});
  }, []);

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.runAnalysis();
      setAnalysis(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="dashboard">
      <Header
        onRunAnalysis={runAnalysis}
        analysisTime={analysis?.timestamp}
        loading={loading}
      />

      {/* Error bar */}
      {error && (
        <div style={{
          background: 'rgba(255,69,96,0.08)',
          border: '1px solid rgba(255,69,96,0.3)',
          borderLeft: '3px solid var(--red)',
          padding: '0.5rem 1.5rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.65rem',
          color: 'var(--red)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span>⚠ {error}</span>
          <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', color: 'var(--red)', cursor: 'pointer', fontSize: '1rem' }}>×</button>
        </div>
      )}

      {/* Loading overlay hint */}
      {loading && (
        <div style={{
          background: 'rgba(0,200,255,0.04)',
          borderBottom: '1px solid var(--gold-line)',
          padding: '0.4rem 1.5rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.6rem',
          color: 'var(--gold)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          letterSpacing: '0.1em',
        }}>
          <span className="spinner" style={{ width: 12, height: 12 }} />
          FETCHING PRICE DATA → RUNNING TECHNICAL AGENT → RUNNING FUNDAMENTAL AGENT → SYNTHESIZING TRADE PLAN…
        </div>
      )}

      {/* Main grid */}
      <div className="main-grid">
        {/* Row 1: Trade Setup (wide) + Technical */}
        <AnalystFeed analysis={analysis} />
        <TechnicalPanel analysis={analysis} />

        {/* Row 2: News + Chart Vision + Risk */}
        <NewsSentiment analysis={analysis} />
        <ChartVision />
        <RiskCalculator analysis={analysis} />

        {/* Row 3: Manual price (shown always, useful when MT5 offline) */}
        <ManualPrice />

        {/* Row 3: Analysis metadata */}
        {analysis && (
          <div className="card span-2 fade-up" style={{ animationDelay: '0.7s' }}>
            <div className="card-header">
              <span className="card-title">◫ Analysis Log</span>
              <span className="card-badge">ID: {analysis.id}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
              {[
                { label: 'TIMESTAMP', value: new Date(analysis.timestamp).toLocaleString() },
                { label: 'PRICE AT ANALYSIS', value: `$${analysis.current_price?.toFixed(2)}` },
                { label: 'DATA SOURCE', value: analysis.source },
                { label: 'CANDLES ANALYZED', value: analysis.candles_used },
                { label: 'TECHNICAL TREND', value: `${analysis.technical.trend} (${analysis.technical.strength})` },
                { label: 'SENTIMENT SCORE', value: analysis.fundamental?.sentiment_score > 0 ? `+${analysis.fundamental.sentiment_score?.toFixed(2)}` : analysis.fundamental?.sentiment_score?.toFixed(2) },
                { label: 'NEWS FETCHED', value: analysis.news_items?.length || 0 },
                { label: 'CONFIDENCE', value: `${analysis.setup?.confidence}%` },
              ].map((row, i) => (
                <div key={i}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.1em', marginBottom: '0.15rem' }}>{row.label}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--gold)' }}>{row.value}</div>
                </div>
              ))}
            </div>

            {/* Fundamental summary */}
            {analysis.fundamental?.news_summary && (
              <>
                <div className="gold-line" />
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.15em', marginBottom: '0.4rem' }}>FUNDAMENTAL SUMMARY</div>
                <div style={{ fontSize: '0.75rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                  {analysis.fundamental.news_summary}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '0.6rem 1.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--bg-card)',
      }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-dim)', letterSpacing: '0.15em' }}>
          AURUM ANALYST · XAUUSD AI TRADING SYSTEM · FOR EDUCATIONAL USE ONLY
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-dim)', letterSpacing: '0.1em' }}>
          NOT FINANCIAL ADVICE · ALWAYS MANAGE YOUR RISK
        </div>
      </footer>
    </div>
  );
}
