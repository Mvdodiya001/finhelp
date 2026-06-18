"""
Application Entry Point — FastAPI server with dependency-injected service container.

Architecture:
    ServiceContainer (composition root)
    ├── DataEngine           → IDataEngine
    ├── RandomForestStrategy → IMLStrategy
    ├── FallbackNewsProvider  → INewsProvider
    ├── LocalLLMProvider      → ILLMProvider
    ├── FusionEngine          → IFusionEngine
    └── InMemoryCacheService  → ICacheService
"""

import os
import time
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.core.database import engine, Base
from src.core.logger import get_logger, setup_logging

from src.domain.auth.router import router as auth
from src.domain.analysis.router import router as analysis
from src.domain.portfolio.router import router as portfolio
from src.domain.market.router import router as market
from src.domain.backtest.router import router as backtest

# ---------------------------------------------------------------------------
# Init Database
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Bootstrap logging before anything else
# ---------------------------------------------------------------------------
setup_logging()
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if USE_REDIS:
        logger.info("Connecting to Redis for distributed rate limiting...")
        try:
            redis_conn = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init(redis_conn)
            logger.info("FastAPILimiter initialized.")
            yield
            await redis_conn.close()
        except Exception as e:
            logger.error("Failed to connect to Redis: %s", e)
            yield
    else:
        logger.info("Redis rate limiting is disabled (USE_REDIS=false).")
        yield

app = FastAPI(title="FinHelp API", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://yourproductiondomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Rate Limiter (Fallback for non-Redis mode) ────────────────────────────
RATE_LIMIT_WINDOW: int = 60
RATE_LIMIT_MAX_REQUESTS: int = 5
ip_request_counts: dict[str, list[float]] = {}

@app.middleware("http")
async def fallback_rate_limit_middleware(request: Request, call_next):
    """Enforce per-IP rate limiting if Redis is not used."""
    if not USE_REDIS and request.url.path == "/api/analyze" and request.method == "POST":
        client_ip: str = request.client.host
        now: float = time.time()

        if client_ip not in ip_request_counts:
            ip_request_counts[client_ip] = []

        ip_request_counts[client_ip] = [
            t for t in ip_request_counts[client_ip] if now - t < RATE_LIMIT_WINDOW
        ]

        if len(ip_request_counts[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning("Fallback Rate limit exceeded for IP %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Security Exception: Rate limit exceeded. Maximum 5 analysis requests per minute."
                },
            )
        ip_request_counts[client_ip].append(now)

    return await call_next(request)

@app.middleware("http")
async def response_timing_middleware(request: Request, call_next):
    """Log request duration and add X-Response-Time header."""
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    response.headers["X-Response-Time"] = f"{duration}ms"
    if request.url.path.startswith("/api/"):
        logger.info("%s %s completed in %sms", request.method, request.url.path, duration)
    return response

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Inject security headers to harden the application."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Mask internal server errors to prevent information leakage."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

async def dynamic_rate_limiter(request: Request, response: Response):
    """Dependency that applies Redis rate limiting if enabled."""
    if USE_REDIS:
        try:
            limiter = RateLimiter(times=RATE_LIMIT_MAX_REQUESTS, seconds=RATE_LIMIT_WINDOW)
            await limiter(request, response)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Redis RateLimiter error: %s", e)
            pass

# ── Include Domain Routers ────────────────────────────────────────────────
app.include_router(auth, tags=["Auth"])
app.include_router(analysis, tags=["Analysis"], dependencies=[Depends(dynamic_rate_limiter)])
app.include_router(portfolio, tags=["Portfolio"])
app.include_router(market, tags=["Market"])
app.include_router(backtest, tags=["Backtest"])

@app.get("/")
def root():
    return {"status": "ok", "message": "API is up and running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}
