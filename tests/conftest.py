# tests/conftest.py
import os, sys, pathlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Sinaliza modo de teste (evita o startup mexer no DB "real")
os.environ.setdefault("TESTING", "1")

# Garante que a raiz do projeto (/app) esteja no PYTHONPATH
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Base, get_db
from app.main import app
from app import models  # <<< IMPORTANTE: registra os modelos no metadata

# Engine SQLite em memória (compartilhada) para testes
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usa a sessão de teste em todas as rotas
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def _db_schema():
    # Isola cada teste com schema limpinho
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def client():
    return TestClient(app)
