import { fmtPrice } from '../api';

export default function AnalystFeed({ analysis }) {
  if (!analysis) return (
    <div className="card span-2" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 260, gap: '0.75rem' }}>
      <div style={{ fontFamily: 'var(--font-display)', color: 'var(--gold-dim)', fontSize: '0.7rem', letterSpacing: '0.2em' }}>NO ANALYSIS YET</div>
      <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', fontSize: '0.65rem' }}>Click ⚡ RUN ANALYSIS to begin</div>
    </div>
  );

  const { setup, technical, session, current_price, candles_used, source } = analysis;
  // ScalperTradeSetup has extra fields
  const isScalper = !!setup?.primary_timeframe;

  return (
    <div className="card span-2 fade-up" style={{ animationDelay: '0.1s' }}>
      <div className="card-header">
        <span className="card-title">⬡ Scalp Trade Setup</span>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {isScalper && (
            <span className="card-badge" style={{ color: '#00C8FF', borderColor: 'rgba(0,200,255,0.3)' }}>
              PRIMARY: {setup.primary_timeframe}
            </span>
          )}
          <span className="card-badge">{source} · {candles_used} CANDLES</span>
          <span className="card-badge">{session}</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>

        {/* Left: Bias + confidence */}
        <div>
          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.15em', marginBottom: '0.4rem' }}>BIAS</div>
            <div className={`bias-badge ${setup.bias}`}>{setup.bias}</div>
          </div>

          {/* MTF Alignment */}
          {isScalper && setup.timeframe_alignment && (
            <div style={{ background: 'rgba(0,200,255,0.05)', border: '1px solid rgba(0,200,255,0.15)', padding: '0.4rem 0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: 'var(--gold-dim)', letterSpacing: '0.1em', marginBottom: '0.2rem' }}>MTF ALIGNMENT</div>
              <div style={{ fontSize: '0.68rem', lineHeight: 1.4 }}>{setup.timeframe_alignment}</div>
            </div>
          )}

          <div style={{ marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.12em' }}>CONFIDENCE</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem', color: setup.confidence >= 70 ? 'var(--green)' : setup.confidence >= 50 ? 'var(--gold)' : 'var(--red)' }}>
                {setup.confidence}%
              </span>
            </div>
            <div className="confidence-bar-track">
              <div className="confidence-bar-fill" style={{ width: `${setup.confidence}%` }} />
            </div>
          </div>

          {/* Trend + Strength from technical */}
          {technical && (
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ flex: 1, background: 'var(--bg-panel)', padding: '0.5rem', border: '1px solid var(--border)' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>TREND (M5)</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', color: technical.trend === 'Bullish' ? 'var(--green)' : technical.trend === 'Bearish' ? 'var(--red)' : 'var(--gold)', marginTop: '0.2rem' }}>
                  {technical.trend}
                </div>
              </div>
              <div style={{ flex: 1, background: 'var(--bg-panel)', padding: '0.5rem', border: '1px solid var(--border)' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>STRENGTH</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.75rem', color: 'var(--gold)', marginTop: '0.2rem' }}>
                  {technical.strength}
                </div>
              </div>
            </div>
          )}

          {/* R:R */}
          <div style={{ background: 'var(--bg-panel)', padding: '0.5rem 0.75rem', border: '1px solid var(--border)', textAlign: 'center' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>RISK : REWARD</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', color: 'var(--gold-bright)', textShadow: '0 0 20px rgba(255,215,0,0.3)', lineHeight: 1 }}>
              1 : {setup.risk_reward?.toFixed(1)}
            </div>
          </div>
        </div>

        {/* Right: Levels */}
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.12em', marginBottom: '0.5rem' }}>SCALP LEVELS</div>

          {[
            { label: 'RESISTANCE 1', value: technical?.resistance_levels?.[2], color: 'var(--red)' },
            { label: 'TAKE PROFIT 2', value: setup.take_profit_2, color: 'var(--green)' },
            { label: 'TAKE PROFIT 1', value: setup.take_profit_1, color: 'var(--green)', opacity: 0.8 },
            { label: '── ENTRY ZONE ──', value: `${fmtPrice(setup.entry_low)} – ${fmtPrice(setup.entry_high)}`, color: 'var(--gold)', bold: true },
            { label: 'STOP LOSS', value: setup.stop_loss, color: 'var(--red)' },
            { label: 'SUPPORT 1', value: technical?.support_levels?.[0], color: 'var(--blue)', opacity: 0.7 },
          ].map((row, i) => (
            <div key={i} className="level-row" style={{ opacity: row.opacity || 1 }}>
              <span className="level-label">{row.label}</span>
              <span className="level-value" style={{ color: row.color, fontWeight: row.bold ? 700 : 400 }}>
                {typeof row.value === 'string' ? row.value : row.value ? `$${fmtPrice(row.value)}` : '—'}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="gold-line" />

      {/* Reasoning */}
      <div style={{ marginBottom: '0.75rem' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--gold-dim)', letterSpacing: '0.15em', marginBottom: '0.4rem' }}>REASONING</div>
        <div style={{ fontSize: '0.78rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>{setup.reasoning}</div>
      </div>

      {/* Invalidation */}
      <div style={{ background: 'var(--red-dim)', border: '1px solid rgba(255,69,96,0.2)', padding: '0.5rem 0.75rem' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--red)', letterSpacing: '0.1em' }}>⚠ INVALIDATION: </span>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-primary)' }}>{setup.invalidation}</span>
      </div>
    </div>
  );
}