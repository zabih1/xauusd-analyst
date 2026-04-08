import { fmtPrice } from '../api';

// Timeframe metadata
const TF_META = {
    M1: { label: '1 MIN', role: 'Entry Timing', color: '#FF8C42', weight: '15%' },
    M5: { label: '5 MIN', role: 'Primary Signal ★', color: '#00C8FF', weight: '35%' },
    M15: { label: '15 MIN', role: 'Trend Context', color: '#A78BFA', weight: '30%' },
    H1: { label: '1 HOUR', role: 'HTF Bias Filter', color: '#00C896', weight: '20%' },
};

const ORDER = ['H1', 'M15', 'M5', 'M1'];

function SignalBadge({ signal }) {
    const colors = {
        BUY: { bg: 'rgba(0,200,150,0.12)', border: 'rgba(0,200,150,0.4)', text: '#00C896' },
        SELL: { bg: 'rgba(255,69,96,0.12)', border: 'rgba(255,69,96,0.4)', text: '#FF4560' },
        WAIT: { bg: 'rgba(74,158,255,0.12)', border: 'rgba(74,158,255,0.4)', text: '#4A9EFF' },
    };
    const c = colors[signal] || colors.WAIT;
    return (
        <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.1em',
            padding: '0.2rem 0.6rem',
            background: c.bg,
            border: `1px solid ${c.border}`,
            color: c.text,
        }}>
            {signal}
        </span>
    );
}

function QualityBar({ value, color }) {
    const barColor = value >= 70 ? '#00C896' : value >= 50 ? '#00C8FF' : '#FF4560';
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <div style={{ flex: 1, height: 3, background: 'var(--bg-panel)', border: '1px solid var(--border)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${value}%`, background: barColor, transition: 'width 1s ease' }} />
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: barColor, minWidth: 28, textAlign: 'right' }}>{value}</span>
        </div>
    );
}

function TimeframeCard({ tf, data }) {
    const meta = TF_META[tf];
    const isM5 = tf === 'M5'; // primary TF — highlight

    if (!data) {
        return (
            <div style={{
                background: isM5 ? 'rgba(0,200,255,0.04)' : 'var(--bg-panel)',
                border: `1px solid ${isM5 ? 'rgba(0,200,255,0.2)' : 'var(--border)'}`,
                padding: '0.75rem',
                opacity: 0.5,
            }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)' }}>
                    [{tf}] No data
                </div>
            </div>
        );
    }

    const trendColor = data.trend === 'Bullish' ? '#00C896'
        : data.trend === 'Bearish' ? '#FF4560'
            : '#00C8FF';

    return (
        <div style={{
            background: isM5 ? 'rgba(0,200,255,0.05)' : 'var(--bg-panel)',
            border: `1px solid ${isM5 ? 'rgba(0,200,255,0.3)' : 'var(--border)'}`,
            padding: '0.75rem',
            position: 'relative',
            overflow: 'hidden',
        }}>
            {/* M5 star glow */}
            {isM5 && (
                <div style={{
                    position: 'absolute', top: 0, right: 0,
                    width: 80, height: 80,
                    background: 'radial-gradient(circle, rgba(0,200,255,0.08), transparent)',
                    pointerEvents: 'none',
                }} />
            )}

            {/* Header row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: meta.color,
                        letterSpacing: '0.1em',
                    }}>
                        {meta.label}
                    </span>
                    <span style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.5rem',
                        color: 'var(--text-muted)',
                        letterSpacing: '0.08em',
                    }}>
                        {meta.role}
                    </span>
                </div>
                <SignalBadge signal={data.scalp_signal} />
            </div>

            {/* Quality bar */}
            <div style={{ marginBottom: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>SIGNAL QUALITY</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: 'var(--text-muted)' }}>WEIGHT: {meta.weight}</span>
                </div>
                <QualityBar value={data.signal_quality} />
            </div>

            {/* Trend + Strength */}
            <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.5rem' }}>
                <div style={{ flex: 1, padding: '0.3rem 0.4rem', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.45rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>TREND</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.65rem', color: trendColor, marginTop: '0.1rem' }}>{data.trend}</div>
                </div>
                <div style={{ flex: 1, padding: '0.3rem 0.4rem', background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.45rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>STRENGTH</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.65rem', color: 'var(--gold)', marginTop: '0.1rem' }}>{data.strength}</div>
                </div>
            </div>

            {/* Momentum */}
            <div style={{ fontSize: '0.68rem', color: 'var(--text-primary)', lineHeight: 1.4, marginBottom: '0.5rem' }}>
                {data.momentum}
            </div>

            {/* S/R compact */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem', marginBottom: '0.5rem' }}>
                <div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.45rem', color: '#FF4560', letterSpacing: '0.1em', marginBottom: '0.2rem' }}>RESISTANCE</div>
                    {[...data.resistance_levels].reverse().slice(0, 2).map((lvl, i) => (
                        <div key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.62rem', color: '#FF4560', opacity: i === 0 ? 1 : 0.6 }}>
                            ${fmtPrice(lvl)}
                        </div>
                    ))}
                </div>
                <div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.45rem', color: '#4A9EFF', letterSpacing: '0.1em', marginBottom: '0.2rem' }}>SUPPORT</div>
                    {data.support_levels.slice(0, 2).map((lvl, i) => (
                        <div key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.62rem', color: '#4A9EFF', opacity: i === 0 ? 1 : 0.6 }}>
                            ${fmtPrice(lvl)}
                        </div>
                    ))}
                </div>
            </div>

            {/* Entry note */}
            {data.entry_note && (
                <div style={{
                    background: 'rgba(0,200,255,0.05)',
                    border: '1px solid rgba(0,200,255,0.15)',
                    padding: '0.35rem 0.5rem',
                    marginBottom: '0.4rem',
                }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: 'var(--gold-dim)', letterSpacing: '0.08em' }}>ENTRY TRIGGER: </span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-primary)' }}>{data.entry_note}</span>
                </div>
            )}

            {/* Warning */}
            {data.warning && data.warning !== 'None' && (
                <div style={{
                    background: 'rgba(255,69,96,0.06)',
                    border: '1px solid rgba(255,69,96,0.2)',
                    padding: '0.3rem 0.5rem',
                }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: '#FF4560', letterSpacing: '0.08em' }}>⚠ </span>
                    <span style={{ fontSize: '0.63rem', color: 'var(--text-primary)' }}>{data.warning}</span>
                </div>
            )}
        </div>
    );
}


// ── Alignment Summary Bar ─────────────────────────────────────
function AlignmentBar({ tfAnalyses }) {
    if (!tfAnalyses) return null;

    const signals = ORDER.map(tf => ({
        tf,
        signal: tfAnalyses[tf]?.scalp_signal || 'WAIT',
        quality: tfAnalyses[tf]?.signal_quality || 0,
    }));

    const buyCount = signals.filter(s => s.signal === 'BUY').length;
    const sellCount = signals.filter(s => s.signal === 'SELL').length;

    let alignColor = '#4A9EFF';
    let alignText = 'MIXED';
    if (buyCount >= 3) { alignColor = '#00C896'; alignText = 'BUY ALIGNED'; }
    if (sellCount >= 3) { alignColor = '#FF4560'; alignText = 'SELL ALIGNED'; }
    if (buyCount >= 2 && sellCount === 0) { alignColor = '#00C896'; alignText = 'LEANING BUY'; }
    if (sellCount >= 2 && buyCount === 0) { alignColor = '#FF4560'; alignText = 'LEANING SELL'; }

    return (
        <div style={{
            background: 'var(--bg-panel)',
            border: '1px solid var(--border)',
            padding: '0.6rem 0.75rem',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
        }}>
            <div style={{ display: 'flex', gap: '1.5rem' }}>
                {signals.map(({ tf, signal, quality }) => {
                    const meta = TF_META[tf];
                    const sigColor = signal === 'BUY' ? '#00C896' : signal === 'SELL' ? '#FF4560' : '#4A9EFF';
                    return (
                        <div key={tf} style={{ textAlign: 'center' }}>
                            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: meta.color, letterSpacing: '0.1em', marginBottom: '0.2rem' }}>{tf}</div>
                            <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.7rem', color: sigColor, fontWeight: 700 }}>{signal}</div>
                            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.45rem', color: 'var(--text-muted)' }}>Q:{quality}</div>
                        </div>
                    );
                })}
            </div>
            <div style={{ textAlign: 'right' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', color: 'var(--text-muted)', letterSpacing: '0.1em', marginBottom: '0.2rem' }}>MTF ALIGNMENT</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.85rem', color: alignColor, letterSpacing: '0.1em' }}>{alignText}</div>
            </div>
        </div>
    );
}


