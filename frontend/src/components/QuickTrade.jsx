import React, { useState } from 'react';
import { Search, Zap } from 'lucide-react';
import { apiClient } from '../utils/api';

export function QuickTrade({ executeTrade }) {
  const [ticker, setTicker] = useState('');
  const [price, setPrice] = useState(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [error, setError] = useState(null);
  
  const [shares, setShares] = useState(1);
  const [trading, setTrading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    
    setLoadingPrice(true);
    setError(null);
    setPrice(null);
    
    try {
      const response = await apiClient(`/api/live_price?ticker=${ticker.toUpperCase().trim()}`);
      setPrice(response.price);
    } catch (err) {
      setError(err.message || 'Failed to fetch price');
    } finally {
      setLoadingPrice(false);
    }
  };

  const handleTrade = async (action) => {
    if (!price || shares <= 0) return;
    setTrading(true);
    setError(null);
    
    const result = await executeTrade(ticker.toUpperCase().trim(), action, parseInt(shares, 10), price);
    
    if (result.success) {
      alert(`Trade successful! ${action} ${shares} shares of ${ticker.toUpperCase()} at $${price.toFixed(2)}`);
      // Reset form
      setTicker('');
      setPrice(null);
      setShares(1);
    } else {
      setError(result.message || 'Trade failed');
    }
    
    setTrading(false);
  };

  return (
    <div className="card mt-4" style={{ border: '1px solid var(--primary)' }}>
      <div className="card-header" style={{ marginBottom: '1rem' }}>
        <Zap size={20} className="icon-accent" />
        <h3>Quick Trade</h3>
      </div>
      
      {error && (
        <div style={{ color: 'var(--error)', marginBottom: '1rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '1rem' }}>
        <div style={{ flex: 1 }}>
          <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Ticker Symbol</label>
          <input 
            type="text" 
            placeholder="e.g. AAPL" 
            value={ticker} 
            onChange={(e) => {
              setTicker(e.target.value);
              setPrice(null); // Reset price when ticker changes
            }}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }}
          />
        </div>
        <button 
          type="submit" 
          className="primary-btn" 
          disabled={loadingPrice || !ticker}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Search size={16} />
          {loadingPrice ? 'Searching...' : 'Get Price'}
        </button>
      </form>

      {price !== null && (
        <div className="fade-in" style={{ padding: '1rem', background: '#0f172a', borderRadius: '6px', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <span style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>Live Price:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold', marginLeft: '0.5rem', color: '#f8fafc' }}>${price.toFixed(2)}</span>
            </div>
            <div>
              <span style={{ color: '#cbd5e1', fontSize: '0.9rem', fontWeight: '500' }}>Est. Total:</span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold', marginLeft: '0.5rem', color: '#f8fafc' }}>${(price * shares).toFixed(2)}</span>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Shares</label>
              <input 
                type="number" 
                min="1"
                value={shares} 
                onChange={(e) => setShares(Math.max(1, parseInt(e.target.value || '1', 10)))}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', background: '#1e293b', color: '#fff' }}
              />
            </div>
            <button 
              type="button" 
              className="primary-btn" 
              onClick={() => handleTrade('BUY')}
              disabled={trading}
              style={{ background: 'var(--success)', border: 'none', color: '#fff' }}
            >
              {trading ? 'Processing...' : 'BUY'}
            </button>
            <button 
              type="button" 
              className="primary-btn" 
              onClick={() => handleTrade('SELL')}
              disabled={trading}
              style={{ background: 'var(--error)', border: 'none', color: '#fff' }}
            >
              {trading ? 'Processing...' : 'SELL'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
