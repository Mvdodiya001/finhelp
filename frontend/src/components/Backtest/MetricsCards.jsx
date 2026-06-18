import React from 'react';
import { TrendingUp, TrendingDown, Percent, Activity, BarChart3, Target } from 'lucide-react';

export function MetricsCards({ data }) {
  return (
    <>
      {/* Row 1: Core metrics */}
      <div className="grid mb-4">
        <div className="card stat-card" style={{ background: 'var(--success-bg)' }}>
          <div className="stat-header">
            <h3 className="stat-label" style={{ color: 'var(--success)' }}>AI Strategy ROI</h3>
            <TrendingUp className="stat-icon" color="var(--success)" />
          </div>
          <div className="stat-value gradient-text">{(data.roi * 100).toFixed(2)}%</div>
        </div>
        <div className="card stat-card" style={{ background: 'var(--primary-bg)' }}>
          <div className="stat-header">
            <h3 className="stat-label" style={{ color: 'var(--primary)' }}>Buy & Hold ROI</h3>
            <Percent className="stat-icon" color="var(--primary)" />
          </div>
          <div className="stat-value">{(data.buy_hold_roi * 100).toFixed(2)}%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-header">
            <h3 className="stat-label">Sharpe Ratio</h3>
            <Activity className="stat-icon" color="var(--text-muted)" />
          </div>
          <div className="stat-value">{data.sharpe_ratio.toFixed(2)}</div>
        </div>
        <div className="card stat-card" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
          <div className="stat-header">
            <h3 className="stat-label" style={{ color: 'var(--error)' }}>Max Drawdown</h3>
            <TrendingDown className="stat-icon" color="var(--error)" />
          </div>
          <div className="stat-value">{(data.max_drawdown * 100).toFixed(2)}%</div>
        </div>
      </div>

      {/* Row 2: Trade-level statistics */}
      <div className="grid mb-4">
        <div className="card stat-card">
          <div className="stat-header">
            <h3 className="stat-label">Total Trades</h3>
            <BarChart3 className="stat-icon" color="var(--text-muted)" />
          </div>
          <div className="stat-value">{data.total_trades}</div>
        </div>
        <div className="card stat-card" style={{ background: 'var(--success-bg)' }}>
          <div className="stat-header">
            <h3 className="stat-label" style={{ color: 'var(--success)' }}>Win Rate</h3>
            <Target className="stat-icon" color="var(--success)" />
          </div>
          <div className="stat-value">{(data.win_rate * 100).toFixed(1)}%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-header">
            <h3 className="stat-label">Profit Factor</h3>
            <TrendingUp className="stat-icon" color="var(--text-muted)" />
          </div>
          <div className="stat-value">{data.profit_factor.toFixed(2)}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-header">
            <h3 className="stat-label">Avg Win / Loss</h3>
            <Activity className="stat-icon" color="var(--text-muted)" />
          </div>
          <div className="stat-value" style={{ fontSize: '1rem' }}>
            <span style={{ color: 'var(--success)' }}>+{(data.avg_win * 100).toFixed(2)}%</span>
            {' / '}
            <span style={{ color: 'var(--error)' }}>-{(data.avg_loss * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>
    </>
  );
}
