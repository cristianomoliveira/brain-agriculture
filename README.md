# Rural Registry (Python-only Frontend)

Aplicação em **Python (FastAPI)** para gerenciar produtores rurais, propriedades, safras e culturas — com **frontend 100% Python** (HTML renderizado no servidor, sem frameworks de front).

## Objetivos (MVP)
- Subir API com Docker + Postgres
- Criar **models** no SQLAlchemy (Produtor, Fazenda, Safra, Plantio)
- Implementar **regras de negócio**:
  - Validar **CPF/CNPJ**
  - `área_agricultável + área_vegetação ≤ área_total`
- Rotas CRUD (REST)
- Dashboard server-side (Jinja2 + Matplotlib) [futuro]

## Como rodar (dev)
```bash
docker compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
