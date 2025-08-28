# tests/test_seasons_plantings.py
from .conftest import client

def _create_producer(c, cpf="39053344705", name="Prod A"):
    r = c.post("/api/producers", json={"cpf_cnpj": cpf, "name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]

def _create_farm(c, pid):
    r = c.post("/api/farms", json={
        "producer_id": pid,
        "name": "Fazenda Teste",
        "city": "Belo Horizonte",
        "state": "MG",
        "area_total": 500,
        "area_agricultable": 300,
        "area_vegetation": 200
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]

def test_season_create_idempotent():
    c = client()
    r1 = c.post("/api/seasons", json={"name": "Safra 2024"})
    assert r1.status_code in (200, 201)
    r2 = c.post("/api/seasons", json={"name": "Safra 2024"})
    assert r2.status_code == 200  # já existia

def test_planting_create_and_duplicate():
    c = client()
    pid = _create_producer(c)
    farm_id = _create_farm(c, pid)
    # cria safra
    s = c.post("/api/seasons", json={"name": "Safra 2023"}).json()
    season_id = s["id"]
    # cria plantio
    p1 = c.post("/api/plantings", json={"farm_id": farm_id, "season_id": season_id, "culture": "Soja"})
    assert p1.status_code == 201, p1.text
    # duplicado
    p2 = c.post("/api/plantings", json={"farm_id": farm_id, "season_id": season_id, "culture": "Soja"})
    assert p2.status_code == 400
