from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    cash_balance = Column(Float, default=10000.0)

class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    ticker = Column(String, index=True)
    action = Column(String)  # 'BUY' or 'SELL'
    shares = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
