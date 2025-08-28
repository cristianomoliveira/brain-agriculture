# app/routers/plantings.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/plantings", tags=["plantings"])

@router.post("", response_model=schemas.PlantingOut, status_code=201)
def create_planting(data: schemas.PlantingCreate, db: Session = Depends(get_db)):
    # valida fk
    if not db.get(models.Farm, data.farm_id):
        raise HTTPException(status_code=404, detail="Propriedade não encontrada.")
    if not db.get(models.Season, data.season_id):
        raise HTTPException(status_code=404, detail="Safra não encontrada.")

    # checa unicidade (farm, season, culture)
    exists = db.execute(
        select(models.Planting).where(
            and_(
                models.Planting.farm_id == data.farm_id,
                models.Planting.season_id == data.season_id,
                models.Planting.culture == data.culture,
            )
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="Plantio já cadastrado para (fazenda, safra, cultura).")

    obj = models.Planting(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[schemas.PlantingOut])
def list_plantings(
    farm_id: int | None = Query(default=None),
    season_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(models.Planting)
    if farm_id is not None:
        stmt = stmt.where(models.Planting.farm_id == farm_id)
    if season_id is not None:
        stmt = stmt.where(models.Planting.season_id == season_id)
    return list(db.scalars(stmt))

@router.delete("/{planting_id}", status_code=204)
def delete_planting(planting_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Planting, planting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantio não encontrado.")
    db.delete(obj); db.commit()
