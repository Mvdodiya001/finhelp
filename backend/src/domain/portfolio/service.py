from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from src.shared.db_models import PortfolioTransaction, User
from src.domain.portfolio.schemas import PortfolioResponse, PortfolioTransactionResponse
from src.core.logger import get_logger

logger = get_logger(__name__)

def calculate_portfolio_valuation(
    page: int,
    limit: int,
    current_user: User,
    db: Session
) -> PortfolioResponse:
    transactions = db.query(PortfolioTransaction).filter(PortfolioTransaction.user_id == current_user.id).all()
    
    holdings = {}
    cost_basis = {}  # ticker -> total cost spent on shares currently held
    for t in transactions:
        if t.ticker not in holdings:
            holdings[t.ticker] = 0
            cost_basis[t.ticker] = 0.0
        if t.action == "BUY":
            holdings[t.ticker] += t.shares
            cost_basis[t.ticker] += t.shares * t.price
        else:
            holdings[t.ticker] -= t.shares
            cost_basis[t.ticker] -= t.shares * t.price

    # Clean up zero-share holdings
    holdings = {k: v for k, v in holdings.items() if v > 0}
    cost_basis = {k: v for k, v in cost_basis.items() if k in holdings}

    # Fetch current prices for P&L
    current_prices = {}
    unrealized_pnl = {}
    if holdings:
        for ticker in holdings:
            try:
                info = yf.Ticker(ticker).fast_info
                price = float(info.get("lastPrice", 0) or info.get("last_price", 0))
                if price > 0:
                    current_prices[ticker] = price
                    market_value = price * holdings[ticker]
                    unrealized_pnl[ticker] = round(market_value - cost_basis.get(ticker, 0), 2)
            except Exception:
                pass

    all_sorted = sorted(transactions, key=lambda x: x.timestamp, reverse=True)
    total_transactions = len(all_sorted)
    start = (page - 1) * limit
    paginated = all_sorted[start:start + limit]

    tx_list = [
        PortfolioTransactionResponse(
            ticker=t.ticker,
            action=t.action,
            shares=t.shares,
            price=t.price,
            timestamp=t.timestamp
        ) for t in paginated
    ]

    return PortfolioResponse(
        cash_balance=current_user.cash_balance,
        holdings=holdings,
        transactions=tx_list,
        current_prices=current_prices,
        unrealized_pnl=unrealized_pnl,
        total_transactions=total_transactions,
        page=page,
        limit=limit,
    )

def calculate_portfolio_history(
    days: int,
    current_user: User,
    db: Session
) -> dict:
    transactions = db.query(PortfolioTransaction).filter(
        PortfolioTransaction.user_id == current_user.id
    ).order_by(PortfolioTransaction.timestamp.asc()).all()

    # Get all unique tickers ever traded
    tickers = list(set(t.ticker for t in transactions))
    
    # Fetch historical data for all tickers over the period
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days + 5) # Extra days for weekends
    
    hist_prices = {}
    if tickers:
        try:
            df = yf.download(tickers, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), progress=False)
            if 'Close' in df:
                close_df = df['Close']
            else:
                close_df = df
            
            if isinstance(close_df, pd.Series):
                hist_prices[tickers[0]] = close_df
            else:
                for ticker in tickers:
                    if ticker in close_df.columns:
                        hist_prices[ticker] = close_df[ticker]
        except Exception as e:
            logger.error(f"Failed to fetch historical prices for P&L graph: {e}")

    # Reconstruct portfolio day by day
    history = []
    
    # Starting balance is 10000.0, we need to track cash from beginning of time
    current_cash = 10000.0
    current_holdings = {t: 0 for t in tickers}
    
    # We will iterate day by day for the requested window
    target_dates = [(end_date - timedelta(days=i)).date() for i in range(days-1, -1, -1)]
    
    tx_idx = 0
    total_tx = len(transactions)
    
    for date in target_dates:
        # Apply transactions up to the end of this day
        while tx_idx < total_tx and transactions[tx_idx].timestamp.date() <= date:
            t = transactions[tx_idx]
            if t.action == "BUY":
                current_cash -= t.shares * t.price
                current_holdings[t.ticker] += t.shares
            else:
                current_cash += t.shares * t.price
                current_holdings[t.ticker] -= t.shares
            tx_idx += 1
            
        # Value the portfolio
        portfolio_value = current_cash
        for ticker, shares in current_holdings.items():
            if shares > 0 and ticker in hist_prices:
                # Get the latest price on or before this date
                ticker_history = hist_prices[ticker]
                # Filter to dates <= current date
                past_prices = ticker_history[ticker_history.index.date <= date]
                if not past_prices.empty:
                    # Fillna just in case
                    last_price = past_prices.ffill().iloc[-1]
                    if pd.notna(last_price):
                        portfolio_value += shares * float(last_price)
                        
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(portfolio_value, 2)
        })
        
    return {"history": history}
