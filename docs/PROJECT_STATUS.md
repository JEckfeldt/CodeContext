# CodeContext Project Status

Living progress tracker for the CodeContext monorepo. Update this file as milestones move forward.

For planned phases and scope, see the [Roadmap](ROADMAP.md).

---

## Current milestone

**Phase 2 — Code Indexing**

Phase 1 is complete end-to-end (upload → browse files). Phase 2A (chunk persistence and line-based chunking) is complete. The active roadmap goal is to **prepare repositories for intelligent search**: smarter chunks, embeddings, and vector storage, as described in [Phase 2 of the Roadmap](ROADMAP.md#phase-2--code-indexing).

**Where we are now:** Every successful ZIP upload creates `File` rows and derived `CodeChunk` rows automatically. Python and Markdown files use structure-aware parsers; other languages fall back to line-based chunks. Chunks are not embedded and are not searchable by meaning yet—that work is Phase 2C–2D below.

---

## Phase 1 — Repository Ingestion (complete)

| Area | Status |
|------|--------|
| ZIP upload & project creation | Done |
| File discovery (extensions, ignores, `.gitignore`) | Done |
| Persist file metadata + full source `content` | Done |
| Frontend upload + file browser | Done |
| Git clone ingestion | Not started (optional extension) |

**Outcome (Roadmap):** User can upload a repository and browse discovered source files. **Achieved.**

---

## Phase 2 — Code Indexing (in progress)

Roadmap features: language-aware parsing, code chunking, embedding generation, vector storage (pgvector).  
Roadmap outcome: *A repository becomes searchable by meaning, not just filenames.* **Not yet achieved.**

### Phase 2A — Chunk foundation (complete)

- [x] `CodeChunk` database model (`file_id`, `project_id`, line range, `content`, `language`, `chunk_kind`, etc.)
- [x] Relationships: `File` → chunks, `Project` → chunks (cascade on delete / re-upload)
- [x] Alembic migration `0002_create_code_chunks`
- [x] Line-based chunking pipeline (~2000 characters, preserves `start_line` / `end_line`, `chunk_kind=text_block`)
- [x] Indexing runs automatically after file persistence on upload
- [x] Upload API reports `chunks_created`
- [x] Unit tests (chunking) + integration test (upload creates chunks)

**Limitations (by design for 2A):** No AST or tree-sitter; no overlap tuning; no project-level indexing status or reindex API; frontend does not surface chunks.

### Phase 2B — Language-aware parsing (complete)

Aligns with Roadmap *“Language-aware parsing”* and better *“Code chunking”* than fixed-size text blocks.

- [x] Parser registry under `app/parsers/` (by `File.language`)
- [x] Python: `ast`-based blocks (module preamble, functions, classes, methods)
- [x] Markdown: split on headings (`markdown_section`, heading as `symbol_name` in parser blocks)
- [x] Fallback: line-based chunker for JS/TS, config, unknown types, and invalid Python syntax
- [x] Richer `chunk_kind` values (`function`, `class`, `method`, `module`, `markdown_section`, `text_block`)
- [x] Pipeline: `File` → parser (if available) → size chunking → `CodeChunk`
- [x] Tests: Python parser, Markdown parser, pipeline fallback

**Note:** `symbol_name` is produced by parsers for structure-aware blocks; it is not persisted on `CodeChunk` yet (optional future column).

### Phase 2C — Embedding generation (not started)

Aligns with Roadmap *“Embedding generation”*.

- [ ] Embedding provider abstraction (`app/embeddings/`)
- [ ] Config: model name, batch size, enable/disable (`OPENAI_API_KEY` from `.env.example`)
- [ ] Build embed text from chunk + file path context (for quality, without changing citation `content`)
- [ ] Batch embed after chunking; idempotent skip for already-embedded chunks
- [ ] Tests with mocked provider (no live API in CI)

**Depends on:** Phase 2A (done). Can run in parallel with 2B, but structure-aware chunks improve embedding quality—many teams do **2B → 2C**.

### Phase 2D — Vector storage (pgvector) (not started)

Aligns with Roadmap *“Vector storage (pgvector)”*.

- [ ] Migration: nullable `embedding` column on `code_chunks` (or dedicated table), `embedding_model`, `embedded_at`
- [ ] HNSW / IVFFlat index on PostgreSQL (SQLite tests remain chunk-only)
- [ ] Wire `DEFAULT_EMBEDDING_DIMENSIONS` in `app/database/vector.py` to the chosen model
- [ ] Document migration / `alembic upgrade head` for Docker deployments

**Depends on:** Phase 2C.

### Phase 2 — Cross-cutting (optional, as needed)

- [ ] `Project.indexing_status` / `chunks_count` / `indexed_at` for clearer upload vs index failures
- [ ] `POST /api/v1/projects/{id}/reindex` to retry chunking (and later embedding) without re-upload
- [ ] Expose chunk stats in upload response or a small status endpoint (backend-only until Phase 3 UI)

---

## Phase 3 — Semantic Search (upcoming)

See [Roadmap Phase 3](ROADMAP.md#phase-3--semantic-search). Blocked on **Phase 2D** (vectors in the database).

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
- [x] PostgreSQL + pgvector extension enabled (infrastructure only; vectors not used yet)
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

---

## In progress

**Nothing actively in flight.** Next recommended slice: **Phase 2C** (embeddings).

---

## Suggested next steps

These follow the [Roadmap](ROADMAP.md) order and current codebase state.

1. **Operational:** Run `alembic upgrade head` on Postgres so `code_chunks` exists. Re-upload a ZIP and confirm `chunks_created` in the upload JSON response.

2. **Phase 2C:** Add embedding provider + batch job after chunking; feature-flag with `EMBEDDING_ENABLED` until API keys are configured.

3. **Phase 2D:** Add pgvector column and index; verify one project can store vectors for all chunks.

4. **Phase 3:** Implement search API and minimal search UI once vectors exist.

5. **Parallel / optional:** Git clone ingestion (Roadmap Phase 1 extension).

6. **Phase 4:** Wire the single-page Q&A UI to real retrieval + LLM.

7. **Future parsing:** JS/TS structure-aware parsers (tree-sitter or heuristics) if chunk quality for those languages becomes a bottleneck.

---

## Current notes

### Stack

- **Frontend:** Next.js (App Router), single-page workspace, off-white doc-style UI.
- **Backend:** FastAPI, SQLAlchemy async, Alembic migrations.
- **Database:** PostgreSQL; pgvector extension created at init/migration—**embedding columns and indexes not added yet**.

### Backend behavior today

| Endpoint | Behavior |
|----------|----------|
| `POST /api/v1/projects` | Create project |
| `POST /api/v1/projects/{id}/upload` | ZIP → discover files → replace `files` → parse/chunk → insert `code_chunks`; returns `files_discovered`, `chunks_created`, `ingestion_status` |
| `GET /api/v1/projects/{id}/files` | File metadata only (no `content`, no chunks) |

Indexing: `app/parsers/` (Python/Markdown) → `app/indexing/pipeline.py` → `app/indexing/chunking.py` (size limits + fallback); orchestration in `app/services/indexing_service.py` after upload.

### Frontend

- Upload and file list are wired to Phase 1 APIs.
- Chunks and search are **not** shown in the UI yet (intentional for Phase 2A).

### Explicitly out of scope until later phases

- Semantic search UI/API (Phase 3)
- LLM / RAG answers (Phase 4)
- Authentication and multi-tenant projects

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
