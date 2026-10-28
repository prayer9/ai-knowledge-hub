# AI Knowledge Hub

AI application/full-stack portfolio MVP v1.0. Features document upload, text chunking, optional embedding-based semantic retrieval, OpenAI-compatible LLM answers with citations, and a React/TypeScript frontend. **Without an embedding API key, retrieval falls back to lexical matching.**

## Option A: Docker Compose with PostgreSQL

Install Docker Desktop and run:

```bash
docker compose up --build -d
docker compose ps
```

Open <http://localhost:3000> for the frontend and <http://localhost:8000/docs> for API docs. The API container runs `alembic upgrade head` before starting. Stop with `docker compose down`; PostgreSQL data is kept in a named volume. The credentials in `docker-compose.yml` are for local development only, never for public deployment.

To enable generated answers, copy `.env.example` to `.env` and enter your own `LLM_API_KEY`. Optionally specify `LLM_BASE_URL` and `LLM_MODEL`. For semantic retrieval set `EMBEDDING_API_KEY` and `EMBEDDING_MODEL` using a compatible embeddings provider. If `EMBEDDING_API_KEY` is absent, the app also tries `LLM_API_KEY`. Do not commit `.env`. Without keys, the app displays retrieved chunks in clearly labeled demo mode. Documents uploaded before embeddings were configured need to be re-uploaded to gain vectors.

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

Additional endpoints: `POST/GET /api/knowledge-bases/{id}/documents`, `DELETE /api/knowledge-bases/{id}/documents/{document_id}`, `POST /api/knowledge-bases/{id}/chat` and `POST /api/knowledge-bases/{id}/chat/stream`. Upload supports PDF, DOCX, TXT and Markdown files up to 5 MB. Invalid input returns 422; missing resources return 404. Data persists in the database.

## Roadmap

1. PostgreSQL pgvector index and hybrid semantic/BM25 retrieval with reranking
2. True upstream LLM token streaming, chat history, asynchronous document processing
3. Authentication, multi-user isolation, observability and production security

If `DATABASE_URL` is not set, data persists to `./knowledge_hub.db`. For PostgreSQL, set `DATABASE_URL` to a suitable `postgresql+psycopg://...` URL. Run migrations before starting the API.

Tests use isolated SQLite databases and verify persistence across app instances, document ingestion and cited retrieval. The SSE endpoint delivers an already-completed model answer in chunks; it is not yet true upstream model streaming. There is no authentication or per-user isolation, and this MVP must not be exposed as a public multi-tenant service.