// ── Main export ───────────────────────────────────────────────
export default function MTFPanel({ analysis }) {
    const tfAnalyses = analysis?.timeframe_analyses;

    return (
        <div className="card span-3 fade-up" style={{ animationDelay: '0.25s' }}>
            <div className="card-header">
                <span className="card-title">◈ Multi-Timeframe Scalper Analysis</span>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className="card-badge">M1 · M5 · M15 · H1</span>
                    <span className="card-badge" style={{ color: '#00C8FF', borderColor: 'rgba(0,200,255,0.3)' }}>4 AGENTS PARALLEL</span>
                </div>
            </div>

            {!tfAnalyses ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 120, gap: '0.75rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', fontSize: '0.65rem' }}>
                        Run analysis to see per-timeframe breakdown
                    </span>
                </div>
            ) : (
                <>
                    <AlignmentBar tfAnalyses={tfAnalyses} />

                    {/* 4-column grid: H1 M15 M5 M1 */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
                        {ORDER.map(tf => (
                            <TimeframeCard key={tf} tf={tf} data={tfAnalyses[tf]} />
                        ))}
                    </div>

                    {/* Scalp execution note */}
                    {analysis?.setup?.scalp_notes && (
                        <>
                            <div className="gold-line" />
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                <div style={{ background: 'rgba(0,200,255,0.05)', border: '1px solid rgba(0,200,255,0.15)', padding: '0.6rem 0.75rem' }}>
                                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.12em', marginBottom: '0.3rem' }}>⚡ SCALP EXECUTION NOTES</div>
                                    <div style={{ fontSize: '0.72rem', lineHeight: 1.5, color: 'var(--text-primary)' }}>{analysis.setup.scalp_notes}</div>
                                </div>
                                <div style={{ background: 'rgba(255,69,96,0.05)', border: '1px solid rgba(255,69,96,0.15)', padding: '0.6rem 0.75rem' }}>
                                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: '#FF4560', letterSpacing: '0.12em', marginBottom: '0.3rem' }}>🚫 DO NOT TRADE IF</div>
                                    <div style={{ fontSize: '0.72rem', lineHeight: 1.5, color: 'var(--text-primary)' }}>{analysis.setup.do_not_trade_if}</div>
                                </div>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}