# AI Knowledge Hub

An incremental portfolio project for AI application/full-stack engineering. **v0.2 is a database-backed FastAPI CRUD backend, not yet an AI/RAG system.**

## Option A: Docker Compose with PostgreSQL

Install Docker Desktop and run:

```bash
docker compose up --build -d
docker compose ps
```

Open <http://localhost:8000/docs>. The API container runs `alembic upgrade head` before starting. Stop with `docker compose down`; PostgreSQL data is kept in a named volume. The credentials in `docker-compose.yml` are for local development only, never for public deployment.

## Option B: Run locally with SQLite

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs>.

```bash
pytest -q
```

## API

| Method | Endpoint | Success |
|---|---|---|
| GET | `/health` | 200 |
| POST | `/api/knowledge-bases` | 201 |
| GET | `/api/knowledge-bases` | 200 |
| GET | `/api/knowledge-bases/{id}` | 200 |
| PUT | `/api/knowledge-bases/{id}` | 200 |
| DELETE | `/api/knowledge-bases/{id}` | 204 |

Invalid input returns 422; missing resources return 404. The data is stored in memory and disappears on restart.

## Roadmap

1. PostgreSQL/SQLAlchemy persistence and document upload
2. LLM API, streaming chat, RAG retrieval and citations
3. React/TypeScript frontend and Docker deployment

If `DATABASE_URL` is not set, data persists to `./knowledge_hub.db`. For PostgreSQL, set `DATABASE_URL` to a suitable `postgresql+psycopg://...` URL. Run migrations before starting the API.

Tests use isolated SQLite databases and verify persistence across app instances. The service is not yet production-ready and has no authentication or AI model integration.
