import React from 'react';
import { Clock } from 'lucide-react';
import { getSignalClass } from '../utils';

export function HistoryPanel({ history }) {
  if (!history || history.length === 0) return null;

  return (
    <div className="card" style={{marginBottom: "2rem", background: 'none', border: 'none', padding: 0}}>
      <h3 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem'}}>
        <Clock size={18} className="icon-accent" /> 
        <span>Analysis History</span>
      </h3>
      <div style={{
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
        gap: '1rem'
      }}>
        {history.map((h, i) => (
          <div key={i} className="card glass-panel hover-lift" style={{padding: '1.25rem', margin: 0}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem'}}>
              <h4 className="font-mono" style={{margin: 0, fontSize: '1.2rem', color: '#f8fafc'}}>{h.ticker}</h4>
              <span className={`signal-badge ${getSignalClass(h.signal)}`} style={{fontSize: '0.85rem', padding: '0.25rem 0.75rem'}}>
                {h.signal}
              </span>
            </div>
            
            <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
              <div style={{display: 'flex', justifyContent: 'space-between'}}>
                <span className="text-muted" style={{fontSize: '0.9rem'}}>Confidence Score</span>
                <span className="font-mono" style={{color: '#f8fafc', fontWeight: 'bold'}}>{h.score}</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between'}}>
                <span className="text-muted" style={{fontSize: '0.9rem'}}>Winning Model</span>
                <span style={{fontSize: '0.9rem', color: '#f8fafc', fontWeight: '500'}}>{h.model}</span>
              </div>
            </div>
            
            <div style={{marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.85rem', color: '#cbd5e1', textAlign: 'right'}}>
              {new Date(h.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
