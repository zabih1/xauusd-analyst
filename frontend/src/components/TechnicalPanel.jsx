import { fmtPrice } from '../api';

export default function TechnicalPanel({ analysis }) {
  if (!analysis) return (
    <div className="card" style={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', fontSize: '0.65rem' }}>Awaiting analysis…</span>
    </div>
  );

  const { technical } = analysis;

  return (
    <div className="card fade-up" style={{ animationDelay: '0.2s' }}>
      <div className="card-header">
        <span className="card-title">◈ Technical</span>
        <span className="card-badge">{technical.trend} · {technical.strength}</span>
      </div>

      {/* Support / Resistance */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--red)', letterSpacing: '0.15em', marginBottom: '0.35rem' }}>RESISTANCE</div>
          {[...technical.resistance_levels].reverse().map((lvl, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', borderBottom: '1px solid var(--border)', opacity: 1 - i * 0.2 }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)' }}>R{i + 1}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--red)' }}>${fmtPrice(lvl)}</span>
            </div>
          ))}
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--blue)', letterSpacing: '0.15em', marginBottom: '0.35rem' }}>SUPPORT</div>
          {technical.support_levels.map((lvl, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', borderBottom: '1px solid var(--border)', opacity: 1 - i * 0.2 }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)' }}>S{i + 1}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--blue)' }}>${fmtPrice(lvl)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="gold-line" />

      {/* Momentum */}
      <div style={{ marginBottom: '0.75rem' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.15em', marginBottom: '0.3rem' }}>MOMENTUM</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>{technical.momentum}</div>
      </div>

      {/* Key observations */}
      <div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.15em', marginBottom: '0.3rem' }}>OBSERVATIONS</div>
        {technical.key_observations.map((obs, i) => (
          <div key={i} className="obs-item">
            <span className="obs-bullet">›</span>
            <span>{obs}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
