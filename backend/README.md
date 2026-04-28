# Backend

FastAPI backend for the AI chatbot SaaS.

## Run locally

1. Create a virtual environment
2. Install dependencies from `requirements/base.txt`
3. Copy `.env.example` to `.env`
4. Start PostgreSQL
5. Run:

```bash
uvicorn app.main:app --reload
```

## Database migrations

```bash
alembic upgrade head
```

## Background worker

```bash
dramatiq app.workers.actors
```

## Docker

```bash
docker compose up --build
```

## Current backend scope

- JWT auth
- organization and bot bootstrap
- PDF, URL, and text ingestion
- FAISS vector storage
- OpenAI embeddings and answer generation
- source citations
- low-confidence fallback
- email-based escalation
- Redis-backed rate limiting
- analytics and conversation admin APIs
- Alembic migration scaffolding
- Dramatiq worker scaffolding
