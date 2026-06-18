"""Shared pytest fixtures and mock factories."""
import pytest
import pandas as pd
import numpy as np

from src.domain.analysis.schemas import QuantResult, SentimentResult, FusionResult


@pytest.fixture
def sample_train_df():
    """Create a synthetic training DataFrame with all required features."""
    np.random.seed(42)
    n = 200
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    close = 100 + np.cumsum(np.random.randn(n) * 2)

    df = pd.DataFrame({"Close": close}, index=dates)
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    df["RSI_14"] = df["RSI_14"].fillna(100)

    df["Daily_Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
    df["Target"] = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)
    df.loc[df.index[-1], "Target"] = np.nan

    df = df.dropna(subset=["SMA_50"])
    return df


@pytest.fixture
def sample_latest_features(sample_train_df):
    """Latest features row (last row of the synthetic DF)."""
    return sample_train_df.iloc[-1:].copy()


@pytest.fixture
def sample_training_data(sample_train_df):
    """Training data (all rows except the last)."""
    train = sample_train_df.iloc[:-1].copy()
    train["Target"] = train["Target"].astype(int)
    return train


@pytest.fixture
def sample_quant_result():
    return QuantResult(
        probability_up=0.72,
        cv_accuracy=0.51,
        model_name="RandomForest",
        features_used=["SMA_20", "SMA_50", "EMA_20", "RSI_14", "Daily_Log_Return"],
    )


@pytest.fixture
def sample_sentiment_result():
    return SentimentResult(
        score=5,
        summary="Bullish outlook due to strong earnings.",
        headlines=["Company reports strong Q2"],
        provider_used="DDGS",
    )


FEATURES = ["SMA_20", "SMA_50", "EMA_20", "RSI_14", "Daily_Log_Return"]
