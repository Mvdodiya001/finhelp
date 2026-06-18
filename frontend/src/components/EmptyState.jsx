import React from 'react';
import { Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function EmptyState({ setTicker, isWatchlist }) {
  const navigate = useNavigate();
  const popularStocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 
    'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS'
  ];

  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <Activity size={48} />
      </div>
      <h2>Awaiting execution</h2>
      <p className="text-muted">Enter a ticker and click Execute to begin analysis.</p>

      <div className="popular-stocks-container">
        <p className="section-subtitle">Popular Indian Stocks (NSE)</p>
        <div className="pill-group">
          {popularStocks.map(t => (
            <button
              key={t}
              type="button"
              className="pill-btn"
              onClick={() => { 
                setTicker(t); 
                if (isWatchlist) navigate('/analyze');
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <p className="disclaimer text-muted">
          * The engine supports 10,000+ global tickers via Yahoo Finance. Use the Watchlist mode for multi-ticker comparison.
        </p>
      </div>
    </div>
  );
}
