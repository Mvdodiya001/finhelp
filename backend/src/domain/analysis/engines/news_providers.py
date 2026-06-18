"""
News Providers — Concrete implementations of the INewsProvider interface.

Implements three providers using the Composite pattern:
  - DDGSProvider: Primary provider using DuckDuckGo search.
  - GoogleRSSProvider: Fallback provider scraping Google News RSS.
  - FallbackNewsProvider: Composite that tries DDGS first, then Google RSS.

Follows:
  - Open/Closed Principle: New providers can be added without modifying existing code.
  - Single Responsibility: Each class handles one news source.
  - Dependency Inversion: All depend on the INewsProvider abstraction.
"""

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from src.core.interfaces import INewsProvider
from src.core.logger import get_logger

logger = get_logger(__name__)


class DDGSProvider(INewsProvider):
    """Fetches recent news headlines using the DuckDuckGo search API.

    Searches for ``{ticker} share price india`` and formats each result
    as ``Title: ... | Summary: ... (Source: ...)``.

    Attributes:
        _provider_name: Identifier string returned for traceability.
    """

    _provider_name: str = "DDGS"

    def fetch_news(self, ticker: str, limit: int = 5) -> list[str]:
        """Fetch up to *limit* news headlines for *ticker* via DuckDuckGo.

        Args:
            ticker: Stock ticker symbol (e.g. ``RELIANCE.NS``).
            limit: Maximum number of headlines to return.

        Returns:
            A list of formatted headline strings. Empty list on failure.
        """
        logger.info("Fetching up to %d news items for %s using DDGS...", limit, ticker)
        try:
            results = DDGS().news(f"{ticker} share price india", max_results=limit)
            if not results:
                logger.warning("DDGS returned no results for %s.", ticker)
                return []

            headlines: list[str] = []
            for item in results:
                title: str = item.get("title", "")
                body: str = item.get("body", "")
                source: str = item.get("source", "")
                text = f"Title: {title} | Summary: {body} (Source: {source})"
                headlines.append(text)

            logger.info("DDGS returned %d headlines for %s.", len(headlines), ticker)
            return headlines

        except Exception as exc:
            logger.error("DDGS error/rate-limit for %s: %s", ticker, exc)
            return []


class GoogleRSSProvider(INewsProvider):
    """Fetches recent news headlines from the Google News RSS feed.

    Uses the endpoint
    ``https://news.google.com/rss/search?q={ticker}+share+price+india&hl=en-IN&gl=IN&ceid=IN:en``
    and parses the XML response with BeautifulSoup.

    Attributes:
        _provider_name: Identifier string returned for traceability.
        _base_url: Google News RSS search URL template.
        _headers: HTTP headers sent with every request.
    """

    _provider_name: str = "GoogleRSS"
    _base_url: str = (
        "https://news.google.com/rss/search?q={query}+share+price+india"
        "&hl=en-IN&gl=IN&ceid=IN:en"
    )
    _headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    def fetch_news(self, ticker: str, limit: int = 5) -> list[str]:
        """Fetch up to *limit* news headlines for *ticker* via Google News RSS.

        Args:
            ticker: Stock ticker symbol (e.g. ``RELIANCE.NS``).
            limit: Maximum number of headlines to return.

        Returns:
            A list of formatted headline strings. Empty list on failure.
        """
        logger.info("Fetching up to %d news items for %s via Google News RSS...", limit, ticker)
        try:
            url: str = self._base_url.format(query=ticker)
            response = requests.get(url, headers=self._headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, features="xml")
            items = soup.find_all("item")

            headlines: list[str] = []
            for item in items[:limit]:
                title: str = item.title.text if item.title else ""
                source: str = item.source.text if item.source else "Google News"
                text = f"Title: {title} | Summary: Breaking news article. (Source: {source})"
                headlines.append(text)

            logger.info("Google RSS returned %d headlines for %s.", len(headlines), ticker)
            return headlines

        except Exception as exc:
            logger.error("Google News RSS error for %s: %s", ticker, exc)
            return []


class FallbackNewsProvider(INewsProvider):
    """Composite news provider implementing the Fallback / Chain-of-Responsibility pattern.

    Tries :class:`DDGSProvider` first; if it raises an exception **or** returns
    an empty list, transparently falls back to :class:`GoogleRSSProvider`.

    Args:
        primary: The preferred news provider (defaults to :class:`DDGSProvider`).
        fallback: The backup news provider (defaults to :class:`GoogleRSSProvider`).

    Attributes:
        _primary: First provider attempted.
        _fallback: Provider used when ``_primary`` fails or returns no results.
    """

    def __init__(
        self,
        primary: INewsProvider | None = None,
        fallback: INewsProvider | None = None,
    ) -> None:
        """Initialize the composite provider with optional overrides.

        Args:
            primary: Primary provider instance. Defaults to ``DDGSProvider()``.
            fallback: Fallback provider instance. Defaults to ``GoogleRSSProvider()``.
        """
        self._primary: INewsProvider = primary or DDGSProvider()
        self._fallback: INewsProvider = fallback or GoogleRSSProvider()

    def fetch_news(self, ticker: str, limit: int = 5) -> list[str]:
        """Fetch headlines, falling back to the secondary provider on failure.

        The method first delegates to ``_primary.fetch_news``. If that call
        raises any exception or returns an empty list, it delegates to
        ``_fallback.fetch_news`` instead.

        Args:
            ticker: Stock ticker symbol (e.g. ``RELIANCE.NS``).
            limit: Maximum number of headlines to return.

        Returns:
            A list of formatted headline strings from whichever provider
            succeeds first (may still be empty if both fail).
        """
        try:
            headlines: list[str] = self._primary.fetch_news(ticker, limit)
            if headlines:
                return headlines
            logger.warning(
                "Primary provider returned empty results for %s; falling back.",
                ticker,
            )
        except Exception as exc:
            logger.warning(
                "Primary provider raised an exception for %s: %s; falling back.",
                ticker,
                exc,
            )

        return self._fallback.fetch_news(ticker, limit)
