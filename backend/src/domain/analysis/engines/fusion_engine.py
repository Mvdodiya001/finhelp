"""
Fusion Engine — Merges quantitative ML output and qualitative LLM sentiment.

Implements the :class:`IFusionEngine` interface.  The engine normalises the
LLM sentiment score from ``[-10, 10]`` to ``[0, 1]``, applies configurable
weights, and maps the combined score to a trading signal.

Signal thresholds:
  - ``>= 0.65``  →  **Strong Buy**
  - ``<= 0.35``  →  **Avoid**
  - otherwise     →  **Hold**
"""

from src.core.interfaces import IFusionEngine
from src.domain.analysis.schemas import QuantResult, SentimentResult, FusionResult
from src.core.logger import get_logger

logger = get_logger(__name__)


class FusionEngine(IFusionEngine):
    """Weighted fusion of ML probability and LLM sentiment into a single signal.

    The engine computes:

    .. code-block:: text

        llm_norm    = (sentiment_score + 10) / 20
        final_score = ml_prob * ml_weight + llm_norm * llm_weight

    and classifies the result into one of three signal buckets.

    Args:
        ml_weight: Weight applied to the ML probability component.
        llm_weight: Weight applied to the normalised LLM score component.

    Attributes:
        _ml_weight: Stored ML weight.
        _llm_weight: Stored LLM weight.
    """

    def __init__(self, ml_weight: float = 0.6, llm_weight: float = 0.4) -> None:
        """Initialize the engine with component weights.

        Args:
            ml_weight: Weight for the ML probability (default ``0.6``).
            llm_weight: Weight for the LLM normalised score (default ``0.4``).
        """
        self._ml_weight: float = ml_weight
        self._llm_weight: float = llm_weight
        logger.info(
            "FusionEngine initialised with ml_weight=%.2f, llm_weight=%.2f",
            self._ml_weight,
            self._llm_weight,
        )

    def generate_signal(
        self, quant: QuantResult, sentiment: SentimentResult
    ) -> FusionResult:
        """Combine ML probability and LLM sentiment into a trading signal.

        Steps:
            1. Normalise the LLM sentiment score from ``[-10, 10]`` → ``[0, 1]``.
            2. Compute a weighted sum of ML probability and normalised LLM score.
            3. Map the final score to a signal label via fixed thresholds.

        Args:
            quant: Output of the quantitative ML pipeline.
            sentiment: Output of the qualitative LLM pipeline.

        Returns:
            A :class:`FusionResult` containing the final score, signal label,
            weights, and normalised component values.
        """
        # Normalise LLM score from [-10, 10] to [0.0, 1.0]
        llm_norm: float = (sentiment.score + 10) / 20.0

        # Weighted combination
        final_score: float = (
            quant.probability_up * self._ml_weight + llm_norm * self._llm_weight
        )

        # Threshold classification
        if final_score >= 0.65:
            signal: str = "Strong Buy"
        elif final_score <= 0.35:
            signal = "Avoid"
        else:
            signal = "Hold"

        logger.info(
            "Fusion result: ml_prob=%.3f, llm_norm=%.3f → final=%.3f (%s)",
            quant.probability_up,
            llm_norm,
            final_score,
            signal,
        )

        return FusionResult(
            final_score=final_score,
            signal=signal,
            ml_weight=self._ml_weight,
            llm_weight=self._llm_weight,
            ml_normalized=quant.probability_up,
            llm_normalized=llm_norm,
        )


if __name__ == "__main__":
    from src.core.logger import setup_logging

    setup_logging()
    logger.info("Running FusionEngine tests...")

    engine = FusionEngine()

    test_cases: list[dict] = [
        {"ml": 0.9, "llm": 10, "expected": "Strong Buy"},   # Both max bullish
        {"ml": 0.1, "llm": -10, "expected": "Avoid"},        # Both max bearish
        {"ml": 0.5, "llm": 0, "expected": "Hold"},           # Completely neutral
        {"ml": 0.8, "llm": -8, "expected": "Hold"},          # Contradictory
        {"ml": 0.3, "llm": 9, "expected": "Hold"},           # Contradictory
        {"ml": 0.8, "llm": 5, "expected": "Strong Buy"},     # Moderately bullish
    ]

    passed: bool = True
    for idx, case in enumerate(test_cases):
        quant_input = QuantResult(
            probability_up=case["ml"],
            cv_accuracy=0.75,
            model_name="TestModel",
            features_used=["feat_a"],
        )
        sentiment_input = SentimentResult(
            score=case["llm"],
            summary="Test headline summary.",
            headlines=["Test headline"],
            provider_used="TestProvider",
        )

        result: FusionResult = engine.generate_signal(quant_input, sentiment_input)

        if result.signal != case["expected"]:
            logger.error(
                "TEST FAILED on Case %d: Expected %s but got %s. Score=%.3f",
                idx,
                case["expected"],
                result.signal,
                result.final_score,
            )
            passed = False

    if passed:
        logger.info("TEST PASSED: FusionEngine logic verified.")
