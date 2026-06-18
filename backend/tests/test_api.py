import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.core.cache import InMemoryCacheService
from src.domain.auth.service import get_current_user
from src.shared.db_models import User
from main import app, dynamic_rate_limiter
from src.core.dependencies import get_container, ServiceContainer

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_dependencies():
    async def override_rate_limiter():
        pass
    def override_get_current_user():
        return User(id=1, username="testadmin", hashed_password="hashed")
        
    app.dependency_overrides[dynamic_rate_limiter] = override_rate_limiter
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

from src.domain.analysis.schemas import (
    AnalysisResponse,
    FusionResult,
    QuantResult,
    SentimentResult,
    WatchlistResponse,
)

client = TestClient(app)

@pytest.fixture
def mock_container():
    container = MagicMock(spec=ServiceContainer)
    
    # Mock Cache
    container.cache = MagicMock()
    container.cache.get.return_value = None
    
    # Mock Data Engine
    container.data_engine = MagicMock()
    container.data_engine.fetch_and_engineer.return_value = (MagicMock(), MagicMock())
    
    # Mock ML Engine
    container.ml_strategy = MagicMock()
    container.ml_strategy.train_and_predict.return_value = QuantResult(
        probability_up=0.8,
        cv_accuracy=0.75,
        model_name="EnsembleMock",
        features_used=["SMA_20"],
        sub_models=[]
    )
    
    # Mock News & LLM
    container.news_provider = MagicMock()
    container.news_provider.fetch_news.return_value = ["Great news"]
    container.llm_provider = MagicMock()
    container.llm_provider.analyze_sentiment.return_value = SentimentResult(
        score=8, summary="Good", headlines=["Great news"], provider_used="MockLLM"
    )
    
    # Mock Fusion Engine
    container.fusion_engine = MagicMock()
    container.fusion_engine.generate_signal.return_value = FusionResult(
        final_score=0.9, signal="Strong Buy", ml_weight=0.6, llm_weight=0.4, ml_normalized=0.8, llm_normalized=1.0
    )
    
    # Set start time for health check
    import time
    container.start_time = time.time() - 100
    
    return container

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]

def test_health_check(mock_container):
    app.dependency_overrides[get_container] = lambda: mock_container
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    app.dependency_overrides.clear()

def test_analyze_ticker_success(mock_container):
    app.dependency_overrides[get_container] = lambda: mock_container
    response = client.post("/api/analyze", json={"ticker": "AAPL", "period": "1y"})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "quant" in data
    assert "sentiment" in data
    assert "fusion" in data
    assert data["fusion"]["signal"] == "Strong Buy"
    app.dependency_overrides.clear()

def test_analyze_ticker_invalid_format():
    # Regex validation should fail for invalid chars
    response = client.post("/api/analyze", json={"ticker": "AAPL!!!", "period": "1y"})
    assert response.status_code == 422 # FastAPI validation error

def test_analyze_ticker_engine_error(mock_container):
    # Simulate data fetching error
    mock_container.data_engine.fetch_and_engineer.side_effect = ValueError("No data found for TICKER")
    app.dependency_overrides[get_container] = lambda: mock_container
    
    response = client.post("/api/analyze", json={"ticker": "BADTICKER", "period": "1y"})
    assert response.status_code == 400
    assert "No data found" in response.json()["detail"]
    app.dependency_overrides.clear()

def test_watchlist_success(mock_container):
    app.dependency_overrides[get_container] = lambda: mock_container
    response = client.post("/api/watchlist", json={"tickers": ["AAPL", "MSFT"], "period": "1y"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert "errors" in data
    app.dependency_overrides.clear()

def test_watchlist_partial_error(mock_container):
    # Make fetch_and_engineer fail only for MSFT
    def mock_fetch(ticker, period):
        if ticker == "MSFT":
            raise ValueError("No data for MSFT")
        return (MagicMock(), MagicMock())
    
    mock_container.data_engine.fetch_and_engineer.side_effect = mock_fetch
    app.dependency_overrides[get_container] = lambda: mock_container
    
    response = client.post("/api/watchlist", json={"tickers": ["AAPL", "MSFT"], "period": "1y"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["ticker"] == "AAPL"
    assert "MSFT" in data["errors"]
    assert "No data" in data["errors"]["MSFT"]
    app.dependency_overrides.clear()

def test_backtest_success(mock_container):
    mock_container.ml_strategy.run_backtest.return_value = {
        "roi": 0.5,
        "sharpe_ratio": 1.2,
        "max_drawdown": -0.2,
        "buy_hold_roi": 0.4,
        "equity_curve": []
    }
    app.dependency_overrides[get_container] = lambda: mock_container
    response = client.post("/api/backtest", json={"ticker": "AAPL", "period": "5y"})
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["roi"] == 0.5
    app.dependency_overrides.clear()
