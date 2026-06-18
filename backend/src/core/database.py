import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

if "pytest" in sys.modules:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stock_predictor.db"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://admin:adminpassword@localhost:5444/stock_predictor"
    )

# SQLite uses connect_args={"check_same_thread": False}, Postgres doesn't
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
