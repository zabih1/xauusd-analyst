import { useState } from 'react';
import { api, fmtPrice } from '../api';

export default function RiskCalculator({ analysis }) {
  const setup = analysis?.setup;

  const [form, setForm] = useState({
    account_balance: '',
    risk_percent: '1',
    entry_price: setup ? ((setup.entry_low + setup.entry_high) / 2).toFixed(2) : '',
    stop_loss_price: setup?.stop_loss?.toFixed(2) || '',
    take_profit_price: setup?.take_profit_1?.toFixed(2) || '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  // auto-fill from analysis
  const autoFill = () => {
    if (!setup) return;
    setForm(f => ({
      ...f,
      entry_price: ((setup.entry_low + setup.entry_high) / 2).toFixed(2),
      stop_loss_price: setup.stop_loss.toFixed(2),
      take_profit_price: setup.take_profit_1.toFixed(2),
    }));
    setResult(null);
  };

  const calculate = async () => {
    setError(null);
    setLoading(true);
    try {
      const payload = {
        account_balance: parseFloat(form.account_balance),
        risk_percent: parseFloat(form.risk_percent),
        entry_price: parseFloat(form.entry_price),
        stop_loss_price: parseFloat(form.stop_loss_price),
        take_profit_price: parseFloat(form.take_profit_price),
      };
      if (Object.values(payload).some(isNaN)) throw new Error('Fill all fields with valid numbers.');
      const data = await api.calculateRisk(payload);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-up" style={{ animationDelay: '0.5s' }}>
      <div className="card-header">
        <span className="card-title">⊛ Risk Calculator</span>
        {setup && (
          <button className="btn" style={{ fontSize: '0.5rem', padding: '0.2rem 0.5rem' }} onClick={autoFill}>
            ↙ AUTO-FILL
          </button>
        )}
      </div>

      {/* Inputs */}
      <div className="risk-input-row">
        <div className="input-group">
          <label className="input-label">Account ($)</label>
          <input className="gold-input" type="number" placeholder="10000" value={form.account_balance} onChange={set('account_balance')} />
        </div>
        <div className="input-group">
          <label className="input-label">Risk %</label>
          <input className="gold-input" type="number" placeholder="1" step="0.1" value={form.risk_percent} onChange={set('risk_percent')} />
        </div>
      </div>
      <div className="risk-input-row">
        <div className="input-group">
          <label className="input-label">Entry Price</label>
          <input className="gold-input" type="number" placeholder="3285.00" step="0.01" value={form.entry_price} onChange={set('entry_price')} />
        </div>
        <div className="input-group">
          <label className="input-label">Stop Loss</label>
          <input className="gold-input" type="number" placeholder="3275.00" step="0.01" value={form.stop_loss_price} onChange={set('stop_loss_price')} />
        </div>
      </div>
      <div className="input-group" style={{ marginBottom: '0.75rem' }}>
        <label className="input-label">Take Profit</label>
        <input className="gold-input" type="number" placeholder="3305.00" step="0.01" value={form.take_profit_price} onChange={set('take_profit_price')} />
      </div>

      {error && <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.62rem', color: 'var(--red)', marginBottom: '0.5rem' }}>{error}</div>}

      <button className="btn btn-primary" style={{ width: '100%', marginBottom: '0.75rem' }} onClick={calculate} disabled={loading}>
        {loading ? 'Calculating…' : 'CALCULATE RISK'}
      </button>

      {/* Results */}
      {result && (
        <div style={{ animation: 'fadeUp 0.3s ease both' }}>
          <div className="gold-line" />

          {/* Hero: lot size */}
          <div style={{ textAlign: 'center', padding: '0.5rem 0', marginBottom: '0.5rem' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.15em' }}>LOT SIZE</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', color: 'var(--gold-bright)', textShadow: '0 0 20px rgba(255,215,0,0.3)', lineHeight: 1 }}>
              {result.lot_size}
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)' }}>LOTS</div>
          </div>

          {/* Stats grid */}
          {[
            { label: 'RISK AMOUNT',   value: `$${result.risk_amount_usd.toFixed(2)}`,     color: 'var(--red)' },
            { label: 'POTENTIAL P&L', value: `$${result.potential_profit_usd.toFixed(2)}`, color: 'var(--green)' },
            { label: 'SL PIPS',       value: result.sl_pips.toFixed(0),                    color: 'var(--text-primary)' },
            { label: 'TP PIPS',       value: result.tp_pips.toFixed(0),                    color: 'var(--text-primary)' },
            { label: 'R : R',         value: `1 : ${result.risk_reward.toFixed(2)}`,       color: 'var(--gold)' },
            { label: 'MARGIN REQ',    value: `$${result.margin_required.toFixed(0)}`,       color: 'var(--text-muted)' },
          ].map((row, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.3rem 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>{row.label}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: row.color, fontWeight: 500 }}>{row.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
