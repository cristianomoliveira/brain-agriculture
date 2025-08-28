# tests/test_producers.py
from .conftest import client

VALID_CPF = "39053344705"  # CPF válido para testes

def test_create_producer_ok():
    c = client()
    resp = c.post("/api/producers", json={"cpf_cnpj": VALID_CPF, "name": "Joana"})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] >= 1
    assert data["cpf_cnpj"] == VALID_CPF
    assert data["name"] == "Joana"

def test_create_producer_invalid_cpf():
    c = client()
    resp = c.post("/api/producers", json={"cpf_cnpj": "123", "name": "X"})
    # Pydantic valida e FastAPI retorna 422
    assert resp.status_code == 422

def test_create_producer_duplicate():
    c = client()
    c.post("/api/producers", json={"cpf_cnpj": VALID_CPF, "name": "A"})
    resp = c.post("/api/producers", json={"cpf_cnpj": VALID_CPF, "name": "B"})
    assert resp.status_code == 400
    assert "já cadastrado" in resp.text

def test_list_producers_filter_by_name():
    c = client()
    c.post("/api/producers", json={"cpf_cnpj": VALID_CPF, "name": "Maria Fernanda"})
    c.post("/api/producers", json={"cpf_cnpj": "11144477735", "name": "João"})
    resp = c.get("/api/producers?q=Maria")
    assert resp.status_code == 200
    arr = resp.json()
    assert len(arr) == 1
    assert arr[0]["name"].startswith("Maria")
