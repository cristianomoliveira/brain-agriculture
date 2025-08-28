# app/routers/farms.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/farms", tags=["farms"])

def _check_areas(total: float, agri: float, veg: float):
    if agri + veg > total + 1e-9:
        raise HTTPException(
            status_code=400,
            detail="Soma de áreas (agricultável + vegetação) não pode ultrapassar a área total."
        )

@router.post("", response_model=schemas.FarmOut, status_code=201)
def create_farm(data: schemas.FarmCreate, db: Session = Depends(get_db)):
    # valida produtor existe
    producer = db.get(models.Producer, data.producer_id)
    if not producer:
        raise HTTPException(status_code=404, detail="Produtor não encontrado.")
    _check_areas(data.area_total, data.area_agricultable, data.area_vegetation)
    farm = models.Farm(**data.model_dump())
    db.add(farm); db.commit(); db.refresh(farm)
    return farm

@router.get("", response_model=list[schemas.FarmOut])
def list_farms(producer_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(models.Farm)
    if producer_id is not None:
        stmt = stmt.where(models.Farm.producer_id == producer_id)
    return list(db.scalars(stmt))

@router.patch("/{farm_id}", response_model=schemas.FarmOut)
def update_farm(farm_id: int, data: schemas.FarmUpdate, db: Session = Depends(get_db)):
    farm = db.get(models.Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    # aplica mudanças
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(farm, k, v if k != "state" or v is None else v.upper())
    _check_areas(farm.area_total, farm.area_agricultable, farm.area_vegetation)
    db.add(farm); db.commit(); db.refresh(farm)
    return farm

@router.delete("/{farm_id}", status_code=204)
def delete_farm(farm_id: int, db: Session = Depends(get_db)):
    farm = db.get(models.Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    db.delete(farm); db.commit()
