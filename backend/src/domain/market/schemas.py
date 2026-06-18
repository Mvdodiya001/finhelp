from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class HistoricalBar(BaseModel):
    """A single row of historical OHLCV + technical indicator data for charting."""
    date: str
    close: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None

