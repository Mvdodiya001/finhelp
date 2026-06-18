import React from 'react';
import { ChartsForm } from './ChartsForm';
import { CandlestickChart } from './CandlestickChart';

export function Charts({ ticker, setTicker, period, setPeriod, fetchChart, data, loading, error }) {
  return (
    <div className="fade-in">
      <ChartsForm 
        ticker={ticker} 
        setTicker={setTicker} 
        period={period} 
        setPeriod={setPeriod} 
        fetchChart={fetchChart} 
        loading={loading} 
      />

      {error && (
        <div className="card error-banner mb-4">
          <div className="error-icon">⚠️</div>
          <div>
            <h3 className="error-title">Chart Error</h3>
            <p className="error-message">{error}</p>
          </div>
        </div>
      )}

      {loading && <div className="skeleton skeleton-hero mb-4" style={{ height: '500px' }}></div>}

      {!loading && data && (
        <CandlestickChart data={data} />
      )}
    </div>
  );
}
