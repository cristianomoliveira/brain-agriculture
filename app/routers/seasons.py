# app/routers/seasons.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/seasons", tags=["seasons"])

@router.post("", response_model=schemas.SeasonOut)
def create_season(data: schemas.SeasonCreate, response: Response, db: Session = Depends(get_db)):
    # idempotente: se já existe, devolve 200; senão cria (201)
    exists = db.execute(select(models.Season).where(models.Season.name == data.name)).scalar_one_or_none()
    if exists:
        return exists
    obj = models.Season(name=data.name)
    db.add(obj); db.commit(); db.refresh(obj)
    response.status_code = 201
    return obj

@router.get("", response_model=list[schemas.SeasonOut])
def list_seasons(db: Session = Depends(get_db)):
    rows = list(db.scalars(select(models.Season)))
    return rows
