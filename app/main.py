# app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sqlalchemy import text
from app.database import Base, engine, SessionLocal
from app import models  
from app.routers import producers, farms, seasons, plantings, dashboard

TESTING = os.getenv("TESTING") == "1"

app = FastAPI(title="Rural Registry (MVP)", version="0.0.7")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    logger.info("DB ok e tabelas garantidas.")

# servir arquivos estáticos (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# inclui as rotas 
app.include_router(dashboard.router)
app.include_router(producers.router)
app.include_router(farms.router)
app.include_router(seasons.router)  
app.include_router(plantings.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"db": "ok"}
