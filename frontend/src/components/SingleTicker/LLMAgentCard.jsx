import React from 'react';
import { BrainCircuit, Activity } from 'lucide-react';

export function LLMAgentCard({ data }) {
  return (
    <div className="card flex-column">
      <h3 className="card-header">
        <BrainCircuit size={18} className="icon-accent" />
        <span>The Context (LLM Agent)</span>
      </h3>
      
      <div className="metric-group">
        <div className="metric-label">Raw Sentiment Score</div>
        <div className="metric-value font-mono">
          <span className={data.sentiment.score > 0 ? 'text-buy' : data.sentiment.score < 0 ? 'text-avoid' : ''}>
            {data.sentiment.score > 0 ? '+' : ''}{data.sentiment.score}
          </span>
          <span className="text-muted" style={{fontSize: "1rem"}}> / 10</span>
        </div>
      </div>

      <div className="blockquote">
        <p>"{data.sentiment.summary}"</p>
      </div>

      <div className="headlines-container mt-4 flex-grow">
        <div className="metric-label mb-2 flex-between">
          <span>Recent Headlines Analyzed</span>
          <Activity size={14} className="text-muted" />
        </div>
        <ul className="headlines-list custom-scrollbar">
          {data.sentiment.headlines.map((headline, i) => {
            const match = headline.match(/^(.*?)\s*\(Source:\s*(.*?)\)$/);
            if (match) {
              return (
                <li key={i} className="headline-item">
                  <span className="headline-text">{match[1]}</span>
                  <span className="headline-source badge">{match[2]}</span>
                </li>
              );
            }
            return <li key={i} className="headline-item"><span className="headline-text">{headline}</span></li>;
          })}
          {data.sentiment.headlines.length === 0 && (
            <li className="headline-item text-muted justify-center py-4">
              No recent news fetched.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
