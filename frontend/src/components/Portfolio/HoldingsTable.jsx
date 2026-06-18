import React from 'react';
import { Briefcase } from 'lucide-react';

export function HoldingsTable({ portfolioData, setTradeConfig }) {
  return (
    <div className="card mt-4">
      <h2><Briefcase size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} /> Current Holdings</h2>
      {Object.keys(portfolioData.holdings).length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No open positions. Analyze a ticker and use the TRADE button to start.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Shares</th>
              <th>Current Price</th>
              <th>Market Value</th>
              <th>Unrealized P&L</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(portfolioData.holdings).map(([ticker, shares]) => {
              const currentPrice = portfolioData.current_prices?.[ticker];
              const pnl = portfolioData.unrealized_pnl?.[ticker];
              const marketValue = currentPrice ? currentPrice * shares : null;
              return (
                <tr key={ticker}>
                  <td className="font-mono"><strong>{ticker}</strong></td>
                  <td>{shares}</td>
                  <td>{currentPrice ? `$${currentPrice.toFixed(2)}` : <span style={{color: 'var(--text-muted)'}}>—</span>}</td>
                  <td>{marketValue ? `$${marketValue.toFixed(2)}` : <span style={{color: 'var(--text-muted)'}}>—</span>}</td>
                  <td style={{ color: pnl != null ? (pnl >= 0 ? 'var(--success)' : 'var(--error)') : '' }}>
                    {pnl != null ? `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}` : <span style={{color: 'var(--text-muted)'}}>—</span>}
                  </td>
                  <td>
                    <button 
                      className="primary-btn"
                      style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
                      onClick={() => setTradeConfig({ ticker, currentPrice: currentPrice || 0 })}
                    >
                      Trade
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
