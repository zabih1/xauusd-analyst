import { useState } from 'react';
import { api, fmtPrice } from '../api';

export default function ManualPrice({ onPriceSet }) {
  const [bid, setBid]     = useState('');
  const [ask, setAsk]     = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone]   = useState(false);
  const [error, setError] = useState(null);

  const submit = async () => {
    const b = parseFloat(bid), a = parseFloat(ask);
    if (isNaN(b) || isNaN(a) || b <= 0 || a <= 0) {
      setError('Enter valid bid and ask prices.');
      return;
    }
    if (a < b) { setError('Ask must be ≥ Bid.'); return; }
    setError(null);
    setLoading(true);
    try {
      const tick = await api.setManualPrice(b, a);
      setDone(true);
      if (onPriceSet) onPriceSet(tick);
      setTimeout(() => setDone(false), 3000);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-up" style={{ animationDelay: '0.6s' }}>
      <div className="card-header">
        <span className="card-title">⌨ Manual Price</span>
        <span className="card-badge">MT5 OFFLINE MODE</span>
      </div>

      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6rem', color: 'var(--text-muted)', marginBottom: '0.75rem', lineHeight: 1.5 }}>
        Enter current XAU/USD price manually when MT5 is not connected.
      </div>

      <div className="risk-input-row" style={{ marginBottom: '0.5rem' }}>
        <div className="input-group">
          <label className="input-label">BID Price</label>
          <input className="gold-input" type="number" placeholder="3285.40" step="0.01" value={bid} onChange={e => setBid(e.target.value)} />
        </div>
        <div className="input-group">
          <label className="input-label">ASK Price</label>
          <input className="gold-input" type="number" placeholder="3285.90" step="0.01" value={ask} onChange={e => setAsk(e.target.value)} />
        </div>
      </div>

      {bid && ask && !isNaN(parseFloat(bid)) && !isNaN(parseFloat(ask)) && (
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          MID: <span style={{ color: 'var(--gold)' }}>${((parseFloat(bid) + parseFloat(ask)) / 2).toFixed(2)}</span>
          &nbsp;·&nbsp;
          SPREAD: <span style={{ color: 'var(--gold)' }}>{((parseFloat(ask) - parseFloat(bid)) * 10).toFixed(1)}</span>
        </div>
      )}

      {error && <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.62rem', color: 'var(--red)', marginBottom: '0.5rem' }}>{error}</div>}

      <button className="btn btn-primary" style={{ width: '100%' }} onClick={submit} disabled={loading}>
        {loading ? 'Setting…' : done ? '✓ PRICE SET' : 'SET PRICE'}
      </button>

      {done && (
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6rem', color: 'var(--green)', marginTop: '0.5rem', textAlign: 'center' }}>
          Price updated — click ⚡ RUN ANALYSIS to analyze
        </div>
      )}
    </div>
  );
}
