import React from 'react';
import { Clock } from 'lucide-react';

export function TransactionHistory({ transactions }) {
  return (
    <div className="card mt-4">
      <h2><Clock size={20} style={{ verticalAlign: 'middle', marginRight: 8 }} /> Transaction History</h2>
      {transactions.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No past transactions.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Ticker</th>
              <th>Shares</th>
              <th>Price</th>
              <th>Total Value</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, idx) => (
              <tr key={idx}>
                <td>{new Date(tx.timestamp).toLocaleString()}</td>
                <td>
                  <span className={`signal-badge ${tx.action === 'BUY' ? 'signal-buy' : 'signal-avoid'}`}>
                    {tx.action}
                  </span>
                </td>
                <td className="font-mono"><strong>{tx.ticker}</strong></td>
                <td>{tx.shares}</td>
                <td>${tx.price.toFixed(2)}</td>
                <td>${(tx.shares * tx.price).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
