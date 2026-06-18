import React, { useState } from 'react';

export function TradeModal({ ticker, currentPrice, executeTrade, onClose }) {
  const [action, setAction] = useState('BUY');
  const [shares, setShares] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const result = await executeTrade(ticker, action, parseInt(shares, 10), currentPrice);
    setSubmitting(false);
    
    if (result.success) {
      setMessage({ type: 'success', text: result.message });
      setTimeout(onClose, 2000);
    } else {
      setMessage({ type: 'error', text: result.message });
    }
  };

  return (
    <div style={modalOverlayStyle}>
      <div className="card" style={modalContentStyle}>
        <h2>Trade {ticker}</h2>
        <p style={{ color: 'var(--text-muted)' }}>Current Price: <strong>${currentPrice.toFixed(2)}</strong></p>
        
        {message && (
          <div className="mb-4" style={{ color: message.type === 'error' ? 'var(--error)' : 'var(--success)' }}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', gap: '1rem', margin: '1rem 0' }}>
            <button 
              type="button" 
              className={`toggle-btn ${action === 'BUY' ? 'active' : ''}`}
              onClick={() => setAction('BUY')}
              style={{ flex: 1, borderColor: action === 'BUY' ? 'var(--success)' : '' }}
            >
              BUY
            </button>
            <button 
              type="button" 
              className={`toggle-btn ${action === 'SELL' ? 'active' : ''}`}
              onClick={() => setAction('SELL')}
              style={{ flex: 1, borderColor: action === 'SELL' ? 'var(--error)' : '' }}
            >
              SELL
            </button>
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Shares</label>
            <input 
              type="number" 
              min="1" 
              value={shares} 
              onChange={(e) => setShares(e.target.value)}
              style={{ width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', padding: '0.75rem', color: 'white', borderRadius: '8px' }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', fontSize: '1.2rem' }}>
            <span>Total:</span>
            <span className="gradient-text">${(shares * currentPrice).toFixed(2)}</span>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button type="button" className="glass-select" onClick={onClose} style={{ flex: 1, textAlign: 'center' }}>Cancel</button>
            <button type="submit" className="primary-btn" style={{ flex: 1 }} disabled={submitting}>
              {submitting ? 'Processing...' : 'Confirm'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const modalOverlayStyle = {
  position: 'fixed',
  top: 0, left: 0, right: 0, bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  backdropFilter: 'blur(4px)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000
};

const modalContentStyle = {
  width: '100%',
  maxWidth: '400px',
  border: '1px solid rgba(255,255,255,0.1)'
};
