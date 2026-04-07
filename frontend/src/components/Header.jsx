import { useState, useEffect } from 'react';
import { api, fmtPrice, timeSince } from '../api';

export default function Header({ onRunAnalysis, analysisTime, loading }) {
  const [tick, setTick]       = useState(null);
  const [health, setHealth]   = useState(null);
  const [prevPrice, setPrev]  = useState(null);
  const [priceDir, setDir]    = useState(null); // 'up' | 'down'
  const [now, setNow]         = useState(new Date());

  // live price polling every 2s
  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const t = await api.getPrice();
        setTick(prev => {
          if (prev) {
            const mid = (t.bid + t.ask) / 2;
            const prevMid = (prev.bid + prev.ask) / 2;
            setDir(mid > prevMid ? 'up' : mid < prevMid ? 'down' : null);
          }
          return t;
        });
      } catch {}
    };
    fetchPrice();
    const id = setInterval(fetchPrice, 2000);
    return () => clearInterval(id);
  }, []);

  // health check every 30s
  useEffect(() => {
    const fetchHealth = async () => {
      try { setHealth(await api.health()); } catch {}
    };
    fetchHealth();
    const id = setInterval(fetchHealth, 30000);
    return () => clearInterval(id);
  }, []);

  // clock
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const mid = tick ? ((tick.bid + tick.ask) / 2).toFixed(2) : '——.——';
  const mt5Connected = health?.mt5?.connected;
  const session = health?.session || '—';

  return (
    <header style={{
      background: 'linear-gradient(180deg, #080805 0%, var(--bg-card) 100%)',
      borderBottom: '1px solid var(--border)',
      padding: '0 1.5rem',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>

      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border)' }}>

        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 28, height: 28,
            background: 'linear-gradient(135deg, var(--gold), var(--gold-dim))',
            clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
            flexShrink: 0,
          }} />
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.15em', color: 'var(--gold)' }}>
              AURUM ANALYST
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.2em' }}>
              XAUUSD · AI POWERED
            </div>
          </div>
        </div>

        {/* Center: live price */}
        <div style={{ display: 'flex', align: 'center', gap: '1.5rem', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '2rem',
              fontWeight: 400,
              color: priceDir === 'up' ? 'var(--green)' : priceDir === 'down' ? 'var(--red)' : 'var(--gold-bright)',
              textShadow: priceDir === 'up' ? '0 0 20px var(--green)' : priceDir === 'down' ? '0 0 20px var(--red)' : '0 0 20px rgba(255,215,0,0.3)',
              transition: 'color 0.3s, text-shadow 0.3s',
              lineHeight: 1,
            }}>
              {mid}
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.15em', marginTop: '0.1rem' }}>
              XAU / USD &nbsp;|&nbsp; {tick ? `B: ${fmtPrice(tick.bid)}  A: ${fmtPrice(tick.ask)}  SPR: ${tick.spread}` : 'NO PRICE DATA'}
            </div>
          </div>
        </div>

        {/* Right: status + clock */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>

          {/* session */}
          <div style={{ textAlign: 'right' }}>
            <div className="session-badge">{session}</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', marginTop: '0.3rem', letterSpacing: '0.1em' }}>
              {now.toUTCString().slice(17, 25)} UTC
            </div>
          </div>

          {/* MT5 status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className={`status-dot ${mt5Connected ? 'live' : tick?.source === 'manual' ? 'manual' : 'offline'}`} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>
              {mt5Connected ? 'MT5 LIVE' : tick?.source === 'manual' ? 'MANUAL' : 'OFFLINE'}
            </span>
          </div>

          {/* run analysis button */}
          <button className={`btn btn-primary`} onClick={onRunAnalysis} disabled={loading}>
            {loading ? <><span className="spinner" style={{width:10,height:10,marginRight:6}} />ANALYSING…</> : '⚡ RUN ANALYSIS'}
          </button>
        </div>
      </div>

      {/* Sub bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '0.35rem 0', fontSize: '0.6rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>
        <span>LAST ANALYSIS: <span style={{ color: 'var(--gold)' }}>{analysisTime ? timeSince(analysisTime) : 'NEVER'}</span></span>
        <span style={{ color: 'var(--border)' }}>|</span>
        <span>AUTO-REFRESH: <span style={{ color: 'var(--gold)' }}>5 MIN</span></span>
        <span style={{ color: 'var(--border)' }}>|</span>
        <span>ENGINE: <span style={{ color: 'var(--gold)' }}>MULTI-AGENT AI</span></span>
        <span style={{ color: 'var(--border)' }}>|</span>
        <span>PIPELINE: <span style={{ color: 'var(--gold)' }}>OPENROUTER</span></span>
      </div>
    </header>
  );
}
