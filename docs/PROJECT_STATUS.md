# CodeContext Project Status

Handoff document for continuing development. **Scope and phased goals** are defined in the [Roadmap](ROADMAP.md). This file describes **what is shipped**, **what works today**, and **what comes next**.

**Summary:** Phases **1–3** are **complete**. Users can upload a ZIP, browse files, and **search the codebase by meaning**. **Phase 4 — AI Code Assistant** is the next milestone.

---

## Phase overview

| Phase | Roadmap goal | Status |
|-------|----------------|--------|
| 1 — Repository Ingestion | Upload and browse discovered source files | **Complete** |
| 2 — Code Indexing | Prepare repositories for semantic search | **Complete** |
| 3 — Semantic Search | Find relevant code with natural language | **Complete** |
| 4 — AI Code Assistant | Grounded answers with file citations | **Not started** |
| 5 — Advanced Developer Tools | Scale and deeper repo insights | **Not started** |

---

## Current state

| Layer | Stack |
|--------|--------|
| Frontend | Next.js — upload, file list, semantic search UI |
| Backend | FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL 16 + **pgvector** + **HNSW** (cosine) |

**Data flow (today):** ZIP → `files` → parsed `code_chunks` → optional OpenAI embeddings → HNSW index → embed query → cosine search → ranked snippets in the UI.

Phase 3 also delivers **context retrieval** (ranked chunks) that Phase 4 RAG will consume unchanged.

---

## Completed work

### Phase 1 — Repository Ingestion

**Roadmap outcome:** User can upload a repository and browse its discovered source files.

| Roadmap feature | Status |
|-----------------|--------|
| Repository upload (ZIP) | Done |
| Project management | Done (create project + upload) |
| Recursive file discovery | Done |
| Supported file filtering and ignores | Done (extensions, `.gitignore`) |
| Persist file metadata and source content | Done |
| Git clone | Deferred (not in MVP) |

### Phase 2 — Code Indexing

**Roadmap outcome:** A repository becomes searchable by meaning, not just filenames.

| Roadmap feature | Status |
|-----------------|--------|
| Language-aware parsing | Done (Python, Markdown; fallback chunker) |
| Code chunking | Done |
| Embedding generation | Done (OpenAI, opt-in via `EMBEDDING_ENABLED`) |
| Vector storage (pgvector) | Done (+ HNSW index, migration `0004`) |

### Phase 3 — Semantic Search

**Roadmap outcome:** User can search the codebase and quickly find relevant files and snippets.

| Roadmap feature | Status |
|-----------------|--------|
| Vector similarity search | Done (`search_similar_chunks`, pgvector `<=>`) |
| Result ranking and filtering | Done (cosine similarity, scoped by `project_id`, top 10) |
| Search API and UI | Done (`POST .../search`, `RepositorySearchSection`) |
| Context retrieval for downstream AI | Done (same retrieval layer; no LLM yet) |

**Implementation highlights:**

| Deliverable | Location / notes |
|-------------|------------------|
| Retrieval service | `backend/app/retrieval/` |
| Search API | `POST /api/v1/projects/{id}/search` |
| Search UI | `frontend/components/search/` |
| Tests | Retrieval + API tests; optional Postgres integration |

---

## Current capabilities

What works end-to-end **today**:

1. Create a project and upload a ZIP archive.
2. Discover and persist source files; browse paths in the UI.
3. Parse and chunk code (structure-aware where supported).
4. Optionally embed chunks on upload (`EMBEDDING_ENABLED` + `OPENAI_API_KEY`).
5. **Search** with natural language (UI or API): file path, symbol, line range, snippet, similarity score.

**HTTP API**

| Method | Path |
|--------|------|
| POST | `/api/v1/projects` |
| POST | `/api/v1/projects/{id}/upload` |
| GET | `/api/v1/projects/{id}/files` |
| POST | `/api/v1/projects/{id}/search` |
| GET | `/api/v1/health` |

**Explicitly not available yet:** LLM-generated answers, conversation history, authentication, Git clone ingestion, reindex-without-re-upload, public chunk listing API.

---

## Phase 4 — AI Code Assistant (next)

Aligned with [Roadmap — Phase 4](ROADMAP.md#phase-4--ai-code-assistant).

**Goal:** Answer questions about a repository.

**Roadmap outcome:** User can ask questions and get **grounded answers linked to real project files**.

### Planned features (from roadmap)

| Feature | Intent |
|---------|--------|
| **LLM integration** | Chat/completion provider (e.g. OpenAI) with config parallel to embeddings |
| **Retrieval-augmented generation (RAG)** | User question → retrieve chunks (Phase 3) → build prompt with context → LLM answer |
| **Source citations** | Answer references `file_path`, line ranges, and/or symbols from retrieved chunks |
| **Conversation history** | Persist or session-scope turns so follow-up questions stay in context |

### Suggested build order

1. **Backend:** `app/llm/` provider + `app/prompts/` templates; single endpoint e.g. `POST /api/v1/projects/{id}/ask` (name TBD) that calls existing `search_similar_chunks` (or shared retrieval) then the LLM.
2. **Prompt design:** System instructions to answer only from provided snippets; require citation format; handle “no relevant context” safely.
3. **Frontend:** Replace or extend the search panel with Q&A — wire `AssistantResponse` (or successor) to streaming/non-streaming API; show citations alongside prose.
4. **Persistence (optional for MVP):** In-memory or DB-backed conversation per project; can ship a single-turn MVP first, then history.
5. **Ops:** Env vars for model, token limits, and cost guards; clear errors when LLM or retrieval is unavailable.

### Dependencies already in place

- Chunk index, embeddings, pgvector search, and search UI/tests from Phases 2–3.
- Retrieval returns structured hits suitable for prompt context and citation UI.

### Out of scope for Phase 4 (roadmap Phase 5+)

Repository maps, dependency graphs, background indexing jobs, and advanced retrieval (hybrid search, re-ranking) remain later phases unless needed for a minimal RAG MVP.

---

## Not implemented yet (beyond Phase 4)

### Phase 5 — Advanced Developer Tools

Per roadmap: repository maps, dependency/relationship insights, stronger retrieval strategies, background indexing and performance tuning.

### Cross-cutting gaps

- Authentication and multi-tenant projects
- Git clone ingestion
- Project indexing status and reindex without re-upload
- Embedding coverage indicators in the UI (empty search vs. missing vectors)

---

## Next recommended step

Start **Phase 4 — AI Code Assistant**: implement RAG on top of existing retrieval, add citations, then conversation history as a follow-on within the phase.

---

## Development notes

### Docker

```bash
docker compose up --build
```

Backend entrypoint: `alembic upgrade head` then uvicorn.

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW.

Legacy DBs created only via `init_db()`: `alembic stamp 0002_create_code_chunks` then `alembic upgrade head`.

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
| Phase 4 placeholders | `backend/app/llm/`, `backend/app/prompts/`, `frontend/components/content/assistant-response.tsx` |

---

*When Phase 4 ships: add a **Completed work — Phase 4** section, update the phase overview table, and set **Next recommended step** to Phase 5 or the highest-priority cross-cutting gap.*
