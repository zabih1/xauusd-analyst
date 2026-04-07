import { useState, useRef } from 'react';
import { api } from '../api';

export default function ChartVision() {
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handleFile = async (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload an image file.');
      return;
    }
    setError(null);
    setResult(null);
    // preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
    // analyze
    setLoading(true);
    try {
      const data = await api.analyzeChart(file);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const suggestionColor = (s = '') => {
    if (s.startsWith('BUY')) return 'var(--green)';
    if (s.startsWith('SELL')) return 'var(--red)';
    return 'var(--gold)';
  };

  return (
    <div className="card fade-up" style={{ animationDelay: '0.4s' }}>
      <div className="card-header">
        <span className="card-title">◎ Chart Vision</span>
        <span className="card-badge">AI VISION</span>
      </div>

      {/* Upload zone */}
      {!result && (
        <div
          className={`upload-zone ${dragging ? 'dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          style={{ marginBottom: result ? '0.75rem' : 0 }}
        >
          <input ref={inputRef} type="file" accept="image/*"
            onChange={(e) => handleFile(e.target.files[0])} />

          {preview ? (
            <img src={preview} alt="chart" style={{ maxHeight: 120, maxWidth: '100%', objectFit: 'contain' }} />
          ) : (
            <>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem', opacity: 0.4 }}>📊</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.65rem', color: 'var(--gold-dim)', letterSpacing: '0.15em' }}>
                DROP CHART HERE
              </div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-dim)', marginTop: '0.3rem' }}>
                or click to browse · PNG / JPG
              </div>
            </>
          )}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem 0' }}>
          <span className="spinner" />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--gold)' }}>
            AI is analyzing your chart…
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--red)', padding: '0.5rem', background: 'var(--red-dim)', border: '1px solid rgba(255,69,96,0.2)' }}>
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div>
          {/* thumbnail + reset */}
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
            {preview && <img src={preview} alt="chart" style={{ width: 80, height: 50, objectFit: 'cover', border: '1px solid var(--border)', flexShrink: 0 }} />}
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', letterSpacing: '0.1em', marginBottom: '0.25rem' }}>SUGGESTION</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '0.9rem', color: suggestionColor(result.trade_suggestion), letterSpacing: '0.08em' }}>
                {result.trade_suggestion}
              </div>
            </div>
            <button className="btn" style={{ fontSize: '0.5rem', padding: '0.2rem 0.5rem' }}
              onClick={() => { setResult(null); setPreview(null); setError(null); }}>
              ↺ NEW
            </button>
          </div>

          {/* Confidence */}
          <div style={{ marginBottom: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.1em' }}>CONFIDENCE</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--gold)' }}>{result.confidence}%</span>
            </div>
            <div className="confidence-bar-track">
              <div className="confidence-bar-fill" style={{ width: `${result.confidence}%` }} />
            </div>
          </div>

          {/* Trend */}
          <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', padding: '0.4rem 0.6rem', marginBottom: '0.5rem' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.1em' }}>TREND: </span>
            <span style={{ fontSize: '0.72rem' }}>{result.trend_visible}</span>
          </div>

          {/* Patterns */}
          <div style={{ marginBottom: '0.5rem' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.12em', marginBottom: '0.25rem' }}>PATTERNS</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
              {result.patterns_found.map((p, i) => (
                <span key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6rem', padding: '0.15rem 0.4rem', border: '1px solid var(--gold-dim)', color: 'var(--gold)', background: 'var(--gold-glow)' }}>{p}</span>
              ))}
            </div>
          </div>

          {/* Key levels */}
          {result.key_levels.length > 0 && (
            <div style={{ marginBottom: '0.5rem' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.12em', marginBottom: '0.25rem' }}>KEY LEVELS</div>
              {result.key_levels.map((lvl, i) => (
                <div key={i} className="obs-item"><span className="obs-bullet">›</span><span style={{ fontSize: '0.72rem' }}>{lvl}</span></div>
              ))}
            </div>
          )}

          {/* Detailed analysis */}
          <div className="gold-line" />
          <div style={{ fontSize: '0.72rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>{result.detailed_analysis}</div>
        </div>
      )}
    </div>
  );
}
