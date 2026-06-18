import csv
import io
from fastapi import HTTPException
from src.core.dependencies import ServiceContainer
from src.domain.backtest.schemas import BacktestRequest
from src.core.logger import get_logger

logger = get_logger(__name__)

FEATURES: list[str] = [
    "SMA_20",
    "SMA_50",
    "EMA_20",
    "RSI_14",
    "Daily_Log_Return",
]

def export_backtest_to_csv(
    req: BacktestRequest,
    container: ServiceContainer,
) -> io.StringIO:
    """Execute backtest and export results as a CSV buffer."""
    try:
        df = container.data_engine.fetch_backtest_data(req.ticker, req.period)
        res = container.ml_strategy.run_backtest(df, FEATURES)

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Summary header
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Ticker", req.ticker])
        writer.writerow(["Strategy ROI", f"{res['roi']*100:.2f}%"])
        writer.writerow(["Buy & Hold ROI", f"{res['buy_hold_roi']*100:.2f}%"])
        writer.writerow(["Sharpe Ratio", f"{res['sharpe_ratio']:.2f}"])
        writer.writerow(["Max Drawdown", f"{res['max_drawdown']*100:.2f}%"])
        writer.writerow(["Total Trades", res['total_trades']])
        writer.writerow(["Win Rate", f"{res['win_rate']*100:.1f}%"])
        writer.writerow(["Profit Factor", f"{res['profit_factor']:.2f}"])
        writer.writerow(["Total Commission", f"{res['total_commission']*100:.4f}%"])
        writer.writerow([])
        
        # Equity curve data
        writer.writerow(["Date", "Strategy Value", "Buy & Hold Value"])
        for pt in res['equity_curve']:
            writer.writerow([pt['date'], f"{pt['strategy_value']:.4f}", f"{pt['buy_hold_value']:.4f}"])

        output.seek(0)
        return output
    except Exception as exc:
        logger.error("Backtest export error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
