# Rural Registry (Python-only Frontend)

Aplicação em **Python (FastAPI)** para gerenciar **produtores rurais**, **propriedades (fazendas)**, **safras** e **culturas** — com **frontend 100% Python** (HTML renderizado no servidor) e **gráficos interativos ECharts** (via CDN), sem frameworks de front-end.

> **Status atual**: API via Docker + Postgres; CRUD completo de **Produtores** e **Fazendas** (com regra de áreas); **Safras** e **Plantios**; **Dashboard** com filtros (UF e Safra) e **export CSV**; scripts de **seed** via API; **testes automatizados** com Pytest + SQLite em memória; **CI** no GitHub Actions.

---

## Sumário

- [Tecnologias](#tecnologias)
- [Como executar](#como-executar)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Endpoints implementados](#endpoints-implementados)
- [Dashboard](#dashboard)
- [Scripts (seeds)](#scripts-seeds)
- [Testes](#testes)
  - [Estratégia](#estratégia)
  - [Dependências](#dependências)
  - [Como rodar os testes](#como-rodar-os-testes)
  - [Cobertura de testes](#cobertura-de-testes)
  - [Estrutura da pasta `tests/`](#estrutura-da-pasta-tests)
  - [Solução de problemas (FAQ)](#solução-de-problemas-faq)
- [CI (GitHub Actions)](#ci-github-actions)
- [Roadmap](#roadmap)
- [Licença](#licença)

---

## Tecnologias

- **Python 3.11**, **FastAPI**, **SQLAlchemy 2.x**
- **PostgreSQL 16** (Docker)
- **Uvicorn** (ASGI)
- **Loguru** (logging)
- **Jinja2** (templates server-side)
- **ECharts** (gráficos no browser via CDN, sem framework)
- **Faker** + **httpx** (scripts de seed via API)
- **Pytest** (testes) + **SQLite em memória**
- **Docker** + **Docker Compose**

---

## Como executar

```bash
docker compose up --build
# API:        http://localhost:8000
# Swagger:    http://localhost:8000/docs
# Dashboard:  http://localhost:8000/dashboard
```

> Se a porta 5432 estiver ocupada, troque a porta de mapeamento do Postgres no `docker-compose.yml`.
> Para desenvolvimento, o serviço `web` usa `PYTHONPATH=/app` e `working_dir: /app` para resolver `import app`.

---

## Variáveis de ambiente

- `DATABASE_URL`
  ```
  postgresql+psycopg2://postgres:postgres@db:5432/rural
  ```
- Opcional (fora do compose):
  ```
  sqlite:///./rural.db
  ```

---

## Endpoints implementados

### Produtores (`/api/producers`)
- `POST /api/producers` — cria produtor (valida CPF/CNPJ, normaliza dígitos, único)
- `GET /api/producers` — lista (filtro `?q=` por nome)
- `GET /api/producers/{id}` — detalhe
- `PATCH /api/producers/{id}` — atualiza nome
- `DELETE /api/producers/{id}` — remove

### Fazendas (`/api/farms`)
- `POST /api/farms` — cria fazenda vinculada a `producer_id`  
  Regra: `area_agricultable + area_vegetation ≤ area_total`
- `GET /api/farms` — lista; filtro `?producer_id=`
- `PATCH /api/farms/{id}` — atualiza; regra revalidada
- `DELETE /api/farms/{id}` — remove

### Safras (`/api/seasons`)
- `POST /api/seasons` — cria/garante safra (idempotente pelo nome, ex.: “Safra 2024”)
- `GET /api/seasons` — lista

### Plantios (`/api/plantings`)
- `POST /api/plantings` — cria cultura em (fazenda, safra)  
  Regra: unicidade `(farm_id, season_id, culture)`
- `GET /api/plantings` — lista; filtros `?farm_id=`, `?season_id=`
- `DELETE /api/plantings/{id}` — remove

---

## Dashboard

Páginas server-side (Jinja2) e gráficos **ECharts** (CDN) consumindo endpoints JSON:
- `GET /dashboard/data/filters` → `{ states: [UF], seasons: [{id,name}] }`
- `GET /dashboard/data/state`
- `GET /dashboard/data/culture?state=UF&season_id=ID`
- `GET /dashboard/data/landuse?state=UF`

Export CSV:
- `/dashboard/export/culture.csv?state=UF&season_id=ID`
- `/dashboard/export/landuse.csv?state=UF`

---

## Scripts (seeds)

```bash
# Produtores
docker compose exec web python scripts/seed_producers.py --n 30

# Fazendas
docker compose exec web python scripts/seed_farms.py --per-producer 3 --seed 42

# Safras e Plantios
docker compose exec web python scripts/seed_seasons_plantings.py --year-start 2021 --year-end 2025 --min-cult 1 --max-cult 3 --seed 7
```

---

## Testes

### Estratégia
- Os testes rodam com **SQLite em memória** via `sqlalchemy.create_engine(..., poolclass=StaticPool)` para serem rápidos e herméticos.
- O `conftest.py`:
  - define `TESTING=1` (o app **não** inicializa o banco “real” no `startup`);
  - injeta a raiz do projeto no `PYTHONPATH` para permitir `import app`;
  - **importa `app.models`** antes do `create_all()` para registrar as tabelas;
  - sobrescreve a dependência `get_db` para usar uma **Session** de teste;
  - recria o schema **antes de cada teste** com um fixture `autouse=True`.

### Dependências
Adicione ao `requirements.txt`:
```
pytest==8.3.2
# opcional (cobertura):
pytest-cov==5.0.0
```

### Como rodar os testes
Dentro do contêiner (recomendado):
```bash
docker compose exec web pytest -q
```

Um teste específico:
```bash
docker compose exec web pytest -q tests/test_producers.py::test_create_producer_ok
```

Ver logs de print/Logger:
```bash
docker compose exec web pytest -q -s
```

Fora do contêiner (se usar venv local):
```bash
pytest -q
```

### Cobertura de testes
```bash
docker compose exec web pytest --cov=app --cov-report=term-missing
```
> Gerará um relatório mostrando linhas não cobertas por teste.

### Estrutura da pasta `tests/`
```
tests/
├─ __init__.py                 # torna 'tests' um pacote (facilita imports relativos)
├─ conftest.py                 # engine SQLite in-memory, override de get_db, fixture autouse
├─ test_producers.py           # CRUD e validações de produtores
├─ test_farms.py               # regra de áreas e normalização de UF
├─ test_seasons_plantings.py   # safra idempotente + unicidade de plantios
└─ test_dashboard.py           # endpoints JSON do dashboard (filtros e agregações)
```


## Licença

Projeto distribuído sob a licença **MIT**.
