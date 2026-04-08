import { useState, useEffect, useCallback } from 'react';
import './index.css';
import { api } from './api';
import Header from './components/Header';
import AnalystFeed from './components/AnalystFeed';
import TechnicalPanel from './components/TechnicalPanel';
import MTFPanel from './components/MTFPanel';

import RiskCalculator from './components/RiskCalculator';


export default function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mt5Connected, setMt5] = useState(false);

  useEffect(() => {
    api.getAnalysis()
      .then(setAnalysis)
      .catch(() => { });

    api.mt5Status()
      .then(s => setMt5(s.connected))
      .catch(() => { });
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
          FETCHING M1/M5/M15/H1 CANDLES → RUNNING 4 TF AGENTS IN PARALLEL → SCALPER SYNTHESIZER…
        </div>
      )}

      {/* Main grid */}
      <div className="main-grid">

        {/* Row 1: MTF Panel spans full width */}
        <MTFPanel analysis={analysis} />

        {/* Row 2: Trade Setup (wide) + Technical */}
        <AnalystFeed analysis={analysis} />
        <TechnicalPanel analysis={analysis} />

        {/* Row 3: Risk Calculator */}
        <RiskCalculator analysis={analysis} />


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
          AURUM ANALYST · XAUUSD MTF SCALPER · M1/M5/M15/H1 AGENTS · FOR EDUCATIONAL USE ONLY
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-dim)', letterSpacing: '0.1em' }}>
          NOT FINANCIAL ADVICE · ALWAYS MANAGE YOUR RISK
        </div>
      </footer>
    </div>
  );
}