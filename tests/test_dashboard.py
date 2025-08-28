# tests/test_dashboard.py
from .conftest import client

def seed_minimal(c):
    # produtor
    p = c.post("/api/producers", json={"cpf_cnpj": "39053344705", "name": "A"}).json()
    # fazenda
    f = c.post("/api/farms", json={
        "producer_id": p["id"],
        "name": "Fazenda A",
        "city": "Unaí",
        "state": "MG",
        "area_total": 100,
        "area_agricultable": 60,
        "area_vegetation": 40
    }).json()
    # safra
    s = c.post("/api/seasons", json={"name": "Safra 2024"}).json()
    # plantio
    c.post("/api/plantings", json={"farm_id": f["id"], "season_id": s["id"], "culture": "Milho"}).json()
    return f, s

def test_dashboard_json_endpoints():
    c = client()
    farm, season = seed_minimal(c)

    # filtros
    filters = c.get("/dashboard/data/filters").json()
    assert "states" in filters and "seasons" in filters

    # estado (sem filtro)
    st = c.get("/dashboard/data/state").json()
    assert "data" in st and isinstance(st["data"], list)

    # cultura com filtros
    cu = c.get(f"/dashboard/data/culture?state=MG&season_id={season['id']}").json()
    assert "data" in cu and any(item["name"] == "Milho" for item in cu["data"])

    # uso do solo com filtro de UF
    lu = c.get("/dashboard/data/landuse?state=MG").json()
    assert "data" in lu and isinstance(lu["data"], list)
