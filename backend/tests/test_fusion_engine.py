"""Tests for the FusionEngine — signal generation with known inputs."""
import pytest
from src.domain.analysis.engines.fusion_engine import FusionEngine
from src.domain.analysis.schemas import QuantResult, SentimentResult, FusionResult


@pytest.fixture
def engine():
    return FusionEngine()


def _make_quant(prob: float) -> QuantResult:
    return QuantResult(probability_up=prob, cv_accuracy=0.5, model_name="Test", features_used=[])


def _make_sentiment(score: int) -> SentimentResult:
    return SentimentResult(score=score, summary="test", headlines=[], provider_used="test")


class TestFusionEngine:
    def test_returns_fusion_result(self, engine):
        result = engine.generate_signal(_make_quant(0.7), _make_sentiment(5))
        assert isinstance(result, FusionResult)

    @pytest.mark.parametrize("ml_prob, llm_score, expected_signal", [
        (0.9, 10, "Strong Buy"),     # Both max bullish
        (0.1, -10, "Avoid"),         # Both max bearish
        (0.5, 0, "Hold"),            # Completely neutral
        (0.8, -8, "Hold"),           # Contradictory signals
        (0.3, 9, "Hold"),            # Contradictory signals
        (0.8, 5, "Strong Buy"),      # Moderately bullish
    ])
    def test_signal_thresholds(self, engine, ml_prob, llm_score, expected_signal):
        result = engine.generate_signal(_make_quant(ml_prob), _make_sentiment(llm_score))
        assert result.signal == expected_signal, (
            f"Expected '{expected_signal}' but got '{result.signal}' "
            f"(final_score={result.final_score:.3f})"
        )

    def test_custom_weights(self):
        engine = FusionEngine(ml_weight=0.8, llm_weight=0.2)
        result = engine.generate_signal(_make_quant(0.9), _make_sentiment(-10))
        # 0.9 * 0.8 + 0.0 * 0.2 = 0.72 → Strong Buy (ML dominates)
        assert result.signal == "Strong Buy"
        assert result.ml_weight == 0.8

    def test_score_bounds(self, engine):
        result = engine.generate_signal(_make_quant(1.0), _make_sentiment(10))
        assert 0.0 <= result.final_score <= 1.0
