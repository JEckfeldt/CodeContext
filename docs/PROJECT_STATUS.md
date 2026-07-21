# CodeContext Project Status

Handoff document for continuing development. Scope and long-term direction live in the [Roadmap](ROADMAP.md).

**Summary:** Phase 1 and Phase 2 are **complete**. The app ingests ZIP repositories, stores files, builds semantic chunks, optionally embeds them, and indexes vectors in PostgreSQL. **Semantic search and AI answers are not built yet** (Phases 3–4).

---

## Current State

CodeContext is a monorepo **AI codebase assistant** (work in progress):

| Layer | Stack |
|--------|--------|
| Frontend | Next.js (App Router), single-page UI — upload + file list + mock Q&A preview |
| Backend | FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL 16 + **pgvector** (`pgvector/pgvector` image in Docker Compose) |

**Data flow today:** ZIP upload → project + `files` rows (with full source `content`) → `code_chunks` (parsed/split) → optional OpenAI embeddings → pgvector column + **HNSW (cosine)** index.

**What CodeContext can do today:** ingest a repo, browse discovered files in the UI, and (on the backend) prepare chunked, embeddable vector data for future retrieval. It cannot yet search by meaning or answer questions with real RAG.

---

## Completed Work

### Phase 1 — Repository Ingestion

| Deliverable | Purpose |
|-------------|---------|
| ZIP repository upload | Accept a codebase archive without Git hosting integration |
| File discovery and filtering | Walk the tree; respect supported extensions, default ignores, and `.gitignore` |
| File persistence | Store path, metadata, and full text in PostgreSQL for downstream indexing |
| Frontend upload flow | Create project, upload ZIP, show progress/errors via `RepositoryUploader` |
| File browsing | List ingested paths after upload (`FileBrowser`) |

**Roadmap outcome achieved:** user can upload a repository and browse discovered source files.

**Not in Phase 1:** Git clone ingestion (optional future extension).

### Phase 2 — Code Indexing

| Deliverable | Purpose |
|-------------|---------|
| `CodeChunk` model | Store retrievable snippets with line ranges, language, kind, optional `symbol_name` |
| Language-aware parsing | Choose parser by `File.language` instead of only fixed-size splits |
| Python AST parsing | Chunk functions, classes, methods, and module preamble with accurate line numbers |
| Markdown parsing | Split on headings into `markdown_section` blocks |
| Chunk generation | Line-based fallback for other languages; size limits (~2000 chars) after structure-aware blocks |
| Embedding generation | OpenAI provider; batch embed after upload when enabled |
| pgvector storage | `embedding` column (1536-dim); metadata `embedding_model`, `embedded_at` |
| HNSW vector index | `ix_code_chunks_embedding_hnsw` with `vector_cosine_ops`, partial `WHERE embedding IS NOT NULL` |
| Tests and migrations | Alembic `0001`–`0004`; pytest unit suite + optional Postgres integration tests |

**Roadmap indexing goal achieved:** repositories are **ready for** semantic search (vectors stored and indexed). The **search/query path** itself is Phase 3.

---

## Current Capabilities

End-to-end behavior **as implemented**:

1. **Upload repository ZIP** — `POST /api/v1/projects`, then `POST /api/v1/projects/{id}/upload`.
2. **Store repository files** — discovered files persisted with content in `files`.
3. **Parse source code** — Python and Markdown use dedicated parsers; others use line-based chunking.
4. **Create semantic chunks** — `code_chunks` rows linked to files and projects.
5. **Generate embeddings** — when `EMBEDDING_ENABLED=true` and `OPENAI_API_KEY` is set; skipped otherwise (`embeddings_created: 0`).
6. **Store vectors for future retrieval** — embeddings in pgvector; HNSW index for cosine similarity queries (use `<=>` in SQL).

**Frontend (working):** single-page upload, repository summary, file list.

**Frontend (mock only):** “Ask CodeContext” uses hardcoded preview answers — not connected to the backend.

**Backend API surface (today):**

| Method | Path | Notes |
|--------|------|--------|
| POST | `/api/v1/projects` | Create project |
| POST | `/api/v1/projects/{id}/upload` | Ingest + index + optional embed |
| GET | `/api/v1/projects/{id}/files` | File metadata only (no content, no chunks) |
| GET | `/api/v1/health` | Health check |

---

## Not Implemented Yet

Compared to [ROADMAP.md](ROADMAP.md):

