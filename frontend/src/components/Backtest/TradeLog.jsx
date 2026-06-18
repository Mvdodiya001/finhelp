import React from 'react';

export function TradeLog({ trades }) {
  if (!trades || trades.length === 0) return null;

  return (
    <div className="card mt-4">
      <h3 className="card-header">Trade Log</h3>
      <div className="table-container" style={{maxHeight: '400px', overflowY: 'auto'}}>
        <table className="data-table">
          <thead style={{position: 'sticky', top: 0, background: 'var(--bg-card)'}}>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Price</th>
              <th className="text-right">Profit / Return</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, i) => (
              <tr key={i}>
                <td>{trade.date}</td>
                <td className={trade.action.includes('BUY') ? 'text-buy' : 'text-avoid'}>{trade.action}</td>
                <td>${trade.price.toFixed(2)}</td>
                <td className="text-right" style={{color: trade.profit > 0 ? 'var(--success)' : trade.profit < 0 ? 'var(--error)' : 'var(--text-muted)'}}>
                  {trade.profit !== 0 ? `${trade.profit > 0 ? '+' : ''}${(trade.profit * 100).toFixed(2)}%` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
