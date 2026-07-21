# CodeContext Project Status

Living progress tracker for the CodeContext monorepo. Update this file as milestones move forward.

For planned phases and scope, see the [Roadmap](ROADMAP.md).

---

## Current milestone

**Phase 3 — Semantic Search** (next)

**Phase 2 — Code Indexing** is **complete**. Repositories are ingested, parsed into chunks, optionally embedded, and vectors are indexed with **HNSW (cosine)** on PostgreSQL for Phase 3 retrieval.

**Where we are now:** Upload → chunk → embed (opt-in) → pgvector HNSW index. No search API or UI yet—that is Phase 3.

---

## Phase 1 — Repository Ingestion (complete)


| Area                                               | Status                           |
| -------------------------------------------------- | -------------------------------- |
| ZIP upload & project creation                      | Done                             |
| File discovery (extensions, ignores, `.gitignore`) | Done                             |
| Persist file metadata + full source `content`      | Done                             |
| Frontend upload + file browser                     | Done                             |
| Git clone ingestion                                | Not started (optional extension) |


**Outcome (Roadmap):** User can upload a repository and browse discovered source files. **Achieved.**

---

## Phase 2 — Code Indexing (complete)

Roadmap features: language-aware parsing, code chunking, embedding generation, vector storage (pgvector).  
Roadmap indexing outcome: *Prepare repositories for intelligent search* — **achieved** (vectors + HNSW ready; query API is Phase 3).

### Phase 2A–2C (complete)

- **2A:** `CodeChunk` model, line chunking, ingest-time indexing, migration `0002`
- **2B:** Python/Markdown parsers, `symbol_name`, pipeline fallback
- **2C:** OpenAI embeddings (opt-in), migration `0003_chunk_symbol_embedding`

### Phase 2D — Vector storage (pgvector) (complete)

- [x] HNSW index `ix_code_chunks_embedding_hnsw` on `code_chunks.embedding` with **`vector_cosine_ops`**
- [x] Partial index `WHERE embedding IS NOT NULL`
- [x] Alembic migration `0004_code_chunks_embedding_hnsw` (PostgreSQL only; no-op on other dialects)
- [x] Backend Docker entrypoint runs **`alembic upgrade head`** before uvicorn
- [x] SQLite tests keep **JSON** embedding fallback via `EmbeddingColumn`
- [x] Postgres integration test (`pytest -m integration` + `CODECONTEXT_INTEGRATION_DATABASE_URL`)

**Ops notes:** Default HNSW uses pgvector defaults. Tune `m` / `ef_construction` later if repos grow very large. Similarity queries should use the **`<=>` cosine distance** operator (same ops class as the index).

**Migration note:** Revision `0003` id shortened to `0003_chunk_symbol_embedding` (fits Alembic `version_num` 32-char limit). Existing DBs created only via `init_db()` should run `alembic stamp 0002_create_code_chunks` then `alembic upgrade head` once.

### Phase 2 — Cross-cutting (optional, as needed)

- [ ] `Project.indexing_status` / `chunks_count` / `indexed_at` for clearer upload vs index failures
- [ ] `POST /api/v1/projects/{id}/reindex` to retry chunking (and later embedding) without re-upload
- [ ] Expose chunk stats in upload response or a small status endpoint (backend-only until Phase 3 UI)

---

## Phase 3 — Semantic Search (upcoming)

