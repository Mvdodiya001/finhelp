from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.shared.db_models import User, PortfolioTransaction
from src.domain.portfolio.schemas import PortfolioResponse, TradeRequest
from src.domain.auth.service import get_current_user
from src.domain.portfolio.service import calculate_portfolio_valuation, calculate_portfolio_history

router = APIRouter()

@router.get("/api/portfolio", response_model=PortfolioResponse)
def get_portfolio(
    page: int = 1, limit: int = 20,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return calculate_portfolio_valuation(page, limit, current_user, db)

@router.post("/api/portfolio/trade")
def execute_trade(
    req: TradeRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    total_cost = req.shares * req.price

    if req.action == "BUY":
        if current_user.cash_balance < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        current_user.cash_balance -= total_cost

    elif req.action == "SELL":
        # Calculate current holdings
        transactions = db.query(PortfolioTransaction).filter(
            PortfolioTransaction.user_id == current_user.id,
            PortfolioTransaction.ticker == req.ticker
        ).all()
        shares_owned = sum(t.shares if t.action == "BUY" else -t.shares for t in transactions)
        
        if shares_owned < req.shares:
            raise HTTPException(status_code=400, detail="Insufficient shares")
        current_user.cash_balance += total_cost
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    tx = PortfolioTransaction(
        user_id=current_user.id,
        ticker=req.ticker,
        action=req.action,
        shares=req.shares,
        price=req.price
    )
    db.add(tx)
    db.commit()
    return {"message": "Trade executed successfully"}

@router.get("/api/portfolio/history")
def get_portfolio_history(
    days: int = 30,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return calculate_portfolio_history(days, current_user, db)
