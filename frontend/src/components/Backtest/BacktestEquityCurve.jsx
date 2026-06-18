import React from 'react';
import { Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function BacktestEquityCurve({ data, ticker, period }) {
  const handleExport = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/backtest/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ ticker, period })
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `backtest_${ticker}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Export failed: ' + err.message);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3>Equity Curve</h3>
        <button className="toggle-btn" onClick={handleExport} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Download size={14} /> Export CSV
        </button>
      </div>
      <div style={{ height: 400, width: '100%' }}>
        <ResponsiveContainer>
          <LineChart data={data.equity_curve} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="date" stroke="#888" tick={{ fill: '#888' }} minTickGap={50} />
            <YAxis stroke="#888" tick={{ fill: '#888' }} domain={['auto', 'auto']} tickFormatter={(v) => v.toFixed(2)} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
              labelStyle={{ color: '#888' }}
              formatter={(value) => value.toFixed(4)}
            />
            <Legend />
            <Line type="monotone" dataKey="strategy_value" name="AI Strategy" stroke="var(--primary)" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="buy_hold_value" name="Buy & Hold" stroke="#888" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
