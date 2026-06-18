import React from 'react';
import { Activity } from 'lucide-react';

export function ChartsForm({ ticker, setTicker, period, setPeriod, fetchChart, loading }) {
  return (
    <div className="card mb-4">
      <h2><Activity size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} /> Advanced Interactive Charts</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
        View detailed price action and volume history using classic Candlestick visualization.
      </p>
      
      <form className="search-box" style={{ background: 'var(--bg-card)' }} onSubmit={(e) => fetchChart(e)}>
        <div className="input-wrapper">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="Ticker (e.g. AAPL)"
            required
          />
        </div>
        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? <span>LOADING...</span> : "LOAD CHART"}
        </button>
      </form>

      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        {['1d', '5d', '1mo', '3mo', '6mo', '1y'].map((p) => (
          <button 
            key={p} 
            type="button" 
            className={`toggle-btn ${period === p ? 'active' : ''}`}
            onClick={(e) => { setPeriod(p); fetchChart(e, p); }}
            disabled={loading}
            style={{ padding: '0.3rem 0.8rem', fontSize: '0.85rem' }}
          >
            {p.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
