"""
ML Engine — Multi-Model Ensemble Pipeline for next-bar direction prediction.

Implements the IMLStrategy interface using the Strategy Pattern.
Four concrete strategies are available:

    * RandomForestStrategy  — sklearn RandomForestClassifier (feature importance)
    * GradientBoostStrategy — sklearn GradientBoostingClassifier (non-linear interactions)
    * LSTMStrategy          — PyTorch LSTM (temporal/sequential patterns)
    * EnsembleStrategy      — Weighted ensemble of multiple IMLStrategy instances (Composite Pattern)

The EnsembleStrategy is the default — it runs all three models and combines
their predictions with configurable weights. This multi-model approach:
    1. LSTM captures sequential memory patterns in price history
    2. RandomForest captures feature-level importance and splits
    3. GradientBoosting captures non-linear interactions between features
    4. The ensemble reduces variance and improves generalization
"""

from typing import List, Tuple

import numpy as np
import pandas as pd
import os
import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler

MODEL_DIR = "/home/shiv/stock_predictor/backend/models"
os.makedirs(MODEL_DIR, exist_ok=True)

from src.core.interfaces import IMLStrategy
from src.domain.analysis.schemas import QuantResult, SubModelResult
from src.core.logger import get_logger

logger = get_logger(__name__)

_N_SPLITS: int = 5
_RANDOM_STATE: int = 42


