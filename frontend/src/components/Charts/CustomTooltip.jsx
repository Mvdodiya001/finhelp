import React from 'react';

export const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    // payload[0] might be wick, payload[1] body, payload[2] volume. 
    // We just need the raw data from the first payload element.
    const data = payload[0].payload;
    const isGrowing = data.close > data.open;
    const color = isGrowing ? 'var(--success)' : 'var(--error)';

    return (
      <div className="custom-tooltip" style={{ backgroundColor: 'var(--bg-card)', padding: '10px', border: '1px solid var(--border-color)', borderRadius: '8px', boxShadow: 'var(--shadow-md)' }}>
        <p className="label" style={{ color: 'var(--text-muted)', marginBottom: '5px' }}>{data.date}</p>
        <p style={{ margin: 0, color: 'var(--text-main)' }}>Open: <span style={{color}}>${data.open.toFixed(2)}</span></p>
        <p style={{ margin: 0, color: 'var(--text-main)' }}>High: <span style={{color}}>${data.high.toFixed(2)}</span></p>
        <p style={{ margin: 0, color: 'var(--text-main)' }}>Low: <span style={{color}}>${data.low.toFixed(2)}</span></p>
        <p style={{ margin: 0, color: 'var(--text-main)' }}>Close: <span style={{color}}>${data.close.toFixed(2)}</span></p>
        <p style={{ margin: 0, color: 'var(--text-muted)', marginTop: '5px' }}>Volume: {(data.volume / 1000).toFixed(1)}K</p>
      </div>
    );
  }
  return null;
};
