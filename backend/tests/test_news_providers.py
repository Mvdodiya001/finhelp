"""Tests for news providers — DDGS, GoogleRSS, and FallbackNewsProvider."""
import pytest
from unittest.mock import patch, MagicMock
from src.domain.analysis.engines.news_providers import DDGSProvider, GoogleRSSProvider, FallbackNewsProvider


class TestDDGSProvider:
    @patch("src.news_providers.DDGS")
    def test_returns_headlines(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.news.return_value = [
            {"title": "Stock rises", "body": "Good earnings", "source": "Reuters"}
        ]
        mock_ddgs_cls.return_value = mock_instance

        provider = DDGSProvider()
        result = provider.fetch_news("RELIANCE.NS", limit=1)

        assert len(result) == 1
        assert "Stock rises" in result[0]

    @patch("src.news_providers.DDGS")
    def test_empty_results(self, mock_ddgs_cls):
        mock_instance = MagicMock()
        mock_instance.news.return_value = []
        mock_ddgs_cls.return_value = mock_instance

        provider = DDGSProvider()
        result = provider.fetch_news("FAKE", limit=5)
        assert result == []

    @patch("src.news_providers.DDGS")
    def test_exception_returns_empty(self, mock_ddgs_cls):
        mock_ddgs_cls.side_effect = Exception("Rate limited")

        provider = DDGSProvider()
        result = provider.fetch_news("RELIANCE.NS")
        assert result == []


class TestGoogleRSSProvider:
    @patch("src.news_providers.requests.get")
    def test_returns_headlines(self, mock_get):
        xml_content = """<?xml version="1.0"?>
        <rss><channel>
            <item><title>Markets rally</title><source>ET</source></item>
        </channel></rss>"""
        mock_response = MagicMock()
        mock_response.content = xml_content.encode()
        mock_get.return_value = mock_response

        provider = GoogleRSSProvider()
        result = provider.fetch_news("TCS.NS", limit=1)
        assert len(result) == 1
        assert "Markets rally" in result[0]


class TestFallbackNewsProvider:
    def test_uses_primary_when_available(self):
        primary = MagicMock()
        primary.fetch_news.return_value = ["Headline from primary"]
        fallback = MagicMock()

        provider = FallbackNewsProvider(primary=primary, fallback=fallback)
        result = provider.fetch_news("X", limit=1)

        assert result == ["Headline from primary"]
        fallback.fetch_news.assert_not_called()

    def test_falls_back_on_empty(self):
        primary = MagicMock()
        primary.fetch_news.return_value = []
        fallback = MagicMock()
        fallback.fetch_news.return_value = ["Headline from fallback"]

        provider = FallbackNewsProvider(primary=primary, fallback=fallback)
        result = provider.fetch_news("X", limit=1)

        assert result == ["Headline from fallback"]

    def test_falls_back_on_exception(self):
        primary = MagicMock()
        primary.fetch_news.side_effect = Exception("Rate limited")
        fallback = MagicMock()
        fallback.fetch_news.return_value = ["Fallback headline"]

        provider = FallbackNewsProvider(primary=primary, fallback=fallback)
        result = provider.fetch_news("X")

        assert result == ["Fallback headline"]