See [Roadmap Phase 3](ROADMAP.md#phase-3--semantic-search). **Unblocked** — Phase 2 indexing infrastructure is ready.

- [ ] Vector similarity search scoped by `project_id`
- [ ] Search API + ranking / filters
- [ ] Search UI and context retrieval hooks for AI

---

## Phase 4 — AI Code Assistant (upcoming)

See [Roadmap Phase 4](ROADMAP.md#phase-4--ai-code-assistant). Blocked on **Phase 3** (retrieval).

- [ ] Replace mock “Ask CodeContext” with RAG over retrieved chunks
- [ ] LLM integration, citations, conversation history

---

## Phase 5 — Advanced Developer Tools (upcoming)

See [Roadmap Phase 5](ROADMAP.md#phase-5--advanced-developer-tools).

- [ ] Background indexing, repo maps, dependency insights, retrieval tuning

---

## Completed (rollup checklist)

- [x] Repository structure and core documentation
- [x] Frontend application shell and design system
- [x] Backend FastAPI foundation
- [x] PostgreSQL + pgvector extension enabled; chunk embeddings stored when enabled
- [x] Project and File database models
- [x] Repository ZIP ingestion API
- [x] File discovery (supported types, ignores, `.gitignore`)
- [x] Ingestion tests (API + discovery)
- [x] Docker Compose dev environment
- [x] Improved frontend hot reload in Docker
- [x] Connect Projects UI to ingestion API
- [x] End-to-end Phase 1 demo (upload → browse files in UI)
- [x] Phase 2A — CodeChunk persistence and line-based chunking on ingest
- [x] Phase 2B — Language-aware parsing (Python, Markdown) + pipeline integration
- [x] Phase 2C — Embedding generation (OpenAI, opt-in via `EMBEDDING_ENABLED`)
- [x] Phase 2D — pgvector HNSW index (cosine) + Docker alembic on startup

---

## In progress

**Phase 3 — Semantic search API and retrieval** (recommended next).

---

## Suggested next steps

These follow the [Roadmap](ROADMAP.md) order and current codebase state.

1. **Operational:** `docker compose up --build` runs migrations through `0004` on backend start. Enable embeddings with `EMBEDDING_ENABLED=true` + `OPENAI_API_KEY`, then re-upload.
2. **Phase 3:** Add project-scoped vector search (`ORDER BY embedding <=> query`) and a backend search endpoint.
3. **Phase 3 UI:** Minimal search in the single-page app (optional after API).
4. **Phase 4:** RAG + real Q&A.
5. **Optional:** Git clone ingestion; reindex endpoint; HNSW tuning for large repos.

---

## Current notes

### Stack

- **Frontend:** Next.js (App Router), single-page workspace, off-white doc-style UI.
- **Backend:** FastAPI, SQLAlchemy async, Alembic migrations.
- **Database:** PostgreSQL (`pgvector/pgvector:pg16` in Compose); HNSW index on chunk embeddings; SQLite JSON fallback in unit tests.

### Backend behavior today


| Endpoint                            | Behavior                                                                                                                                      |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /api/v1/projects`             | Create project                                                                                                                                |
| `POST /api/v1/projects/{id}/upload` | ZIP → files → parse/chunk → optional embed; returns `files_discovered`, `chunks_created`, `embeddings_created`, `ingestion_status` |
| `GET /api/v1/projects/{id}/files`   | File metadata only (no `content`, no chunks)                                                                                                  |


Indexing + embeddings on upload; migrations **`0001`–`0004`** via Alembic (backend container entrypoint).

**Postgres integration tests:**  
`CODECONTEXT_INTEGRATION_DATABASE_URL=postgresql+asyncpg://...@localhost:5432/... pytest -m integration`

### Frontend

- Upload and file list are wired to Phase 1 APIs.
- Chunks and search are **not** shown in the UI yet (intentional for Phase 2A).

### Explicitly out of scope until later phases

- Semantic search UI/API (Phase 3)
- LLM / RAG answers (Phase 4)
- Authentication and multi-tenant projects

Embeddings are **implemented but off by default** (`EMBEDDING_ENABLED=false` in `.env.example`).

### Run locally

```bash
docker compose up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000) — health at `/api/v1/health`
- Set `NEXT_PUBLIC_API_URL` and `CORS_ORIGINS` for your environment (see `.env.example`).

---

## How to update this file

When finishing a sub-phase (2B, 2C, …):

1. Move its checklist items to **Completed (rollup)** or mark complete under the Phase 2 subsection.
2. Set **In progress** to the slice you are actively building.
3. Adjust **Suggested next steps** so the top item is the next logical Roadmap step.

