import React from 'react';
import { BacktestForm } from './BacktestForm';
import { MetricsCards } from './MetricsCards';
import { BacktestEquityCurve } from './BacktestEquityCurve';
import { TradeLog } from './TradeLog';

export function Backtest({ ticker, setTicker, period, setPeriod, fetchBacktest, data, loading, error }) {
  return (
    <div className="fade-in">
      <BacktestForm 
        ticker={ticker} 
        setTicker={setTicker} 
        period={period} 
        setPeriod={setPeriod} 
        fetchBacktest={fetchBacktest} 
        loading={loading} 
      />

      {error && (
        <div className="card error-banner mb-4">
          <div className="error-icon">⚠️</div>
          <div>
            <h3 className="error-title">Simulation Error</h3>
            <p className="error-message">{error}</p>
          </div>
        </div>
      )}

      {loading && <div className="skeleton skeleton-hero mb-4"></div>}

      {!loading && data && (
        <div className="fade-in">
          <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Strategy: <span className="gradient-text">{data.strategy_used || 'Ensemble Strategy'}</span></h3>
          </div>
          
          <MetricsCards data={data} />
          
          <BacktestEquityCurve data={data} ticker={ticker} period={period} />
          
          <TradeLog trades={data.trades} />
        </div>
      )}
    </div>
  );
}
