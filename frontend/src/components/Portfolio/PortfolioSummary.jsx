import React from 'react';
import { DollarSign, PieChart, TrendingUp, TrendingDown } from 'lucide-react';

export function PortfolioSummary({ portfolioData, totalPnl, totalPortfolioValue }) {
  return (
    <div className="grid">
      <div className="card stat-card" style={{ background: 'var(--success-bg)' }}>
        <div className="stat-header">
          <h3 className="stat-label" style={{ color: 'var(--success)' }}>Cash Balance</h3>
          <DollarSign className="stat-icon" color="var(--success)" />
        </div>
        <div className="stat-value gradient-text">
          ${portfolioData.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>
      <div className="card stat-card" style={{ background: 'var(--primary-bg)' }}>
        <div className="stat-header">
          <h3 className="stat-label" style={{ color: 'var(--primary)' }}>Total Portfolio Value</h3>
          <PieChart className="stat-icon" color="var(--primary)" />
        </div>
        <div className="stat-value">
          ${totalPortfolioValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>
      <div className="card stat-card" style={{ background: totalPnl >= 0 ? 'var(--success-bg)' : 'rgba(239, 68, 68, 0.1)' }}>
        <div className="stat-header">
          <h3 className="stat-label" style={{ color: totalPnl >= 0 ? 'var(--success)' : 'var(--error)' }}>Unrealized P&L</h3>
          {totalPnl >= 0 
            ? <TrendingUp className="stat-icon" color="var(--success)" />
            : <TrendingDown className="stat-icon" color="var(--error)" />
          }
        </div>
        <div className="stat-value" style={{ color: totalPnl >= 0 ? 'var(--success)' : 'var(--error)' }}>
          {totalPnl >= 0 ? '+' : ''}${totalPnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>
    </div>
  );
}
