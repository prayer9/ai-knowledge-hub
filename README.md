# AI Knowledge Hub

An incremental AI application portfolio project. **v0.1 is a FastAPI CRUD backend, not yet an AI/RAG system.**

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
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

This initial version does not claim production readiness, authentication, or AI capabilities.
