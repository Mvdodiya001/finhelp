"""Tests for Pydantic domain models — serialization, validation, and constraints."""
import pytest
from src.domain.analysis.schemas import (
    QuantResult, SentimentResult, FusionResult, AnalysisResponse,
    HistoricalBar, WatchlistRequest, WatchlistResponse,
)


class TestQuantResult:
    def test_valid_creation(self):
        q = QuantResult(probability_up=0.75, cv_accuracy=0.52, model_name="RandomForest", features_used=["SMA_20"])
        assert q.probability_up == 0.75
        assert q.model_name == "RandomForest"

    def test_probability_clamped(self):
        with pytest.raises(Exception):
            QuantResult(probability_up=1.5, cv_accuracy=0.5, model_name="RF", features_used=[])

    def test_serialization_round_trip(self):
        q = QuantResult(probability_up=0.5, cv_accuracy=0.5, model_name="RF", features_used=["A", "B"])
        data = q.model_dump()
        q2 = QuantResult(**data)
        assert q == q2


class TestSentimentResult:
    def test_valid_creation(self):
        s = SentimentResult(score=7, summary="Bullish", headlines=["test"], provider_used="DDGS")
        assert s.score == 7

    def test_score_range(self):
        with pytest.raises(Exception):
            SentimentResult(score=15, summary="x", headlines=[], provider_used="x")


class TestFusionResult:
    def test_signal_labels(self):
        f = FusionResult(final_score=0.8, signal="Strong Buy", ml_normalized=0.9, llm_normalized=0.7)
        assert f.signal == "Strong Buy"


class TestWatchlistRequest:
    def test_max_tickers(self):
        with pytest.raises(Exception):
            WatchlistRequest(tickers=["A"] * 11)

    def test_min_tickers(self):
        with pytest.raises(Exception):
            WatchlistRequest(tickers=[])
