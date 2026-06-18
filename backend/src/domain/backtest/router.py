from fastapi import APIRouter, Depends, HTTPException
from src.core.dependencies import ServiceContainer, get_container
from src.domain.backtest.schemas import BacktestRequest, BacktestResponse
from src.shared.db_models import User
from src.domain.auth.service import get_current_user
from src.domain.backtest.service import export_backtest_to_csv, FEATURES
from src.core.logger import get_logger
from starlette.responses import StreamingResponse

logger = get_logger(__name__)

router = APIRouter()

@router.post("/api/backtest", response_model=BacktestResponse)
def run_backtest(
    req: BacktestRequest,
    container: ServiceContainer = Depends(get_container),
    current_user: User = Depends(get_current_user),
):
    try:
        df = container.data_engine.fetch_backtest_data(req.ticker, req.period)
        res = container.ml_strategy.run_backtest(df, FEATURES)
        return BacktestResponse(ticker=req.ticker, strategy_used="Ensemble Strategy (RF + GB)", **res)
    except Exception as exc:
        logger.error("Backtest error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/api/backtest/export")
def export_backtest_csv(
    req: BacktestRequest,
    container: ServiceContainer = Depends(get_container),
    current_user: User = Depends(get_current_user),
):
    try:
        output = export_backtest_to_csv(req, container)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=backtest_{req.ticker}.csv"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
