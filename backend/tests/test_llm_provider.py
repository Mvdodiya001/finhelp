import pytest
from unittest.mock import MagicMock, patch
from src.domain.analysis.engines.llm_provider import LocalLLMProvider
from src.domain.analysis.schemas import SentimentResult

@pytest.fixture
def mocked_llm_provider():
    # We patch the huggingface_hub download and llama_cpp initialization using yield to keep it active
    with patch("src.llm_provider.hf_hub_download") as mock_hf, \
         patch("src.llm_provider.Llama") as mock_llama:
        
        mock_hf.return_value = "/fake/path/to/model.gguf"
        mock_llama_instance = MagicMock()
        mock_llama.return_value = mock_llama_instance
        
        provider = LocalLLMProvider()
        provider._llm = mock_llama_instance
        yield provider

def test_analyze_sentiment_success(mocked_llm_provider):
    # Mock the LLM output to return a valid JSON string
    mocked_llm_provider._llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"score": 8, "summary": "Great earnings report."}'
                }
            }
        ]
    }
    
    headlines = ["Company beats earnings expectations."]
    result = mocked_llm_provider.analyze_sentiment(headlines)
    
    assert isinstance(result, SentimentResult)
    assert result.score == 8
    assert "Great earnings report." in result.summary

def test_analyze_sentiment_json_fallback(mocked_llm_provider):
    # Mock the LLM output to return invalid JSON, should trigger fallback
    mocked_llm_provider._llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "content": 'This is not json!'
                }
            }
        ]
    }
    
    headlines = ["Company beats earnings expectations."]
    result = mocked_llm_provider.analyze_sentiment(headlines)
    
    assert isinstance(result, SentimentResult)
    assert result.score == 0  # Neutral fallback
    assert "Unable to analyze" in result.summary or "Local LLM Error" in result.summary
    
def test_analyze_sentiment_empty_headlines(mocked_llm_provider):
    result = mocked_llm_provider.analyze_sentiment([])
    
    assert isinstance(result, SentimentResult)
    assert result.score == 0
    assert "No news found" in result.summary
