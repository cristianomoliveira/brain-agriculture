# app/routers/dashboard.py
from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app import models
import csv
import io

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_farms = db.scalar(select(func.count(models.Farm.id))) or 0
    total_hectares = float(db.scalar(select(func.coalesce(func.sum(models.Farm.area_total), 0.0))) or 0.0)
    ctx = {"request": request, "total_farms": total_farms, "total_hectares": total_hectares}
    return templates.TemplateResponse("dashboard.html", ctx)

# --------------------- Dados para ECharts (JSON) ---------------------

@router.get("/dashboard/data/filters")
def data_filters(db: Session = Depends(get_db)):
    # UFs presentes no banco (distintos)
    states = [r[0] for r in db.execute(select(models.Farm.state).distinct().order_by(models.Farm.state))]
    # Safras
    seasons = [{"id": s.id, "name": s.name} for s in db.scalars(select(models.Season).order_by(models.Season.name))]
    return {"states": states, "seasons": seasons}

@router.get("/dashboard/data/state")
def data_state(
    # opcionalmente poderíamos filtrar por safra (fazendas que tenham plantio na safra),
    # mas manteremos simples: gráfico geral de fazendas por UF
    db: Session = Depends(get_db)
):
    rows = db.execute(
        select(models.Farm.state, func.count(models.Farm.id)).group_by(models.Farm.state)
    ).all()
    data = [{"name": r[0], "value": r[1]} for r in rows] or [{"name": "Sem dados", "value": 1}]
    return {"data": data, "title": "Fazendas por Estado"}

@router.get("/dashboard/data/culture")
def data_culture(
    state: str | None = Query(default=None, description="UF para filtrar (ex.: MG)"),
    season_id: int | None = Query(default=None, description="ID da Safra"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Planting.culture, func.count(models.Planting.id))
        .join(models.Farm, models.Farm.id == models.Planting.farm_id)
    )
    if state:
        stmt = stmt.where(models.Farm.state == state.upper())
    if season_id:
        stmt = stmt.where(models.Planting.season_id == season_id)
    stmt = stmt.group_by(models.Planting.culture)

    rows = db.execute(stmt).all()
    data = [{"name": r[0], "value": r[1]} for r in rows] or [{"name": "Sem dados", "value": 1}]
    return {"data": data, "title": "Cultura Plantada"}

@router.get("/dashboard/data/landuse")
def data_landuse(
    state: str | None = Query(default=None, description="UF para filtrar (ex.: MG)"),
    db: Session = Depends(get_db),
):
    q_agri = select(func.coalesce(func.sum(models.Farm.area_agricultable), 0.0))
    q_veg  = select(func.coalesce(func.sum(models.Farm.area_vegetation), 0.0))
    if state:
        q_agri = q_agri.where(models.Farm.state == state.upper())
        q_veg  = q_veg.where(models.Farm.state == state.upper())

    total_agri = float(db.scalar(q_agri) or 0.0)
    total_veg  = float(db.scalar(q_veg) or 0.0)

    if total_agri + total_veg == 0:
        data = [{"name": "Sem dados", "value": 1}]
    else:
        data = [
            {"name": "Agricultável", "value": round(total_agri, 2)},
            {"name": "Vegetação",    "value": round(total_veg, 2)},
        ]
    return {"data": data, "title": "Uso do Solo"}

# --------------------- Export CSV ---------------------

def _csv_response(rows: list[tuple[str, float]], filename: str) -> Response:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["category", "value"])
    for name, value in rows:
        writer.writerow([name, value])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/dashboard/export/culture.csv")
def export_culture_csv(
    state: str | None = Query(default=None),
    season_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Planting.culture, func.count(models.Planting.id))
        .join(models.Farm, models.Farm.id == models.Planting.farm_id)
    )
    if state:
        stmt = stmt.where(models.Farm.state == state.upper())
    if season_id:
        stmt = stmt.where(models.Planting.season_id == season_id)
    stmt = stmt.group_by(models.Planting.culture)
    rows = db.execute(stmt).all() or [("Sem dados", 1)]
    return _csv_response(rows, "culture.csv")

@router.get("/dashboard/export/landuse.csv")
def export_landuse_csv(
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q_agri = select(func.coalesce(func.sum(models.Farm.area_agricultable), 0.0))
    q_veg  = select(func.coalesce(func.sum(models.Farm.area_vegetation), 0.0))
    if state:
        q_agri = q_agri.where(models.Farm.state == state.upper())
        q_veg  = q_veg.where(models.Farm.state == state.upper())

    total_agri = float(db.scalar(q_agri) or 0.0)
    total_veg  = float(db.scalar(q_veg) or 0.0)

    rows = [("Agricultável", total_agri), ("Vegetação", total_veg)]
    # evita CSV vazio absoluto
    if total_agri + total_veg == 0:
        rows = [("Sem dados", 1.0)]
    return _csv_response(rows, "landuse.csv")
