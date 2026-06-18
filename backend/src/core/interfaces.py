"""
Interfaces — Abstract Base Classes defining the contracts for all engines.

Demonstrates:
  - Interface Segregation Principle (ISP): Each ABC has a single, focused responsibility.
  - Dependency Inversion Principle (DIP): High-level modules (main.py) depend on
    these abstractions, not on concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any

import pandas as pd

from src.domain.analysis.schemas import QuantResult, SentimentResult, FusionResult


class IDataEngine(ABC):
    """Responsible for fetching raw market data and engineering technical features."""

    @abstractmethod
    def fetch_and_engineer(self, ticker: str, period: str = "2y") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch historical OHLCV data and compute technical indicators.

        Returns:
            Tuple of (training_df, latest_features_df).
            training_df has a 'Target' column (1 = next close up, 0 = down).
            latest_features_df is 1 row with today's features for prediction.
        """
        ...


class IMLStrategy(ABC):
    """A pluggable ML model strategy for predicting next-bar direction."""

    @abstractmethod
    def get_name(self) -> str:
        """Return a human-readable name for this strategy."""
        ...

    @abstractmethod
    def train_and_predict(
        self,
        ticker: str,
        train_df: pd.DataFrame,
        latest_features: pd.DataFrame,
        features: list[str],
    ) -> QuantResult:
        """
        Train on historical data, run cross-validation, and predict next bar.

        Returns:
            QuantResult with probability, accuracy, and model metadata.
        """
        ...


class INewsProvider(ABC):
    """Fetches recent news headlines for a given ticker."""

    @abstractmethod
    def fetch_news(self, ticker: str, limit: int = 5) -> list[str]:
        """
        Return up to `limit` news headlines/summaries.

        Returns:
            List of formatted headline strings.
        """
        ...


class ILLMProvider(ABC):
    """Analyzes news headlines and produces a sentiment score via an LLM."""

    @abstractmethod
    def analyze_sentiment(self, headlines: list[str]) -> SentimentResult:
        """
        Pass headlines to an LLM and extract structured sentiment.

        Returns:
            SentimentResult with score, summary, and metadata.
        """
        ...


class IFusionEngine(ABC):
    """Merges quantitative ML output and qualitative LLM sentiment into a unified signal."""

    @abstractmethod
    def generate_signal(self, quant: QuantResult, sentiment: SentimentResult) -> FusionResult:
        """
        Combine ML probability and LLM sentiment score.

        Returns:
            FusionResult with final_score, signal label, and component weights.
        """
        ...


class ICacheService(ABC):
    """A generic key-value cache with TTL expiration."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value by key. Returns None if expired or missing."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store a value with a TTL (default 5 minutes)."""
        ...

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        ...

    @abstractmethod
    def stats(self) -> dict:
        """Return cache statistics (hits, misses, size)."""
        ...
