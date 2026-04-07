import { useState, useEffect } from 'react';
import { api, timeSince } from '../api';

export default function NewsSentiment({ analysis }) {
  const [news, setNews]       = useState([]);
  const [loading, setLoading] = useState(false);
  const [score, setScore]     = useState(null);

  const fetchNews = async () => {
    setLoading(true);
    try {
      const data = await api.getNews();
      setNews(data.items || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNews(); }, []);

  // Use score from analysis if available
  useEffect(() => {
    if (analysis?.fundamental) {
      setScore(analysis.fundamental.sentiment_score);
      setNews(prev => {
        const analysisNews = analysis.news_items || [];
        return analysisNews.length > 0 ? analysisNews : prev;
      });
    }
  }, [analysis]);

  const overall = analysis?.fundamental?.overall_sentiment || 'NEUTRAL';
  const dxy     = analysis?.fundamental?.dxy_outlook;
  const factors = analysis?.fundamental?.macro_factors || [];

  const scoreColor = (s) => {
    if (s === null || s === undefined) return 'var(--text-muted)';
    if (s > 0.3) return 'var(--green)';
    if (s < -0.3) return 'var(--red)';
    return 'var(--gold)';
  };

  const macroTag = (f) => {
    if (f.startsWith('BULLISH')) return <span className="tag bull">BULL</span>;
    if (f.startsWith('BEARISH')) return <span className="tag bear">BEAR</span>;
    return <span className="tag neut">NEUT</span>;
  };

  return (
    <div className="card fade-up" style={{ animationDelay: '0.3s' }}>
      <div className="card-header">
        <span className="card-title">◉ Sentiment</span>
        <button className="btn" style={{ fontSize: '0.5rem', padding: '0.2rem 0.5rem' }} onClick={fetchNews} disabled={loading}>
          {loading ? '…' : '↻ REFRESH'}
        </button>
      </div>

      {/* Overall sentiment score */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.12em' }}>OVERALL</div>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1rem',
            fontWeight: 700,
            letterSpacing: '0.1em',
            color: overall === 'BULLISH' ? 'var(--green)' : overall === 'BEARISH' ? 'var(--red)' : 'var(--gold)',
            marginTop: '0.1rem',
          }}>
            {overall}
          </div>
        </div>
        {score !== null && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--text-muted)', letterSpacing: '0.12em' }}>SCORE</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.3rem', color: scoreColor(score), marginTop: '0.1rem' }}>
              {score > 0 ? '+' : ''}{score?.toFixed(2)}
            </div>
          </div>
        )}
      </div>

      {/* Score bar */}
      {score !== null && (
        <div style={{ position: 'relative', height: 6, background: 'var(--bg-panel)', border: '1px solid var(--border)', marginBottom: '0.75rem' }}>
          <div style={{
            position: 'absolute',
            top: 0, bottom: 0,
            left: '50%',
            width: `${Math.abs(score) * 50}%`,
            transform: score < 0 ? 'translateX(-100%)' : 'none',
            background: score > 0 ? 'var(--green)' : 'var(--red)',
            opacity: 0.7,
            transition: 'width 1s ease',
          }} />
          <div style={{ position: 'absolute', top: -2, bottom: -2, left: '50%', width: 1, background: 'var(--border)' }} />
        </div>
      )}

      {/* DXY outlook */}
      {dxy && (
        <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', padding: '0.5rem 0.6rem', marginBottom: '0.75rem' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.12em', marginBottom: '0.25rem' }}>DXY OUTLOOK</div>
          <div style={{ fontSize: '0.72rem', lineHeight: 1.4 }}>{dxy}</div>
        </div>
      )}

      {/* Macro factors */}
      {factors.length > 0 && (
        <div style={{ marginBottom: '0.75rem' }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.12em', marginBottom: '0.35rem' }}>MACRO FACTORS</div>
          {factors.map((f, i) => (
            <div key={i} className="macro-factor">
              {macroTag(f)}
              <span style={{ fontSize: '0.72rem' }}>{f.replace(/^(BULLISH|BEARISH|NEUTRAL):\s*/i, '')}</span>
            </div>
          ))}
        </div>
      )}

      <div className="gold-line" />

      {/* News headlines */}
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.5rem', color: 'var(--gold-dim)', letterSpacing: '0.15em', marginBottom: '0.35rem' }}>
        HEADLINES ({news.length})
      </div>
      <div style={{ maxHeight: 220, overflowY: 'auto' }}>
        {news.length === 0 && (
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--text-dim)', padding: '0.5rem 0' }}>No news loaded.</div>
        )}
        {news.map((item, i) => (
          <div key={i} className="news-item" onClick={() => item.url && window.open(item.url, '_blank')}>
            <div className={`impact-dot ${item.impact || 'LOW'}`} />
            <div>
              <div className="news-title">{item.title}</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.52rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                {item.source}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.2rem' }}>
              <span className={`sentiment-tag ${item.sentiment || 'NEUTRAL'}`}>{item.sentiment || '—'}</span>
              <span className="news-meta">{timeSince(item.published_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
