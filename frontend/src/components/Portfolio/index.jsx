import React, { useState, useEffect } from 'react';
import { TradeModal } from '../TradeModal';
import { QuickTrade } from '../QuickTrade';
import { PortfolioSummary } from './PortfolioSummary';
import { EquityCurve } from './EquityCurve';
import { HoldingsTable } from './HoldingsTable';
import { TransactionHistory } from './TransactionHistory';

export function Portfolio({ portfolioData, historyData, fetchPortfolio, executeTrade, loading }) {
  const [tradeConfig, setTradeConfig] = useState(null);
  
  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  if (loading && !portfolioData) {
    return <div className="skeleton skeleton-hero"></div>;
  }

  if (!portfolioData) return null;

  const holdingsValue = Object.entries(portfolioData.holdings).reduce((sum, [ticker, shares]) => {
    const price = portfolioData.current_prices?.[ticker] || 0;
    return sum + (price * shares);
  }, 0);
  
  const totalPnl = Object.values(portfolioData.unrealized_pnl || {}).reduce((sum, pnl) => sum + pnl, 0);
  const totalPortfolioValue = portfolioData.cash_balance + holdingsValue;

  return (
    <div className="portfolio-container fade-in">
      {tradeConfig && (
        <TradeModal 
          ticker={tradeConfig.ticker}
          currentPrice={tradeConfig.currentPrice}
          executeTrade={executeTrade}
          onClose={() => setTradeConfig(null)}
        />
      )}
      
      <PortfolioSummary 
        portfolioData={portfolioData} 
        totalPnl={totalPnl} 
        totalPortfolioValue={totalPortfolioValue} 
      />

      <QuickTrade executeTrade={executeTrade} />

      <EquityCurve historyData={historyData} />

      <HoldingsTable 
        portfolioData={portfolioData} 
        setTradeConfig={setTradeConfig} 
      />

      <TransactionHistory 
        transactions={portfolioData.transactions} 
      />
    </div>
  );
}
