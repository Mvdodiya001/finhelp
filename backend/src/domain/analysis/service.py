import pandas as pd

from src.core.dependencies import ServiceContainer
from src.core.logger import get_logger
from src.domain.analysis.schemas import AnalysisResponse, FusionResult, HistoricalBar, QuantResult, SentimentResult

logger = get_logger(__name__)

FEATURES: list[str] = [
    "SMA_20",
    "SMA_50",
    "EMA_20",
    "RSI_14",
    "Daily_Log_Return",
]

def run_analysis_pipeline(
    ticker: str,
    period: str,
    container: ServiceContainer,
) -> AnalysisResponse:
    """Execute the full quant → sentiment → fusion pipeline for *ticker*.

    Args:
        ticker: The stock ticker symbol.
        period: Historical data look-back period.
        container: The wired service container.

    Returns:
        A fully populated ``AnalysisResponse`` Pydantic model.

    Raises:
        ValueError: Propagated from the data engine when the ticker is invalid.
        Exception: Any unexpected error from downstream engines.
    """
    # 1. Quantitative Pipeline
    train_df, latest_features = container.data_engine.fetch_and_engineer(
        ticker, period=period
    )
    quant: QuantResult = container.ml_strategy.train_and_predict(
        ticker, train_df, latest_features, FEATURES
    )

    # 2. Qualitative Pipeline
    headlines: list[str] = container.news_provider.fetch_news(ticker, limit=5)
    sentiment: SentimentResult = container.llm_provider.analyze_sentiment(headlines)

    # 3. Fusion Engine
    fusion: FusionResult = container.fusion_engine.generate_signal(quant, sentiment)

    # 4. Historical charting data (last 120 bars)
    hist_data = train_df[["Close", "SMA_20", "SMA_50"]].tail(120)
    historical_bars: list[HistoricalBar] = [
        HistoricalBar(
            date=date.strftime("%Y-%m-%d"),
            close=None if pd.isna(row["Close"]) else float(row["Close"]),
            sma_20=None if pd.isna(row["SMA_20"]) else float(row["SMA_20"]),
            sma_50=None if pd.isna(row["SMA_50"]) else float(row["SMA_50"]),
        )
        for date, row in hist_data.iterrows()
    ]

    return AnalysisResponse(
        ticker=ticker,
        historical_data=historical_bars,
        quant=quant,
        sentiment=sentiment,
        fusion=fusion,
    )
