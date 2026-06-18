import React from 'react';
import { TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

export function MLEngineCard({ data, displayHistoricalData }) {
  return (
    <div className="card flex-column">
      <h3 className="card-header">
        <TrendingUp size={18} className="icon-accent" />
        <span>The Math (ML Ensemble)</span>
      </h3>
      
      <div className="metrics-row">
        <div className="metric-group flex-1">
          <div className="metric-label">Ensemble P(Up)</div>
          <div className="metric-value font-mono highlight-text">
            {(data.quant.probability_up * 100).toFixed(2)}%
          </div>
        </div>
        <div className="metric-group flex-1">
          <div className="metric-label">Ensemble CV Accuracy</div>
          <div className="metric-value font-mono">
            {(data.quant.cv_accuracy * 100).toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Sub-model breakdown */}
      {data.quant.sub_models && data.quant.sub_models.length > 0 && (
        <div className="sub-models-container mt-4">
          <div className="metric-label mb-2">Model Breakdown</div>
          <div className="sub-models-list">
            {data.quant.sub_models.map((sub, i) => (
              <div key={i} className="sub-model-item">
                <div className="sub-model-info">
                  <span className="fw-bold">{sub.model_name}</span>
                  <span className="sub-model-weight">
                    {(sub.weight * 100).toFixed(0)}% weight
                  </span>
                </div>
                <div className="sub-model-score font-mono fw-bold text-accent">
                  {(sub.probability_up * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Confidence Interval */}
      {data.quant.confidence_interval && data.quant.confidence_interval.length === 2 && (
        <div className="mt-4">
          <div className="metric-label mb-2">95% Confidence Interval</div>
          <div style={{ position: 'relative', height: 32, background: 'rgba(255,255,255,0.05)', borderRadius: 8, overflow: 'hidden' }}>
            <div style={{
              position: 'absolute',
              left: `${data.quant.confidence_interval[0] * 100}%`,
              width: `${(data.quant.confidence_interval[1] - data.quant.confidence_interval[0]) * 100}%`,
              height: '100%',
              background: 'linear-gradient(90deg, rgba(99,102,241,0.3), rgba(99,102,241,0.6))',
              borderRadius: 6,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-main)' }}>
                {(data.quant.confidence_interval[0] * 100).toFixed(1)}% — {(data.quant.confidence_interval[1] * 100).toFixed(1)}%
              </span>
            </div>
            {/* Pointer for the P(Up) value */}
            <div style={{
              position: 'absolute',
              left: `${data.quant.probability_up * 100}%`,
              top: 0, height: '100%', width: 2,
              background: 'var(--primary)',
              transform: 'translateX(-1px)'
            }} />
          </div>
        </div>
      )}

      {/* Feature Importance */}
      {data.quant.feature_importances && Object.keys(data.quant.feature_importances).length > 0 && (
        <div className="mt-4">
          <div className="metric-label mb-2">Feature Importance</div>
          <div style={{ width: '100%', height: Math.max(120, Object.keys(data.quant.feature_importances).length * 32) }}>
            <ResponsiveContainer>
              <BarChart
                data={Object.entries(data.quant.feature_importances)
                  .map(([name, value]) => ({ name, value: parseFloat((value * 100).toFixed(1)) }))
                  .sort((a, b) => b.value - a.value)}
                layout="vertical"
                margin={{ top: 0, right: 20, bottom: 0, left: 80 }}
              >
                <XAxis type="number" stroke="#888" tick={{ fill: '#888', fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="name" stroke="#888" tick={{ fill: '#ccc', fontSize: 11 }} width={75} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px' }}
                  formatter={(value) => `${value}%`}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {Object.entries(data.quant.feature_importances)
                    .map(([name, value]) => ({ name, value }))
                    .sort((a, b) => b.value - a.value)
                    .map((entry, index) => (
                      <Cell key={index} fill={index === 0 ? 'var(--primary)' : index === 1 ? '#6366f1' : '#4b5563'} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="chart-container mt-4 flex-grow">
        <div className="metric-label mb-2">Historical Trend & Moving Averages</div>
        <div style={{ width: '100%', height: 250 }}>
          <ResponsiveContainer>
            <LineChart data={displayHistoricalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
              <XAxis dataKey="date" stroke="var(--text-muted)" tick={{fontSize: 10, fill: "var(--text-muted)"}} tickLine={false} axisLine={false} minTickGap={30} />
              <YAxis stroke="var(--text-muted)" domain={['auto', 'auto']} tick={{fontSize: 10, fill: "var(--text-muted)"}} tickLine={false} axisLine={false} width={40} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--bg-card)', 
                  borderColor: 'var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-main)',
                  boxShadow: 'var(--shadow-md)'
                }} 
                itemStyle={{color: 'var(--text-main)'}}
              />
              <Line type="monotone" dataKey="close" stroke="#0F172A" dot={false} strokeWidth={2} activeDot={{r: 6, fill: "var(--color-accent)", stroke: "#fff", strokeWidth: 2}} />
              <Line type="monotone" dataKey="sma_20" stroke="#3b82f6" dot={false} strokeWidth={1.5} opacity={0.8} />
              <Line type="monotone" dataKey="sma_50" stroke="#f59e0b" dot={false} strokeWidth={1.5} opacity={0.8} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-legend">
          <span className="legend-item"><span className="legend-color" style={{backgroundColor: '#0F172A'}}></span> Close</span>
          <span className="legend-item"><span className="legend-color" style={{backgroundColor: '#3b82f6'}}></span> SMA 20</span>
          <span className="legend-item"><span className="legend-color" style={{backgroundColor: '#f59e0b'}}></span> SMA 50</span>
        </div>
      </div>
    </div>
  );
}
