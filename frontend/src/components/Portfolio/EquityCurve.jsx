import React from 'react';
import { Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function EquityCurve({ historyData }) {
  if (!historyData || historyData.length === 0) return null;

  return (
    <div className="card mt-4">
      <div className="card-header" style={{ marginBottom: '1rem' }}>
        <Activity size={20} className="icon-accent" />
        <h3>Portfolio Equity Curve (30 Days)</h3>
      </div>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <AreaChart data={historyData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="date" stroke="#64748b" tick={{fill: '#64748b'}} />
            <YAxis stroke="#64748b" tick={{fill: '#64748b'}} domain={['auto', 'auto']} tickFormatter={(v) => `$${v}`} />
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
              itemStyle={{ color: '#60a5fa' }}
              formatter={(value) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
            />
            <Area type="monotone" dataKey="value" stroke="#3b82f6" fillOpacity={1} fill="url(#colorValue)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
