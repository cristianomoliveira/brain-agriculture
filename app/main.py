from fastapi import FastAPI
from loguru import logger
import os

app = FastAPI(title="Rural Registry (MVP)", version="0.0.1")

@app.get("/health")
def health():
    db_url = os.getenv("DATABASE_URL", "not-set")
    return {"status": "ok", "database_url": db_url}

@app.on_event("startup")
async def _startup():
    logger.info("API iniciada.")
