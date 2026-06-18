import React, { useState } from 'react';
import { ShoppingCart } from 'lucide-react';
import { getSignalClass } from '../../utils';
import { TradeModal } from '../TradeModal';

export function TickerHero({ data, currentPrice, priceChange, priceChangePercent, holding, unrealizedPnl, pnlPercent, executeTrade }) {
  const [showTradeModal, setShowTradeModal] = useState(false);

  return (
    <section className="hero card mb-4">
      {showTradeModal && (
        <TradeModal 
          ticker={data.ticker} 
          currentPrice={currentPrice} 
          executeTrade={executeTrade} 
          onClose={() => setShowTradeModal(false)} 
        />
      )}
      <div className="hero-content" style={{position: 'relative'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', marginBottom: '1rem'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap'}}>
            <div className="ticker-badge" style={{margin: 0}}>{data.ticker}</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>${currentPrice.toFixed(2)}</span>
              {priceChange !== 0 && (
                <span style={{ fontSize: '1rem', fontWeight: '500', color: priceChange >= 0 ? 'var(--success)' : 'var(--error)' }}>
                  {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChange >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
                </span>
              )}
              {holding && (
                <div style={{marginLeft: '1rem', fontSize: '0.9rem', padding: '0.2rem 0.6rem', background: 'rgba(255,255,255,0.08)', borderRadius: '6px', display: 'flex', gap: '0.5rem', alignItems: 'center'}}>
                  <span className="text-muted">Pos:</span> {holding.shares} @ ${holding.avg_price.toFixed(2)}
                  <span style={{color: unrealizedPnl >= 0 ? 'var(--success)' : 'var(--error)', fontWeight: 'bold', marginLeft: '0.5rem'}}>
                    PNL: {unrealizedPnl >= 0 ? '+' : ''}${unrealizedPnl.toFixed(2)} ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                  </span>
                </div>
              )}
            </div>
          </div>
          <button className="primary-btn" style={{padding: '0.5rem 1rem'}} onClick={() => setShowTradeModal(true)}>
            <ShoppingCart size={16} style={{marginRight: 6, verticalAlign: 'middle'}} />
            TRADE
          </button>
        </div>
        <h2 className="signal-title">
          FINAL SIGNAL: <span className={getSignalClass(data.fusion.signal)}>
            {data.fusion.signal.toUpperCase()}
          </span>
        </h2>
        
        <div className="progress-container">
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill"
              style={{ width: `${Math.min(100, Math.max(0, data.fusion.final_score * 100))}%` }}
            ></div>
          </div>
          <div className="progress-labels">
            <span className="text-muted small-text">0.0 (Bearish)</span>
            <span className="metric-label fw-bold">Confidence Score: {data.fusion.final_score.toFixed(3)} / 1.000</span>
            <span className="text-muted small-text">1.0 (Bullish)</span>
          </div>
        </div>
        
        <div className="hero-footer text-muted small-text">
          <span>Model: <strong className="text-main">{data.quant.model_name}</strong></span>
          <span className="divider">•</span>
          <span>News Provider: <strong className="text-main">{data.sentiment.provider_used}</strong></span>
        </div>
      </div>
    </section>
  );
}
