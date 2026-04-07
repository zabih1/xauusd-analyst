// src/api.js — All backend API calls

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

export const api = {
  health:          ()           => apiFetch('/health'),
  getPrice:        ()           => apiFetch('/price'),
  setManualPrice:  (bid, ask)   => apiFetch('/price/manual', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bid, ask }),
  }),
  mt5Status:       ()           => apiFetch('/mt5/status'),
  getAnalysis:     ()           => apiFetch('/analysis'),
  runAnalysis:     ()           => apiFetch('/analysis/run', { method: 'POST' }),
  getNews:         ()           => apiFetch('/news'),
  calculateRisk:   (data)       => apiFetch('/risk/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  analyzeChart:    (file)       => {
    const form = new FormData();
    form.append('file', file);
    return apiFetch('/vision/analyze', { method: 'POST', body: form });
  },
};

export function timeSince(isoString) {
  if (!isoString) return '—';
  const diff = (Date.now() - new Date(isoString)) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export function fmtPrice(n) {
  if (!n && n !== 0) return '—';
  return Number(n).toFixed(2);
}
