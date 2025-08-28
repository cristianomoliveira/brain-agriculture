# app/routers/producers.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app import models
from app import schemas

router = APIRouter(prefix="/api/producers", tags=["producers"])

@router.post("", response_model=schemas.ProducerOut, status_code=201)
def create_producer(data: schemas.ProducerCreate, db: Session = Depends(get_db)):
    # data.cpf_cnpj já vem validado/normalizado (só dígitos)
    exists = db.execute(
        select(models.Producer).where(models.Producer.cpf_cnpj == data.cpf_cnpj)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado.")
    obj = models.Producer(cpf_cnpj=data.cpf_cnpj, name=data.name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.get("", response_model=list[schemas.ProducerOut])
def list_producers(q: str | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(models.Producer)
    if q:
        stmt = stmt.where(models.Producer.name.ilike(f"%{q}%"))
    rows = list(db.scalars(stmt))
    return rows

@router.get("/{producer_id}", response_model=schemas.ProducerOut)
def get_producer(producer_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Producer, producer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produtor não encontrado.")
    return obj

@router.patch("/{producer_id}", response_model=schemas.ProducerOut)
def update_producer(producer_id: int, data: schemas.ProducerUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Producer, producer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produtor não encontrado.")
    if data.name is not None:
        obj.name = data.name
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.delete("/{producer_id}", status_code=204)
def delete_producer(producer_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Producer, producer_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Produtor não encontrado.")
    db.delete(obj); db.commit()
