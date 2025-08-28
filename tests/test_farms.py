# tests/test_farms.py
from .conftest import client

def _create_producer(c, cpf="39053344705", name="Joana"):
    r = c.post("/api/producers", json={"cpf_cnpj": cpf, "name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]

def test_create_farm_ok():
    c = client()
    pid = _create_producer(c)
    payload = {
        "producer_id": pid,
        "name": "Fazenda Azul",
        "city": "Unaí",
        "state": "mg",
        "area_total": 1000,
        "area_agricultable": 700,
        "area_vegetation": 300
    }
    r = c.post("/api/farms", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["state"] == "MG"  # deve normalizar para maiúsculas
    assert data["area_total"] == 1000

def test_create_farm_invalid_areas():
    c = client()
    pid = _create_producer(c, cpf="11144477735")
    payload = {
        "producer_id": pid,
        "name": "Fazenda Verde",
        "city": "Patos",
        "state": "PB",
        "area_total": 1000,
        "area_agricultable": 800,
        "area_vegetation": 300  # 800+300 > 1000
    }
    r = c.post("/api/farms", json=payload)
    assert r.status_code == 400
    assert "Soma de áreas" in r.text
