from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re
from src.domain.market.schemas import HistoricalBar

class SubModelResult(BaseModel):
    """Result from a single model within an ensemble."""
    model_name: str
    probability_up: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Weight in the ensemble")


class QuantResult(BaseModel):
    """Output of the ML (quantitative) pipeline."""
    probability_up: float = Field(..., ge=0.0, le=1.0, description="Probability that the next bar closes higher")
    cv_accuracy: float = Field(..., ge=0.0, le=1.0, description="Average cross-validation accuracy")
    model_name: str = Field(..., description="Name of the ML strategy used (e.g., 'RandomForest', 'GradientBoost')")
    features_used: list[str] = Field(default_factory=list, description="List of feature column names used")
    feature_importances: dict[str, float] = Field(default_factory=dict, description="Feature name → importance score")
    confidence_interval: list[float] = Field(default_factory=list, description="[low, high] 95% confidence bounds for P(Up)")
    sub_models: list[SubModelResult] = Field(default_factory=list, description="Per-model breakdown for ensembles")


class SentimentResult(BaseModel):
    """Output of the qualitative (LLM sentiment) pipeline."""
    score: int = Field(..., ge=-10, le=10, description="Sentiment score from -10 (bearish) to +10 (bullish)")
    summary: str = Field(..., description="LLM-generated explanation of the sentiment")
    headlines: list[str] = Field(default_factory=list, description="Raw headlines that were analyzed")
    provider_used: str = Field(default="unknown", description="Which news provider fetched the headlines")


class FusionResult(BaseModel):
    """Output of the fusion engine that merges quant + sentiment signals."""
    final_score: float = Field(..., ge=0.0, le=1.0, description="Weighted confidence score")
    signal: str = Field(..., description="Trading signal label: 'Strong Buy', 'Hold', or 'Avoid'")
    ml_weight: float = Field(default=0.6, description="Weight assigned to the ML component")
    llm_weight: float = Field(default=0.4, description="Weight assigned to the LLM component")
    ml_normalized: float = Field(..., ge=0.0, le=1.0, description="ML probability (already 0-1)")
    llm_normalized: float = Field(..., ge=0.0, le=1.0, description="LLM score normalized to 0-1")


class AnalysisResponse(BaseModel):
    """Full unified response for a single ticker analysis."""
    ticker: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    historical_data: list[HistoricalBar] = Field(default_factory=list)
    quant: QuantResult
    sentiment: SentimentResult
    fusion: FusionResult


class WatchlistRequest(BaseModel):
    """Request body for multi-ticker watchlist analysis."""
    tickers: list[str] = Field(..., min_length=1, max_length=10, description="List of ticker symbols to analyze")
    period: str = Field(default="2y", description="Historical data period")


class WatchlistResponse(BaseModel):
    """Response for multi-ticker watchlist — ranked by fusion score."""
    results: list[AnalysisResponse] = Field(default_factory=list)
    errors: dict[str, str] = Field(default_factory=dict, description="Tickers that failed with error messages")


class AnalyzeRequest(BaseModel):
    ticker: str = Field(
        ...,
        pattern=r"^[A-Z0-9.\-]+$",
        max_length=15,
        description="Valid stock ticker",
    )
    period: str = "2y"