# ---------------------------------------------------------------------------
# Strategy 1: Random Forest (feature importance)
# ---------------------------------------------------------------------------
class RandomForestStrategy(IMLStrategy):
    """Next-bar direction predictor using a Random Forest ensemble.

    Captures feature-level importance — which technical indicators
    (SMA, RSI, etc.) are most predictive of next-bar direction.
    """

    _MODEL_NAME: str = "RandomForest"
    _loaded_models = {}

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        random_state: int = _RANDOM_STATE,
    ) -> None:
        self._n_estimators = n_estimators
        self._max_depth = max_depth
        self._random_state = random_state

    def get_name(self) -> str:
        return self._MODEL_NAME

    def train_and_predict(
        self,
        ticker: str,
        train_df: pd.DataFrame,
        latest_features: pd.DataFrame,
        features: list[str],
    ) -> QuantResult:
        logger.info("[%s] Training with %d features", self._MODEL_NAME, len(features))

        X = train_df[features]
        y = train_df["Target"]

        if ticker in self._loaded_models:
            model, cv_accuracy = self._loaded_models[ticker]
            logger.info("[%s] Using in-memory model for %s", self._MODEL_NAME, ticker)
        else:
            model_path = os.path.join(MODEL_DIR, f"{ticker}_{self._MODEL_NAME}.joblib")
            if os.path.exists(model_path):
                logger.info("[%s] Loading cached model for %s", self._MODEL_NAME, ticker)
                model, cv_accuracy = joblib.load(model_path)
            else:
                model = RandomForestClassifier(
                    n_estimators=self._n_estimators,
                    max_depth=self._max_depth,
                    random_state=self._random_state,
                    class_weight="balanced",
                )
                cv_accuracy = self._cross_validate(model, X, y)
                model.fit(X, y)
                joblib.dump((model, cv_accuracy), model_path)
            self._loaded_models[ticker] = (model, cv_accuracy)
        prob_up = float(model.predict_proba(latest_features[features])[0][1])

        # Feature importances
        importances = dict(zip(features, model.feature_importances_.tolist()))

        # Confidence interval from individual tree predictions
        tree_probs = np.array([
            est.predict_proba(latest_features[features].values)[0][1]
            for est in model.estimators_
        ])
        std = float(np.std(tree_probs))
        ci_low = max(0.0, prob_up - 1.96 * std)
        ci_high = min(1.0, prob_up + 1.96 * std)

        logger.info("[%s] P(Up)=%.4f, CV=%.4f", self._MODEL_NAME, prob_up, cv_accuracy)

        return QuantResult(
            probability_up=prob_up,
            cv_accuracy=cv_accuracy,
            model_name=self._MODEL_NAME,
            features_used=list(features),
            feature_importances=importances,
            confidence_interval=[ci_low, ci_high],
        )

    def _cross_validate(self, model, X: pd.DataFrame, y: pd.Series) -> float:
        """Expanding-window walk-forward validation."""
        n = len(X)
        step_size = max(1, n // 10)
        start = n // 2
        accs: List[float] = []
        while start + step_size <= n:
            X_tr, y_tr = X.iloc[:start], y.iloc[:start]
            X_te, y_te = X.iloc[start:start + step_size], y.iloc[start:start + step_size]
            model.fit(X_tr, y_tr)
            accs.append(accuracy_score(y_te, model.predict(X_te)))
            start += step_size
        return float(np.mean(accs)) if accs else 0.5


# ---------------------------------------------------------------------------
# Strategy 2: Gradient Boosting (non-linear interactions)
# ---------------------------------------------------------------------------
class GradientBoostStrategy(IMLStrategy):
    """Next-bar direction predictor using Gradient Boosting.

    Captures non-linear feature interactions via sequential boosting.
    """

    _MODEL_NAME: str = "GradientBoost"
    _loaded_models = {}

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 3,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        random_state: int = _RANDOM_STATE,
    ) -> None:
        self._n_estimators = n_estimators
        self._max_depth = max_depth
        self._learning_rate = learning_rate
        self._subsample = subsample
        self._random_state = random_state

    def get_name(self) -> str:
        return self._MODEL_NAME

    def train_and_predict(
        self,
        ticker: str,
        train_df: pd.DataFrame,
        latest_features: pd.DataFrame,
        features: list[str],
    ) -> QuantResult:
        logger.info("[%s] Training with %d features", self._MODEL_NAME, len(features))

        X = train_df[features]
        y = train_df["Target"]

        if ticker in self._loaded_models:
            model, cv_accuracy = self._loaded_models[ticker]
            logger.info("[%s] Using in-memory model for %s", self._MODEL_NAME, ticker)
        else:
            model_path = os.path.join(MODEL_DIR, f"{ticker}_{self._MODEL_NAME}.joblib")
            if os.path.exists(model_path):
                logger.info("[%s] Loading cached model for %s", self._MODEL_NAME, ticker)
                model, cv_accuracy = joblib.load(model_path)
            else:
                model = GradientBoostingClassifier(
                    n_estimators=self._n_estimators,
                    max_depth=self._max_depth,
                    learning_rate=self._learning_rate,
                    subsample=self._subsample,
                    random_state=self._random_state,
                )
                cv_accuracy = self._cross_validate(model, X, y)
                model.fit(X, y)
                joblib.dump((model, cv_accuracy), model_path)
            self._loaded_models[ticker] = (model, cv_accuracy)
        prob_up = float(model.predict_proba(latest_features[features])[0][1])

        # Feature importances
        importances = dict(zip(features, model.feature_importances_.tolist()))

        # Confidence interval from staged predictions
        staged_probs = np.array([
            proba[0][1] for proba in model.staged_predict_proba(latest_features[features])
        ])
        std = float(np.std(staged_probs))
        ci_low = max(0.0, prob_up - 1.96 * std)
        ci_high = min(1.0, prob_up + 1.96 * std)

        logger.info("[%s] P(Up)=%.4f, CV=%.4f", self._MODEL_NAME, prob_up, cv_accuracy)

        return QuantResult(
            probability_up=prob_up,
            cv_accuracy=cv_accuracy,
            model_name=self._MODEL_NAME,
            features_used=list(features),
            feature_importances=importances,
            confidence_interval=[ci_low, ci_high],
        )

    def _cross_validate(self, model, X: pd.DataFrame, y: pd.Series) -> float:
        """Expanding-window walk-forward validation."""
        n = len(X)
        step_size = max(1, n // 10)
        start = n // 2
        accs: List[float] = []
        while start + step_size <= n:
            X_tr, y_tr = X.iloc[:start], y.iloc[:start]
            X_te, y_te = X.iloc[start:start + step_size], y.iloc[start:start + step_size]
            model.fit(X_tr, y_tr)
            accs.append(accuracy_score(y_te, model.predict(X_te)))
            start += step_size
        return float(np.mean(accs)) if accs else 0.5


# ---------------------------------------------------------------------------
# Strategy 3: LSTM (temporal/sequential patterns)
# ---------------------------------------------------------------------------
class LSTMStrategy(IMLStrategy):
    """Next-bar direction predictor using a PyTorch LSTM neural network.

    LSTM (Long Short-Term Memory) captures **sequential temporal patterns**
    in the price history that tree-based models cannot detect — such as
    momentum shifts, mean-reversion cycles, and multi-day trend structures.

    Architecture:
        Input (window_size × n_features)
          → LSTM(hidden_size=64, num_layers=2, dropout=0.2)
          → Fully Connected(64 → 1)
          → Sigmoid → P(Up)

    Training:
        - Creates sliding windows of `window_size` consecutive bars
        - Normalises features with MinMaxScaler (fit on training data only)
        - Uses walk-forward TimeSeriesSplit for unbiased CV accuracy
        - Trains with BCELoss (Binary Cross-Entropy) + Adam optimizer
    """

    _MODEL_NAME: str = "LSTM"
    _loaded_models = {}

    def __init__(
        self,
        window_size: int = 30,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        epochs: int = 50,
        learning_rate: float = 0.001,
        batch_size: int = 32,
    ) -> None:
        self._window_size = window_size
        self._hidden_size = hidden_size
        self._num_layers = num_layers
        self._dropout = dropout
        self._epochs = epochs
        self._lr = learning_rate
        self._batch_size = batch_size

    def get_name(self) -> str:
        return self._MODEL_NAME

    def train_and_predict(
        self,
        ticker: str,
        train_df: pd.DataFrame,
        latest_features: pd.DataFrame,
        features: list[str],
    ) -> QuantResult:
        """Train LSTM on windowed sequences and predict next bar."""
        import torch
        import torch.nn as nn

        logger.info(
            "[%s] Training with window=%d, hidden=%d, layers=%d, epochs=%d",
            self._MODEL_NAME, self._window_size, self._hidden_size,
            self._num_layers, self._epochs,
        )

        # ── 1. Prepare full feature matrix ──────────────────────────────
        full_df = pd.concat([train_df, latest_features], axis=0)
        feature_data = full_df[features].values
        targets = full_df["Target"].values  # last row is NaN

        # ── 2. Scale features (fit only on training data) ───────────────
        scaler = MinMaxScaler()
        n_train = len(train_df)
        scaler.fit(feature_data[:n_train])
        scaled_data = scaler.transform(feature_data)

        # ── 3. Create sliding windows ───────────────────────────────────
        X_windows, y_windows = self._create_windows(
            scaled_data[:n_train], targets[:n_train], self._window_size
        )

        if len(X_windows) < 20:
            logger.warning("[%s] Insufficient data for LSTM (%d windows)", self._MODEL_NAME, len(X_windows))
            return QuantResult(
                probability_up=0.5, cv_accuracy=0.5,
                model_name=self._MODEL_NAME, features_used=list(features),
                feature_importances={},
                confidence_interval=[0.4, 0.6],
            )

        model_path = os.path.join(MODEL_DIR, f"{ticker}_{self._MODEL_NAME}.pt")
        meta_path = os.path.join(MODEL_DIR, f"{ticker}_{self._MODEL_NAME}_meta.joblib")
        
        if ticker in self._loaded_models:
            model, cv_accuracy, scaler = self._loaded_models[ticker]
            logger.info("[%s] Using in-memory model for %s", self._MODEL_NAME, ticker)
            scaled_data = scaler.transform(feature_data)
        elif os.path.exists(model_path) and os.path.exists(meta_path):
            logger.info("[%s] Loading cached model for %s", self._MODEL_NAME, ticker)
            model = self._build_model(len(features), torch, nn)
            model.load_state_dict(torch.load(model_path))
            cv_accuracy, scaler = joblib.load(meta_path)
            scaled_data = scaler.transform(feature_data)
            self._loaded_models[ticker] = (model, cv_accuracy, scaler)
        else:
            # ── 4. Walk-forward CV to compute unbiased accuracy ─────────────
            cv_accuracy = self._cross_validate_lstm(
                X_windows, y_windows, len(features), torch, nn
            )

            # ── 5. Train final model on all data ────────────────────────────
            model = self._build_model(len(features), torch, nn)
            self._train_model(model, X_windows, y_windows, torch, nn)
            
            torch.save(model.state_dict(), model_path)
            joblib.dump((cv_accuracy, scaler), meta_path)
            scaled_data = scaler.transform(feature_data)
            self._loaded_models[ticker] = (model, cv_accuracy, scaler)

        # ── 6. Predict using the latest window ──────────────────────────
        latest_window = scaled_data[-self._window_size:]  # Last window_size bars
        X_pred = torch.FloatTensor(latest_window).unsqueeze(0)  # (1, window, features)

        model.eval()
        with torch.no_grad():
            prob_up = float(model(X_pred).item())

        prob_up = max(0.0, min(1.0, prob_up))

        logger.info("[%s] P(Up)=%.4f, CV=%.4f", self._MODEL_NAME, prob_up, cv_accuracy)

        return QuantResult(
            probability_up=prob_up,
            cv_accuracy=cv_accuracy,
            model_name=self._MODEL_NAME,
            features_used=list(features),
            feature_importances={},
            confidence_interval=[max(0.0, prob_up - 0.1), min(1.0, prob_up + 0.1)],
        )

    @staticmethod
    def _create_windows(
        data: np.ndarray, targets: np.ndarray, window_size: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sliding windows from sequential data."""
        X, y = [], []
        for i in range(window_size, len(data)):
            X.append(data[i - window_size : i])
            y.append(targets[i])
        return np.array(X), np.array(y)

    def _build_model(self, n_features: int, torch, nn):
        """Construct the LSTM network."""

        class _LSTMNet(nn.Module):
            def __init__(self_, input_size, hidden_size, num_layers, dropout):
                super().__init__()
                self_.lstm = nn.LSTM(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    dropout=dropout if num_layers > 1 else 0.0,
                    batch_first=True,
                )
                self_.fc = nn.Linear(hidden_size, 1)
                self_.sigmoid = nn.Sigmoid()

            def forward(self_, x):
                lstm_out, _ = self_.lstm(x)
                last_hidden = lstm_out[:, -1, :]  # Take last timestep
                return self_.sigmoid(self_.fc(last_hidden)).squeeze(-1)

        return _LSTMNet(n_features, self._hidden_size, self._num_layers, self._dropout)

    def _train_model(self, model, X: np.ndarray, y: np.ndarray, torch, nn) -> None:
        """Train the LSTM model."""
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y)

        optimizer = torch.optim.Adam(model.parameters(), lr=self._lr)
        criterion = nn.BCELoss()

        model.train()
        n_samples = len(X_tensor)

        for epoch in range(self._epochs):
            # Mini-batch training
            indices = torch.randperm(n_samples)
            total_loss = 0.0
            n_batches = 0

            for start in range(0, n_samples, self._batch_size):
                end = min(start + self._batch_size, n_samples)
                batch_idx = indices[start:end]
                X_batch = X_tensor[batch_idx]
                y_batch = y_tensor[batch_idx]

                optimizer.zero_grad()
                output = model(X_batch)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                n_batches += 1

            if (epoch + 1) % 25 == 0:
                logger.debug(
                    "[LSTM] Epoch %d/%d — Loss: %.4f",
                    epoch + 1, self._epochs, total_loss / max(n_batches, 1),
                )

    def _cross_validate_lstm(
        self, X: np.ndarray, y: np.ndarray, n_features: int, torch, nn
    ) -> float:
        """Walk-forward CV for LSTM."""
        tscv = TimeSeriesSplit(n_splits=3)  # Fewer splits for LSTM (expensive)
        accs: List[float] = []

        for tr_idx, te_idx in tscv.split(X):
            model = self._build_model(n_features, torch, nn)
            self._train_model(model, X[tr_idx], y[tr_idx], torch, nn)

            model.eval()
            with torch.no_grad():
                X_test = torch.FloatTensor(X[te_idx])
                preds = model(X_test).numpy()
                preds_binary = (preds > 0.5).astype(int)
                accs.append(accuracy_score(y[te_idx].astype(int), preds_binary))

        return float(np.mean(accs)) if accs else 0.5


# ---------------------------------------------------------------------------
# Strategy 4: Ensemble (Composite Pattern — combines multiple strategies)
# ---------------------------------------------------------------------------
class EnsembleStrategy(IMLStrategy):
    """Multi-model ensemble that combines LSTM + RandomForest + GradientBoost.

    This is the Composite Pattern applied to ML — the ensemble itself implements
    IMLStrategy, so it is fully substitutable anywhere a single strategy is used.

    Architecture:
        ┌────────────────────────────────────────┐
        │          EnsembleStrategy               │
        │                                         │
        │  ┌──────────┐  LSTM captures temporal   │
        │  │  LSTM    │  sequential patterns       │
        │  │  (40%)   │  (momentum, mean-reversion)│
        │  └────┬─────┘                            │
        │       │                                  │
        │  ┌────┴─────┐  RF captures which         │
        │  │  RF      │  features matter most      │
        │  │  (30%)   │  (SMA crossovers, RSI)     │
        │  └────┬─────┘                            │
        │       │                                  │
        │  ┌────┴─────┐  GB captures non-linear    │
        │  │  GB      │  feature interactions      │
        │  │  (30%)   │  (RSI × SMA patterns)      │
        │  └────┬─────┘                            │
        │       │                                  │
        │       ▼                                  │
        │  Weighted Average → P(Up)                │
        └────────────────────────────────────────┘

    Why this combination works:
        - LSTM learns from the *sequence* of recent bars (last 30 days)
        - RF/GB learn from *cross-sectional* feature values (today's SMA, RSI)
        - They capture fundamentally different signal types → low correlation
        - Ensemble averaging reduces variance → more stable predictions
    """

    _MODEL_NAME: str = "Ensemble(LSTM+RF+GB)"

    def __init__(
        self,
        strategies: list[Tuple[IMLStrategy, float]] | None = None,
    ) -> None:
        """Initialize with a list of (strategy, weight) tuples.

        Args:
            strategies: List of (IMLStrategy, weight) pairs. Weights should
                       sum to 1.0. Defaults to LSTM(0.4) + RF(0.3) + GB(0.3).
        """
        if strategies is None:
            self._strategies: list[Tuple[IMLStrategy, float]] = [
                (LSTMStrategy(), 0.4),
                (RandomForestStrategy(), 0.3),
                (GradientBoostStrategy(), 0.3),
            ]
        else:
            self._strategies = strategies

        total_weight = sum(w for _, w in self._strategies)
        if abs(total_weight - 1.0) > 0.01:
            logger.warning("Ensemble weights sum to %.2f, normalizing", total_weight)
            self._strategies = [
                (s, w / total_weight) for s, w in self._strategies
            ]

    def get_name(self) -> str:
        return self._MODEL_NAME

    def train_and_predict(
        self,
        ticker: str,
        train_df: pd.DataFrame,
        latest_features: pd.DataFrame,
        features: list[str],
    ) -> QuantResult:
        """Run all sub-strategies and combine with weighted average."""
        logger.info(
            "[%s] Running %d sub-models: %s",
            self._MODEL_NAME,
            len(self._strategies),
            [(s.get_name(), f"{w:.0%}") for s, w in self._strategies],
        )

        sub_results: list[SubModelResult] = []
        sub_probs: list[float] = []
        weighted_prob = 0.0
        weighted_cv = 0.0
        all_features: set[str] = set()
        all_importances: list[dict[str, float]] = []

        for strategy, weight in self._strategies:
            try:
                result = strategy.train_and_predict(ticker, train_df, latest_features, features)
                sub_results.append(SubModelResult(
                    model_name=result.model_name,
                    probability_up=result.probability_up,
                    weight=weight,
                ))
                weighted_prob += result.probability_up * weight
                weighted_cv += result.cv_accuracy * weight
                all_features.update(result.features_used)
                sub_probs.append(result.probability_up)
                if result.feature_importances:
                    all_importances.append(result.feature_importances)

                logger.info(
                    "[%s] %s → P(Up)=%.4f (weight=%.0f%%)",
                    self._MODEL_NAME, result.model_name,
                    result.probability_up, weight * 100,
                )

            except Exception as exc:
                logger.error(
                    "[%s] %s failed: %s — using neutral P(Up)=0.5",
                    self._MODEL_NAME, strategy.get_name(), exc,
                )
                sub_results.append(SubModelResult(
                    model_name=strategy.get_name(),
                    probability_up=0.5,
                    weight=weight,
                ))
                weighted_prob += 0.5 * weight
                weighted_cv += 0.5 * weight
                sub_probs.append(0.5)

        weighted_prob = max(0.0, min(1.0, weighted_prob))
        weighted_cv = max(0.0, min(1.0, weighted_cv))

        # Merge feature importances by averaging across sub-models
        merged_importances: dict[str, float] = {}
        if all_importances:
            all_keys = set().union(*all_importances)
            for key in all_keys:
                vals = [imp[key] for imp in all_importances if key in imp]
                merged_importances[key] = sum(vals) / len(vals)

        # Confidence interval from the spread of sub-model predictions
        ci_low = float(min(sub_probs)) if sub_probs else 0.0
        ci_high = float(max(sub_probs)) if sub_probs else 1.0

        logger.info(
            "[%s] Ensemble P(Up)=%.4f, Ensemble CV=%.4f",
            self._MODEL_NAME, weighted_prob, weighted_cv,
        )

        return QuantResult(
            probability_up=weighted_prob,
            cv_accuracy=weighted_cv,
            model_name=self._MODEL_NAME,
            features_used=sorted(all_features),
            feature_importances=merged_importances,
            confidence_interval=[ci_low, ci_high],
            sub_models=sub_results,
        )

    def run_backtest(self, df: pd.DataFrame, features: list[str], commission_pct: float = 0.001) -> dict:
        """Run a vectorized historical backtest with transaction cost modeling."""
        split_idx = int(len(df) * 0.6)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df[features]
        y_train = train_df["Target"]
        X_test = test_df[features]
        
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
        
        rf.fit(X_train, y_train)
        gb.fit(X_train, y_train)
        
        rf_preds = rf.predict_proba(X_test)[:, 1]
        gb_preds = gb.predict_proba(X_test)[:, 1]
        
        ensemble_preds = (rf_preds + gb_preds) / 2.0
        signals = (ensemble_preds > 0.5).astype(int)
        
        test_returns = test_df['Close'].pct_change().fillna(0)
        
        # Detect position changes for transaction cost modeling
        signal_changes = np.diff(signals, prepend=0)
        trades_mask = signal_changes != 0  # True on days where we enter/exit
        transaction_costs = np.where(trades_mask, commission_pct, 0.0)
        
        # Strategy returns with costs
        strategy_returns = signals[:-1] * test_returns.values[1:]
        strategy_returns = np.insert(strategy_returns, 0, 0)
        strategy_returns = strategy_returns - transaction_costs  # Deduct costs
        
        strategy_returns_series = pd.Series(strategy_returns, index=test_df.index)
        
        buy_hold_cum = (1 + test_returns).cumprod()
        strategy_cum = (1 + strategy_returns_series).cumprod()
        
        roi = float(strategy_cum.iloc[-1] - 1)
        buy_hold_roi = float(buy_hold_cum.iloc[-1] - 1)
        
        mean_ret = np.mean(strategy_returns)
        std_ret = np.std(strategy_returns)
        sharpe = float((mean_ret / std_ret) * np.sqrt(252)) if std_ret > 0 else 0.0
        
        rolling_max = strategy_cum.cummax()
        drawdown = (strategy_cum - rolling_max) / rolling_max
        max_dd = float(drawdown.min())
        
        # ── Trade-level statistics ──
        # Find trade segments: contiguous blocks where signal=1
        trade_returns_list = []
        trades_log = []
        in_trade = False
        current_trade_return = 0.0
        entry_price = 0.0
        entry_date = None
        
        prices = test_df['Close'].values
        dates = test_df.index
        
        for i in range(len(signals)):
            if signals[i] == 1:
                if not in_trade:
                    in_trade = True
                    entry_price = prices[i]
                    entry_date = dates[i].strftime("%Y-%m-%d")
                    trades_log.append({
                        "date": entry_date,
                        "action": "BUY",
                        "price": float(entry_price),
                        "profit": 0.0
                    })
                if i < len(strategy_returns):
                    current_trade_return += strategy_returns[i]
            else:
                if in_trade:
                    trade_returns_list.append(current_trade_return)
                    exit_price = prices[i]
                    trades_log.append({
                        "date": dates[i].strftime("%Y-%m-%d"),
                        "action": "SELL",
                        "price": float(exit_price),
                        "profit": float(current_trade_return)
                    })
                    current_trade_return = 0.0
                    in_trade = False
                    
        if in_trade:
            trade_returns_list.append(current_trade_return)
            trades_log.append({
                "date": dates[-1].strftime("%Y-%m-%d"),
                "action": "SELL (EOP)",
                "price": float(prices[-1]),
                "profit": float(current_trade_return)
            })
        
        total_trades = len(trade_returns_list)
        winning_trades = sum(1 for r in trade_returns_list if r > 0)
        losing_trades = sum(1 for r in trade_returns_list if r <= 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        avg_win = np.mean([r for r in trade_returns_list if r > 0]) if winning_trades > 0 else 0.0
        avg_loss = abs(np.mean([r for r in trade_returns_list if r <= 0])) if losing_trades > 0 else 0.0
        profit_factor = float(avg_win / avg_loss) if avg_loss > 0 else float('inf') if avg_win > 0 else 0.0
        # Cap profit factor for JSON serialization
        if profit_factor == float('inf'):
            profit_factor = 99.99
        
        total_commission = float(np.sum(transaction_costs))
        
        equity_curve = []
        for i, date in enumerate(test_df.index):
            equity_curve.append({
                "date": date.strftime("%Y-%m-%d"),
                "strategy_value": float(strategy_cum.iloc[i]),
                "buy_hold_value": float(buy_hold_cum.iloc[i])
            })
            
        return {
            "roi": roi,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "buy_hold_roi": buy_hold_roi,
            "equity_curve": equity_curve,
            "trades": trades_log,
            "total_trades": total_trades,
            "win_rate": float(win_rate),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "profit_factor": float(profit_factor),
            "total_commission": total_commission,
        }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from src.domain.analysis.engines.data_engine import DataEngine
    from src.core.logger import setup_logging

    setup_logging()

    FEATURES = ["SMA_20", "SMA_50", "EMA_20", "RSI_14", "Daily_Log_Return"]

    try:
        engine = DataEngine()
        train_df, latest = engine.fetch_and_engineer("RELIANCE.NS", period="2y")

        # Test individual strategies
        for strategy in [RandomForestStrategy(), GradientBoostStrategy(), LSTMStrategy()]:
            result = strategy.train_and_predict("RELIANCE.NS", train_df, latest, FEATURES)
            logger.info("[%s] P(Up)=%.4f, CV=%.4f", result.model_name, result.probability_up, result.cv_accuracy)

        # Test ensemble
        ensemble = EnsembleStrategy()
        result = ensemble.train_and_predict("RELIANCE.NS", train_df, latest, FEATURES)
        logger.info("[Ensemble] P(Up)=%.4f, CV=%.4f", result.probability_up, result.cv_accuracy)
        for sub in result.sub_models:
            logger.info("  └─ %s: P(Up)=%.4f (weight=%.0f%%)", sub.model_name, sub.probability_up, sub.weight * 100)

    except Exception as exc:
        logger.error("TEST FAILED: %s", exc, exc_info=True)
