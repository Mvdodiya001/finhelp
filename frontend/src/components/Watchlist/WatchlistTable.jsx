import React from 'react';
import { getSignalClass } from '../../utils';

export function WatchlistTable({ results, setTradeConfig }) {
  return (
    <div className="table-container">
      <table className="data-table interactive">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Ticker</th>
            <th>Signal</th>
            <th>Score</th>
            <th>ML P(Up)</th>
            <th>Sentiment</th>
            <th>Model</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className="table-row">
              <td className="fw-bold text-muted">#{i + 1}</td>
              <td className="fw-bold font-mono">{r.ticker}</td>
              <td>
                <span className={`signal-badge ${getSignalClass(r.fusion.signal)}`}>
                  {r.fusion.signal}
                </span>
              </td>
              <td className="font-mono fw-bold">{r.fusion.final_score.toFixed(3)}</td>
              <td className="font-mono">{(r.quant.probability_up * 100).toFixed(1)}%</td>
              <td className="font-mono">{r.sentiment.score}/10</td>
              <td className="text-muted small-text">{r.quant.model_name}</td>
              <td>
                <button 
                  className="primary-btn"
                  style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
                  onClick={() => setTradeConfig({ 
                    ticker: r.ticker, 
                    currentPrice: r.historical_data && r.historical_data.length > 0 
                      ? r.historical_data[r.historical_data.length - 1].close 
                      : 0
                  })}
                >
                  Trade
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
