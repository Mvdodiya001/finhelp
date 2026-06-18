import React from 'react';
import { useLivePrice } from '../../hooks/useLivePrice';
import { TickerHero } from './TickerHero';
import { MLEngineCard } from './MLEngineCard';
import { LLMAgentCard } from './LLMAgentCard';

export function SingleTicker({ data, executeTrade, portfolioData }) {
  const livePrice = useLivePrice(data?.ticker);

  if (!data) return null;

  const basePrice = data.historical_data && data.historical_data.length > 0 
    ? data.historical_data[data.historical_data.length - 1].close 
    : 0;

  const currentPrice = livePrice !== null ? livePrice : basePrice;

  const displayHistoricalData = data.historical_data ? [...data.historical_data] : [];
  if (displayHistoricalData.length > 0 && livePrice !== null) {
    displayHistoricalData[displayHistoricalData.length - 1] = {
      ...displayHistoricalData[displayHistoricalData.length - 1],
      close: livePrice
    };
  }

  const previousPrice = data.historical_data && data.historical_data.length > 1
    ? data.historical_data[data.historical_data.length - 2].close
    : basePrice;

  const priceChange = currentPrice - previousPrice;
  const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0;

  const holding = portfolioData?.holdings?.[data.ticker];
  const unrealizedPnl = holding ? (currentPrice - holding.avg_price) * holding.shares : 0;
  const pnlPercent = holding && holding.avg_price > 0 ? (unrealizedPnl / (holding.avg_price * holding.shares)) * 100 : 0;

  return (
    <main>
      <TickerHero 
        data={data}
        currentPrice={currentPrice}
        priceChange={priceChange}
        priceChangePercent={priceChangePercent}
        holding={holding}
        unrealizedPnl={unrealizedPnl}
        pnlPercent={pnlPercent}
        executeTrade={executeTrade}
      />
      <section className="grid">
        <MLEngineCard 
          data={data} 
          displayHistoricalData={displayHistoricalData} 
        />
        <LLMAgentCard 
          data={data} 
        />
      </section>
    </main>
  );
}
