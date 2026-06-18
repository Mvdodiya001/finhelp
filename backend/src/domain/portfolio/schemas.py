from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class PortfolioTransactionResponse(BaseModel):
    ticker: str
    action: str
    shares: int
    price: float
    timestamp: datetime

class PortfolioResponse(BaseModel):
    cash_balance: float
    holdings: dict[str, int]
    transactions: list[PortfolioTransactionResponse]
    current_prices: dict[str, float] = Field(default_factory=dict)
    unrealized_pnl: dict[str, float] = Field(default_factory=dict)
    total_transactions: int = 0
    page: int = 1
    limit: int = 20

class TradeRequest(BaseModel):
    ticker: str
    action: str
    shares: int
    price: float
