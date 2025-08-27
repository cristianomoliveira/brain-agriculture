# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rural.db")

# Para SQLite local (fallback) precisamos desse connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    """Base para os modelos SQLAlchemy."""
    pass

# Dependency para FastAPI (vamos usar mais adiante)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
