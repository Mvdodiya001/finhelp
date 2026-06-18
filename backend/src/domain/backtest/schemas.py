from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class BacktestRequest(BaseModel):
    ticker: str
    period: str = "5y"

class EquityPoint(BaseModel):
    date: str
    strategy_value: float
    buy_hold_value: float

class TradeLog(BaseModel):
    date: str
    action: str
    price: float
    profit: float = 0.0

class BacktestResponse(BaseModel):
    ticker: str
    strategy_used: str
    roi: float
    sharpe_ratio: float
    max_drawdown: float
    buy_hold_roi: float
    equity_curve: list[EquityPoint]
    trades: list[TradeLog] = []
    total_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    total_commission: float = 0.0