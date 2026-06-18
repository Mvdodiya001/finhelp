"""Tests for the ML Engine — all 4 strategies including LSTM and Ensemble."""
import pytest
import numpy as np
from src.domain.analysis.engines.ml_engine import RandomForestStrategy, GradientBoostStrategy, LSTMStrategy, EnsembleStrategy
from src.domain.analysis.schemas import QuantResult
from tests.conftest import FEATURES


class TestRandomForestStrategy:
    def test_get_name(self):
        assert RandomForestStrategy().get_name() == "RandomForest"

    def test_returns_quant_result(self, sample_training_data, sample_latest_features):
        result = RandomForestStrategy().train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
        assert isinstance(result, QuantResult)
        assert 0.0 <= result.probability_up <= 1.0
        assert result.model_name == "RandomForest"


class TestGradientBoostStrategy:
    def test_get_name(self):
        assert GradientBoostStrategy().get_name() == "GradientBoost"

    def test_returns_quant_result(self, sample_training_data, sample_latest_features):
        result = GradientBoostStrategy().train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
        assert isinstance(result, QuantResult)
        assert 0.0 <= result.probability_up <= 1.0


class TestLSTMStrategy:
    def test_get_name(self):
        assert LSTMStrategy().get_name() == "LSTM"

    def test_returns_quant_result(self, sample_training_data, sample_latest_features):
        """LSTM should train and return valid QuantResult with synthetic data."""
        strategy = LSTMStrategy(window_size=10, epochs=5)  # Fast for testing
        result = strategy.train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
        assert isinstance(result, QuantResult)
        assert 0.0 <= result.probability_up <= 1.0
        assert result.model_name == "LSTM"

    def test_insufficient_data_returns_neutral(self):
        """LSTM should return 0.5 if there's not enough data for windowing."""
        import pandas as pd
        # Create tiny DF with only 10 rows — not enough for window_size=30
        tiny_df = pd.DataFrame({
            "Close": [100] * 10,
            "SMA_20": [100] * 10,
            "SMA_50": [100] * 10,
            "EMA_20": [100] * 10,
            "RSI_14": [50] * 10,
            "Daily_Log_Return": [0.0] * 10,
            "Target": [1] * 10,
        })
        latest = tiny_df.iloc[-1:].copy()

        strategy = LSTMStrategy(window_size=30)
        result = strategy.train_and_predict("TEST", tiny_df, latest, FEATURES)
        assert result.probability_up == 0.5  # Neutral fallback


class TestEnsembleStrategy:
    def test_get_name(self):
        assert "Ensemble" in EnsembleStrategy().get_name()

    def test_returns_quant_result_with_sub_models(self, sample_training_data, sample_latest_features):
        """Ensemble should return results with sub-model breakdown."""
        from src.domain.analysis.engines.ml_engine import RandomForestStrategy, GradientBoostStrategy
        ensemble = EnsembleStrategy(strategies=[
            (RandomForestStrategy(), 0.5),
            (GradientBoostStrategy(), 0.5),
        ])
        result = ensemble.train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
        assert isinstance(result, QuantResult)
        assert 0.0 <= result.probability_up <= 1.0
        assert len(result.sub_models) == 2
        assert result.sub_models[0].model_name == "RandomForest"
        assert result.sub_models[1].model_name == "GradientBoost"

    def test_weights_sum_to_one(self):
        """Ensemble should normalize weights if they don't sum to 1."""
        ensemble = EnsembleStrategy(strategies=[
            (RandomForestStrategy(), 2.0),
            (GradientBoostStrategy(), 3.0),
        ])
        total = sum(w for _, w in ensemble._strategies)
        assert abs(total - 1.0) < 0.01

    def test_sub_model_weights_visible(self, sample_training_data, sample_latest_features):
        """Each sub-model should report its weight in the result."""
        ensemble = EnsembleStrategy(strategies=[
            (RandomForestStrategy(), 0.7),
            (GradientBoostStrategy(), 0.3),
        ])
        result = ensemble.train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
        assert result.sub_models[0].weight == pytest.approx(0.7, abs=0.01)
        assert result.sub_models[1].weight == pytest.approx(0.3, abs=0.01)


class TestStrategyInterchangeability:
    """All strategies implement the same IMLStrategy interface."""

    def test_all_produce_valid_output(self, sample_training_data, sample_latest_features):
        strategies = [
            RandomForestStrategy(),
            GradientBoostStrategy(),
            LSTMStrategy(window_size=10, epochs=5),
        ]
        for strategy in strategies:
            result = strategy.train_and_predict("TEST", sample_training_data, sample_latest_features, FEATURES)
            assert isinstance(result, QuantResult), f"{strategy.get_name()} failed"
            assert 0.0 <= result.probability_up <= 1.0
