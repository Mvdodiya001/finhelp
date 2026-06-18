import React, { useState } from 'react';
import { TradeModal } from '../TradeModal';
import { WatchlistTable } from './WatchlistTable';
import { WatchlistErrors } from './WatchlistErrors';

export function Watchlist({ watchlistData, executeTrade }) {
  const [tradeConfig, setTradeConfig] = useState(null);

  if (!watchlistData) return null;

  return (
    <main>
      {tradeConfig && (
        <TradeModal 
          ticker={tradeConfig.ticker}
          currentPrice={tradeConfig.currentPrice}
          executeTrade={executeTrade}
          onClose={() => setTradeConfig(null)}
        />
      )}
      <section className="card" style={{marginBottom: "2rem"}}>
        <h3 className="card-header">
          <span className="gradient-text">📊 Watchlist Comparison</span> 
          <span className="text-muted" style={{fontSize: "0.9rem", marginLeft: "1rem", fontWeight: "normal"}}>Ranked by Score</span>
        </h3>
        
        <WatchlistTable 
          results={watchlistData.results} 
          setTradeConfig={setTradeConfig} 
        />

        <WatchlistErrors 
          errors={watchlistData.errors} 
        />
      </section>
    </main>
  );
}
