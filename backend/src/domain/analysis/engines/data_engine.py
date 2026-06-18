"""
DataEngine — Fetches historical OHLCV data and engineers technical features.

Implements the IDataEngine interface defined in src/interfaces.py.
All market data is fetched via yfinance; technical indicators (SMA, EMA, RSI,
log-returns) are computed in-place before splitting into training and
latest-feature DataFrames.
"""

import time
from typing import Tuple

import numpy as np
import pandas as pd
import polars as pl
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.interfaces import IDataEngine
from src.core.logger import get_logger

logger = get_logger(__name__)


class DataEngine(IDataEngine):
    """Concrete implementation of IDataEngine using yfinance and pandas.

    Responsibilities:
        1. Download historical OHLCV bars for any ticker supported by yfinance.
        2. Compute a standard set of technical indicators (SMA-20, SMA-50,
           EMA-20, RSI-14, daily log-return).
        3. Construct a binary classification target:
           Target = 1 if next bar's Close > current Close, else 0.
        4. Split into a labelled training DataFrame and a single-row
           latest-features DataFrame (Target = NaN) for live prediction.

    Design notes:
        - The Target column is calculated on the *full* DataFrame before any
          row is dropped, avoiding the off-by-one bug that appeared in the
          legacy implementation.
        - NaN rows introduced by the 50-period SMA warm-up are removed after
          target assignment so the alignment stays correct.
    """

    _WARMUP_COLUMN: str = "SMA_50"
    _cache: dict[str, tuple[float, pd.DataFrame]] = {}
    _CACHE_TTL: int = 300

    def fetch_and_engineer(
        self, ticker: str, period: str = "2y"
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch historical data for *ticker* and return engineered features.

        Args:
            ticker: A yfinance-compatible ticker symbol (e.g. ``"RELIANCE.NS"``).
            period: Look-back period string accepted by ``yf.Ticker.history``
                    (e.g. ``"1y"``, ``"2y"``, ``"5y"``).

        Returns:
            A 2-tuple ``(train_df, latest_features)``:
            * **train_df** — Historical rows with all technical indicators
              plus a ``Target`` column (``int``, 0 or 1). No NaN values remain.
            * **latest_features** — A single-row DataFrame containing
              today's indicator values. ``Target`` is ``NaN``.

        Raises:
            ValueError: If yfinance returns an empty DataFrame for *ticker*.
        """
        df = self._download(ticker, period)
        df_pl = pl.from_pandas(df.reset_index())
        df_pl = self._add_indicators(df_pl)
        df_pl = self._add_target(df_pl)
        df_pl = self._drop_warmup_rows(df_pl)
        
        df_pd = df_pl.to_pandas()
        if "Date" in df_pd.columns:
            df_pd.set_index("Date", inplace=True)
            
        return self._split(df_pd)

    def fetch_backtest_data(
        self, ticker: str, period: str = "5y"
    ) -> pd.DataFrame:
        """Fetch historical data for backtesting simulation."""
        df = self._download(ticker, period)
        df_pl = pl.from_pandas(df.reset_index())
        df_pl = self._add_indicators(df_pl)
        df_pl = self._add_target(df_pl)
        df_pl = self._drop_warmup_rows(df_pl)
        
        df_pd = df_pl.to_pandas()
        if "Date" in df_pd.columns:
            df_pd.set_index("Date", inplace=True)
            
        # Drop the last row because it doesn't have a next-day target
        df_pd = df_pd.dropna(subset=["Target"]).copy()
        df_pd["Target"] = df_pd["Target"].astype(int)
        return df_pd

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _download(ticker: str, period: str) -> pd.DataFrame:
        """Download OHLCV history from yfinance."""
        cache_key = f"{ticker}:{period}"
        now = time.time()
        
        if cache_key in DataEngine._cache:
            timestamp, cached_df = DataEngine._cache[cache_key]
            if now - timestamp < DataEngine._CACHE_TTL:
                logger.debug("DataEngine cache hit for %s", cache_key)
                return cached_df.copy()

        logger.info("Fetching %s of data for %s …", period, ticker)
        stock = yf.Ticker(ticker)
        df: pd.DataFrame = stock.history(period=period)

        if df.empty:
            raise ValueError(f"No data returned for ticker '{ticker}'")

        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
            
        DataEngine._cache[cache_key] = (now, df.copy())

        return df

    @staticmethod
    def _add_indicators(df: pl.DataFrame) -> pl.DataFrame:
        """Compute technical indicators using Polars for high performance."""
        df = df.with_columns([
            pl.col("Close").rolling_mean(window_size=20).alias("SMA_20"),
            pl.col("Close").rolling_mean(window_size=50).alias("SMA_50"),
            pl.col("Close").ewm_mean(span=20, adjust=False).alias("EMA_20"),
            (pl.col("Close") / pl.col("Close").shift(1)).log().alias("Daily_Log_Return")
        ])
        
        delta = pl.col("Close").diff()
        gain = pl.when(delta > 0).then(delta).otherwise(0).rolling_mean(window_size=14)
        loss = pl.when(delta < 0).then(-delta).otherwise(0).rolling_mean(window_size=14)
        rs = gain / pl.when(loss == 0).then(None).otherwise(loss)
        rsi = 100 - (100 / (1 + rs))
        
        df = df.with_columns([
            rsi.fill_null(100).alias("RSI_14")
        ])
        return df

    @staticmethod
    def _add_target(df: pl.DataFrame) -> pl.DataFrame:
        """Create the binary Target column using Polars."""
        df = df.with_columns([
            pl.when(pl.col("Close").shift(-1) > pl.col("Close")).then(1).otherwise(0).alias("Target")
        ])
        # Set the last target to null (NaN)
        df = df.with_columns(
            pl.when(pl.col("Date") == pl.col("Date").last()).then(None).otherwise(pl.col("Target")).alias("Target")
        )
        return df

    def _drop_warmup_rows(self, df: pl.DataFrame) -> pl.DataFrame:
        """Remove rows where the slowest indicator is still NaN."""
        before = len(df)
        df = df.filter(pl.col(self._WARMUP_COLUMN).is_not_null())
        logger.debug(
            "Dropped %d warm-up rows (SMA_50 NaN); %d rows remain.",
            before - len(df),
            len(df),
        )
        return df

    @staticmethod
    def _split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split into training rows and the latest-feature row."""
        latest_features: pd.DataFrame = df.iloc[-1:].copy()
        train_df: pd.DataFrame = df.iloc[:-1].copy()
        train_df["Target"] = train_df["Target"].astype(int)

        logger.info(
            "Data ready — training rows: %d, feature columns: %s",
            len(train_df),
            list(train_df.columns),
        )
        return train_df, latest_features


if __name__ == "__main__":
    from src.core.logger import setup_logging

    setup_logging()

    logger.info("Running DataEngine smoke tests …")
    engine = DataEngine()
    test_ticker = "RELIANCE.NS"

    try:
        train_df, latest_features = engine.fetch_and_engineer(test_ticker, period="1y")
        logger.info("Training data shape: %s", train_df.shape)
        logger.info("Latest features shape: %s", latest_features.shape)

        nan_count = train_df.isnull().sum().sum()
        assert nan_count == 0, f"TEST FAILED: {nan_count} NaNs in training DataFrame."
        logger.info("TEST PASSED: No NaNs in the training matrix.")

        assert np.isnan(
            latest_features["Target"].iloc[0]
        ), "TEST FAILED: Latest features Target should be NaN."
        logger.info("TEST PASSED: Latest features separated correctly.")

    except Exception as exc:
        logger.error("TEST FAILED: %s", exc, exc_info=True)