### Phase 3 — Semantic Search

- Retrieval service (`app/retrieval/` is a placeholder)
- Vector similarity search API (project-scoped query embedding + pgvector)
- Search UI
- Result ranking and filtering
- Context packaging for downstream AI

### Phase 4 — AI Code Assistant

- LLM integration beyond embeddings (`app/llm/`, `app/prompts/` placeholders)
- RAG pipeline (retrieve chunks → prompt → answer)
- Prompt construction
- Conversation persistence
- Source citations wired to real search results

### Phase 5 — Developer Experience (Roadmap: Advanced Developer Tools)

- Repository map / navigation
- Dependency graph and relationship insights
- Background indexing (upload path is synchronous today)
- Performance tuning (HNSW params, batching, large repos)
- Cost optimization (embedding batching exists; broader cost controls do not)

### Other gaps (not full roadmap phases)

- Authentication and multi-user projects
- Git clone ingestion
- Reindex API / project indexing status fields
- Public API to list or inspect chunks

---

## Next Recommended Step

**Milestone: Phase 3 — Semantic Search**

Implement in this order:

1. **Backend retrieval service** — embed the user query (reuse embedding provider), run pgvector cosine search filtered by `project_id`, return chunk metadata + scores + snippets (not necessarily full file content).
2. **Search API** — e.g. `POST /api/v1/projects/{id}/search` with `{ "query": "..." }`.
3. **Frontend integration** — minimal search input and results list (after API is stable).

Phase 4 should not start until retrieval returns ranked chunks reliably.

---

## Development Notes

### Docker setup

```bash
docker compose up --build
```

- **Frontend:** http://localhost:3000  
- **Backend:** http://localhost:8000  
- **DB:** PostgreSQL + pgvector on port `5432` (see `.env`)

Backend container runs **`alembic upgrade head`** on start (`backend/docker-entrypoint.sh`).

### Database and migrations

- **Source of truth:** Alembic migrations `0001` → `0004` (not `init_db()` alone for production-shaped DBs).
- **0003** (`0003_chunk_symbol_embedding`): `symbol_name`, embedding columns.
- **0004**: HNSW index on PostgreSQL only.

**Existing dev DBs** created before Alembic (tables from `init_db()` only):

```bash
docker compose exec backend alembic stamp 0002_create_code_chunks
docker compose exec backend alembic upgrade head
```

Or reset the `postgres-data` Docker volume for a clean history.

### Important environment variables

| Variable | Role |
|----------|------|
| `DATABASE_URL` | Async Postgres URL for backend |
| `NEXT_PUBLIC_API_URL` | Frontend → backend (e.g. `http://localhost:8000`) |
| `CORS_ORIGINS` | Must include frontend origin |
| `EMBEDDING_ENABLED` | Default `false`; set `true` to embed on upload |
| `OPENAI_API_KEY` | Required when embeddings enabled |
| `EMBEDDING_MODEL` | Default `text-embedding-3-small` |
| `EMBEDDING_BATCH_SIZE` | Default `64` |
| `DATA_DIR` | Upload/extraction data on disk |
| `CODECONTEXT_INTEGRATION_DATABASE_URL` | Optional; enables Postgres integration pytest |

Copy from `.env.example` to `.env` at repo root.

### Tests

From `backend/`:

```bash
python -m pytest -q
```

- **Default:** 26 passed, 1 skipped (integration test skipped without `CODECONTEXT_INTEGRATION_DATABASE_URL`).
- **Postgres integration:**  
  `CODECONTEXT_INTEGRATION_DATABASE_URL=postgresql+asyncpg://...@localhost:5432/... pytest -m integration`
- Unit tests use **SQLite in-memory** with JSON embedding fallback (not pgvector).

### Key code locations

| Area | Path |
|------|------|
| Ingestion | `backend/app/services/ingestion_service.py` |
| Indexing / chunking | `backend/app/indexing/`, `backend/app/services/indexing_service.py` |
| Parsers | `backend/app/parsers/` |
| Embeddings | `backend/app/embeddings/`, `backend/app/services/embedding_service.py` |
| Vector types / index name | `backend/app/database/vector.py` |
| Frontend app | `frontend/components/code-context-app.tsx` |

---

*When you ship a milestone, update this file: move items from **Not Implemented** to **Completed Work**, refresh **Current Capabilities**, and set **Next Recommended Step**.*
