from fastapi import APIRouter, Depends, HTTPException
from src.shared.db_models import User
from src.domain.auth.service import get_current_user
from src.core.logger import get_logger
import yfinance as yf

logger = get_logger(__name__)

router = APIRouter()

@router.get("/api/live_price")
def get_live_price(
    ticker: str,
    current_user: User = Depends(get_current_user)
):
    try:
        t = yf.Ticker(ticker)
        try:
            price = float(t.fast_info['lastPrice'])
            return {"ticker": ticker, "price": price}
        except Exception:
            # Fallback to history
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                return {"ticker": ticker, "price": float(hist['Close'].iloc[-1])}
            raise ValueError("No price data found")
    except Exception as exc:
        logger.error("Live price error for %s: %s", ticker, exc)
        raise HTTPException(status_code=400, detail="Could not fetch live price")

@router.get("/api/chart")
def get_chart_data(
    ticker: str,
    period: str = "1y",
    current_user: User = Depends(get_current_user)
):
    try:
        t = yf.Ticker(ticker)
        interval = "1d"
        if period in ["1d", "5d"]:
            interval = "5m"
        elif period in ["1mo", "3mo"]:
            interval = "1h"
            
        df = t.history(period=period, interval=interval)
        if df.empty:
            raise ValueError("No data")
            
        data = []
        for date, row in df.iterrows():
            data.append({
                "date": str(date),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            })
        return {"ticker": ticker, "period": period, "interval": interval, "data": data}
    except Exception as exc:
        logger.error("Chart data error for %s: %s", ticker, exc)
        raise HTTPException(status_code=400, detail="Could not fetch chart data")
