import React, { useMemo } from 'react';
import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { CustomTooltip } from './CustomTooltip';

export function CandlestickChart({ data }) {
  const formattedData = useMemo(() => {
    if (!data || !data.data) return [];
    return data.data.map(d => ({
      ...d,
      body: [Math.min(d.open, d.close), Math.max(d.open, d.close)],
      wick: [d.low, d.high],
      isGrowing: d.close >= d.open,
      // Simplify date label depending on period
      displayDate: data.period.includes('d') ? d.date.substring(11, 16) : d.date.substring(0, 10)
    }));
  }, [data]);

  if (formattedData.length === 0) return null;

  return (
    <div className="card fade-in">
      <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>{data.ticker} <span className="text-muted" style={{fontSize: '0.9rem', marginLeft: '0.5rem'}}>{data.interval} candles</span></h3>
      </div>
      
      <div style={{ height: 500, width: '100%' }}>
        <ResponsiveContainer>
          <ComposedChart data={formattedData} margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            
            {/* X Axis */}
            <XAxis 
              dataKey="displayDate" 
              stroke="var(--text-muted)" 
              tick={{ fontSize: 11, fill: 'var(--text-muted)' }} 
              minTickGap={30} 
              axisLine={false}
              tickLine={false}
            />
            
            {/* Price Y Axis */}
            <YAxis 
              yAxisId="price"
              stroke="var(--text-muted)" 
              domain={['auto', 'auto']} 
              tick={{ fontSize: 11, fill: 'var(--text-muted)' }} 
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `$${v.toFixed(2)}`}
            />
            
            {/* Volume Y Axis (Hidden, scaled to keep bars at bottom) */}
            <YAxis 
              yAxisId="volume" 
              orientation="right" 
              domain={[0, dataMax => dataMax * 4]} 
              hide 
            />
            
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />

            {/* Volume Bars */}
            <Bar yAxisId="volume" dataKey="volume" isAnimationActive={false}>
              {formattedData.map((entry, index) => (
                <Cell key={`vol-${index}`} fill={entry.isGrowing ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'} />
              ))}
            </Bar>

            {/* Candlestick Wicks */}
            <Bar yAxisId="price" dataKey="wick" barSize={2} isAnimationActive={false}>
              {formattedData.map((entry, index) => (
                <Cell key={`wick-${index}`} fill={entry.isGrowing ? 'var(--success)' : 'var(--error)'} />
              ))}
            </Bar>

            {/* Candlestick Bodies */}
            <Bar yAxisId="price" dataKey="body" barSize={8} isAnimationActive={false}>
              {formattedData.map((entry, index) => (
                <Cell key={`body-${index}`} fill={entry.isGrowing ? 'var(--success)' : 'var(--error)'} />
              ))}
            </Bar>

          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
