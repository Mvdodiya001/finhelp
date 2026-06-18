from fastapi import APIRouter, Depends, HTTPException
from src.core.dependencies import ServiceContainer, get_container
from src.domain.analysis.schemas import AnalysisResponse, WatchlistRequest, WatchlistResponse, AnalyzeRequest
from src.shared.db_models import User
from src.domain.auth.service import get_current_user
from src.domain.analysis.service import run_analysis_pipeline
from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/api/analyze", response_model=AnalysisResponse)
def analyze_ticker(
    req: AnalyzeRequest,
    container: ServiceContainer = Depends(get_container),
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    cache_key: str = f"{req.ticker}:{req.period}"

    try:
        # Check cache first
        cached = container.cache.get(cache_key)
        if cached is not None:
            logger.info("Returning cached result for %s", cache_key)
            return cached

        logger.info("Running full pipeline for %s (period=%s)", req.ticker, req.period)
        response = run_analysis_pipeline(req.ticker, req.period, container)

        # Store in cache (default 300 s TTL)
        container.cache.set(cache_key, response)
        return response

    except ValueError as exc:
        logger.error("ValueError analysing %s: %s", req.ticker, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unhandled error analysing %s: %s", req.ticker, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/api/watchlist", response_model=WatchlistResponse)
def analyze_watchlist(
    req: WatchlistRequest,
    container: ServiceContainer = Depends(get_container),
    current_user: User = Depends(get_current_user),
) -> WatchlistResponse:
    logger.info("Watchlist request for %d tickers: %s", len(req.tickers), req.tickers)

    results: list[AnalysisResponse] = []
    errors: dict[str, str] = {}

    for ticker in req.tickers:
        try:
            cache_key: str = f"{ticker}:{req.period}"
            cached = container.cache.get(cache_key)
            if cached is not None:
                logger.info("Watchlist cache hit for %s", ticker)
                results.append(cached)
                continue

            response = run_analysis_pipeline(ticker, req.period, container)
            container.cache.set(cache_key, response)
            results.append(response)
        except Exception as exc:
            logger.error("Watchlist error for %s: %s", ticker, exc)
            errors[ticker] = str(exc)

    # Sort by fusion score descending
    results.sort(key=lambda r: r.fusion.final_score, reverse=True)

    return WatchlistResponse(results=results, errors=errors)
