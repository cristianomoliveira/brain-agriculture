# app/main.py
from fastapi import FastAPI
from loguru import logger
from sqlalchemy import text
from app.database import Base, engine, SessionLocal
from app import models  # <-- IMPORTANTE: registra os modelos no metadata

app = FastAPI(title="Rural Registry (MVP)", version="0.0.3")

@app.on_event("startup")
def on_startup():
    # garante que as tabelas existam
    Base.metadata.create_all(bind=engine)
    # ping no banco só pra confirmar conexão
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    logger.info("DB ok e tabelas garantidas.")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"db": "ok"}
