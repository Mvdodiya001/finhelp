import React from 'react';
import { Activity } from 'lucide-react';

export function BacktestForm({ ticker, setTicker, period, setPeriod, fetchBacktest, loading }) {
  return (
    <div className="card mb-4">
      <h2><Activity size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} /> Historical Backtest Simulation</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
        Simulate trading based on the AI Ensemble Strategy over historical data. Includes 0.1% transaction costs per trade.
      </p>
      <form className="search-box" style={{ background: 'var(--bg-card)' }} onSubmit={fetchBacktest}>
        <div className="input-wrapper">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="Ticker (e.g. TCS.NS)"
            required
          />
        </div>
        <select className="glass-select" value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="2y">2 Years</option>
          <option value="5y">5 Years</option>
        </select>
        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? <span>SIMULATING...</span> : "RUN BACKTEST"}
        </button>
      </form>
    </div>
  );
}
