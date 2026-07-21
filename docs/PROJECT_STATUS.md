# CodeContext Project Status

Handoff document for continuing development. Scope and long-term direction live in the [Roadmap](ROADMAP.md).

**Summary:** Phases **1–3** are **complete** for MVP. Users can upload a ZIP, browse files, and **search indexed code by meaning**. Phase **4** (AI assistant / RAG answers) is next.

---

## Current State

| Layer | Stack |
|--------|--------|
| Frontend | Next.js single-page UI — upload, file list, **semantic search** |
| Backend | FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL 16 + **pgvector** + **HNSW** (cosine) |

**Architecture:** ZIP → `files` → parsed `code_chunks` → optional OpenAI embeddings → vector index → query embed → cosine search → ranked snippets in the UI.

---

## Completed Work

### Phase 1 — Repository Ingestion

Enables accepting a codebase without Git hosting: ZIP upload, filtered discovery (extensions, ignores, `.gitignore`), persistence of file metadata and full `content`, and a frontend upload + file browser flow.

### Phase 2 — Code Indexing

Prepares data for semantic search: `CodeChunk` model, Python/Markdown parsers with line-based fallback, embedding generation (OpenAI, opt-in), pgvector storage, and HNSW index (`0001`–`0004` migrations).

### Phase 3 — Semantic Search

Delivers meaning-based code lookup:

| Deliverable | Purpose |
|-------------|---------|
| Retrieval service | `search_similar_chunks()` — embed query, pgvector cosine search, top 10 by project |
| Search API | `POST /api/v1/projects/{id}/search` |
| Search UI | `RepositorySearchSection`, result cards with loading / empty / error states |
| Tests | API tests + retrieval unit tests + optional Postgres integration |

**Roadmap Phase 3 outcome achieved:** user can search the codebase and find relevant snippets (not yet AI-generated prose).

---

## Current Capabilities

End-to-end **today**:

1. Create project and upload ZIP.
2. Discover and persist source files; browse paths in the UI.
3. Parse and chunk code (structure-aware where supported).
4. Optionally embed chunks on upload (`EMBEDDING_ENABLED` + `OPENAI_API_KEY`).
5. **Search** with natural language in the UI or via API; view path, symbol, lines, snippet, similarity.

**API:**

| Method | Path |
|--------|------|
| POST | `/api/v1/projects` |
| POST | `/api/v1/projects/{id}/upload` |
| GET | `/api/v1/projects/{id}/files` |
| POST | `/api/v1/projects/{id}/search` |
| GET | `/api/v1/health` |

**Not available:** LLM answers, conversation history, auth, Git clone, reindex endpoint.

---

## Not Implemented Yet

### Phase 4 — AI Code Assistant

- LLM integration (`app/llm/`, `app/prompts/` placeholders)
- RAG pipeline (retrieve → prompt → answer)
- Prompt templates and citation formatting
- Conversation persistence
- Replace placeholder `AssistantResponse` UI with real answers

### Phase 5 — Advanced Developer Tools

- Repository map, dependency insights
- Background indexing, HNSW tuning at scale
- Broader cost controls

### Other gaps

- Authentication / multi-tenant projects
- Git clone ingestion
- Public chunk listing API
- Project indexing status / reindex without re-upload

---

## Next Recommended Step

**Phase 4 — AI Code Assistant**

1. Retrieval-augmented generation using existing search results as context.
2. LLM provider + prompts with source citations.
3. Wire frontend Q&A to backend (retire mock-only assistant components or repurpose them).

---

## Development Notes

### Docker

```bash
docker compose up --build
```

Backend entrypoint: `alembic upgrade head` then uvicorn.

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW.

Legacy DBs from `init_db()` only: `alembic stamp 0002_create_code_chunks` then `alembic upgrade head`.

### Environment

See [README.md](../README.md) and `.env.example` — especially `EMBEDDING_ENABLED`, `OPENAI_API_KEY`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`.

### Tests

```bash
cd backend && python -m pytest -q    # 34 passed, 1 skipped (default)
cd frontend && npm run build
```

Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

### Key paths

| Area | Path |
|------|------|
| Retrieval | `backend/app/retrieval/` |
| Search route | `backend/app/api/routes/projects.py` |
| Search UI | `frontend/components/search/` |
| API client | `frontend/lib/api.ts` |

---

*Update this file when Phase 4 ships: move AI items to **Completed Work** and refresh **Next Recommended Step**.*
