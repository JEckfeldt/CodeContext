# CodeContext Project Status

Handoff document for continuing development. **Scope and phased goals** are defined in the [Roadmap](ROADMAP.md). This file describes **what is shipped**, **what works today**, **what is missing**, and **recommended next steps**.

---

## Development summary

| | |
|--|--|
| **Current phase** | Post–Phase 4 MVP (Phases 1–4 complete; Phase 5 not started) |
| **Completed phases** | 1 Repository Ingestion · 2 Code Indexing · 3 Semantic Search · 4 AI Code Assistant |
| **Recommended next milestone** | Production foundations: **authentication**, **re-index workflow**, and **deployment** |
| **Approximate MVP maturity** | **Strong local/demo MVP** — ingest (ZIP or Git URL) → search → explain with Docker, Postgres, and OpenAI; not production-hardened (no auth, no hosted deploy story, no streaming/history) |

---

## Summary

Phases **1–4** are **complete**. CodeContext is a single-page app where users **connect a project** (ZIP or public Git URL), **browse files**, and use one **project workspace** with two modes:

- **Search** — natural-language search over indexed snippets (semantic / vector search)
- **Explain** — RAG assistant that answers from retrieved context with **source citations**

Ingestion is **source-agnostic**: ZIP and Git URL both flow through `app/ingestion/` (Importer → `ExtractedDocument` → shared chunking, embeddings, search, and explain).

The frontend uses a **unified, responsive workspace** (light theme, tabbed modes, full-width results). Backend tests: **66 passed, 1 skipped** (default). Frontend: **`npm run build`** verified. ZIP and Git import paths verified in Docker after **git** was added to the backend image.

**Phase 5** (advanced developer tools) and several **cross-cutting** features (auth, streaming, etc.) are **not** implemented.

---

## Phase overview

| Phase | Roadmap goal | Status |
|-------|----------------|--------|
| 1 — Repository Ingestion | Upload and browse discovered source files | **Complete** (ZIP + Git URL import) |
| 2 — Code Indexing | Prepare repositories for semantic search | **Complete** |
| 3 — Semantic Search | Find relevant code with natural language | **Complete** |
| 4 — AI Code Assistant | Grounded answers with file citations | **Complete** |
| 5 — Advanced Developer Tools | Scale and deeper repo insights | **Not started** |

---

## Current state

| Layer | Stack |
|--------|--------|
| Frontend | Next.js — ZIP / Git connect, file list, **Search** / **Explain** workspace |
| Backend | FastAPI, SQLAlchemy async, Alembic, **ingestion pipeline**, retrieval, LLM + RAG |
| Database | PostgreSQL 16 + **pgvector** + **HNSW** (cosine) |

**Backend ingestion flow:**

```text
Source (ZIP or Git URL)
        ↓
Importer (ZipImporter / GitImporter)
        ↓
CodeExtractor → ExtractedDocument[]
        ↓
Persist files → chunk → optional embed
        ↓
Search / Explain (vector search + RAG)
```

**Legacy mental model** (still accurate for outcomes): discovered content → `files` → `code_chunks` → optional embeddings → vector search → (Explain) RAG → answer + citations.

---

## UI workflow (today)

```text
Connect project (Upload ZIP  |  Repository URL)
        ↓
Browse discovered files + active project summary
        ↓
Project workspace (one panel, tabbed)
   ┌─────────┬──────────┐
   │ Search  │ Explain  │  ← only one mode visible at a time
   └─────────┴──────────┘
        ↓
   Query input + primary action (Search / Explain)
        ↓
   Results (scrollable, full width)
```

### Search (UI label)

**Purpose:** Help users **locate** relevant files, documents, and code in the indexed project.

**Backend:** `POST /api/v1/projects/{id}/search` → vector similarity over embedded chunks.

**Results:** Ranked hits with path, line range, symbol (if any), snippet, similarity score.

### Explain (UI label)

**Purpose:** Help users **understand** the project via AI explanations tied to indexed content.

**Backend:** `POST /api/v1/projects/{id}/ask` → retrieve chunks → RAG prompt → LLM → Markdown answer + **SourceCitation** list (aligned with prompt context).

**Results:** Markdown answer and expandable source cards (path, lines, symbol, snippet).

Component filenames (`RepositorySearchSection`, `RepositoryAskSection`, etc.) are unchanged; user-facing copy uses Search / Explain.

---

## Current MVP capabilities

Everything below works **today** when run via Docker (or equivalent) with PostgreSQL + pgvector, **git** in the backend container, and OpenAI configured as documented.

**Ingestion & browsing**

- Create project and **ZIP upload** (`POST .../upload`)
- **Git repository URL import** — validate URL, shallow `git clone`, same discovery rules as ZIP (`POST .../import`)
- **Source-agnostic pipeline** — `backend/app/ingestion/` (`SourceType`, `ExtractedDocument`, importers, `CodeExtractor`, shared `_ingest_imported_tree`)
- File discovery with extension / ignore rules and `.gitignore` respect
- Persist file metadata and content
- **Browse** discovered files in the UI
- Frontend: tabbed **Upload ZIP** / **Repository URL** on the connect panel

**Indexing & search (backend)**

- **Code chunking** (Python / Markdown parsers; line-based fallback) from `ExtractedDocument`
- Optional **embeddings** on ingest (`EMBEDDING_ENABLED`, OpenAI; **disabled by default**)
- **pgvector** storage and **HNSW** cosine index
- **Semantic search** API and Search UI

**AI assistant (backend + UI)**

- LLM provider abstraction + OpenAI chat completions (`LLM_ENABLED`)
- RAG **prompts**, **assistant_service** orchestration
- **Explain** UI: Markdown answers, **source citations**, user-friendly errors
- Citation list matches chunks sent to the model (`select_rag_context_chunks`)

**Frontend / UX**

- **Responsive** layout (mobile / tablet / desktop)
- **Unified workspace** with tabbed Search / Explain (state preserved when switching tabs)
- Light, developer-tool-style UI (panels, composers, code blocks)

**Quality & tooling**

- Backend unit/API tests (including Git importer and import API with mocked clone); optional Postgres integration test (skipped by default)
- **Test settings isolation** — pytest skips repo `.env` and forces feature flags off so local `.env` does not break deterministic tests
- Frontend production build passes
- Backend Docker image includes **git** for in-container cloning

---

## HTTP API (reference)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/projects` | Create project |
| POST | `/api/v1/projects/{id}/upload` | Upload ZIP |
| POST | `/api/v1/projects/{id}/import` | Import Git URL (`{ "source_type": "git", "url": "…" }`) |
| GET | `/api/v1/projects/{id}/files` | List files |
| POST | `/api/v1/projects/{id}/search` | Search (semantic) |
| POST | `/api/v1/projects/{id}/ask` | Explain (RAG) |
| GET | `/api/v1/health` | Health check |

**Import request (Git):** `{ "source_type": "git", "url": "https://github.com/user/repository" }`.

**Import / upload response:** `{ "project_id", "files_discovered", "chunks_created", "embeddings_created", "ingestion_status" }`.

**Ask request:** `{ "question": "…", "top_k": 8 }` (`top_k` optional, 1–20).

**Ask response:** `{ "project_id", "question", "answer", "citations": [{ "index", "file_path", "start_line", "end_line", "symbol_name", "snippet", "similarity" }] }`.

Search/ask require **PostgreSQL + pgvector**, **`EMBEDDING_ENABLED`**, and for ask also **`LLM_ENABLED`** + **`OPENAI_API_KEY`**. See [README.md](../README.md) and `.env.example`.

---

## Completed work (by phase)

### Phase 1 — Repository Ingestion

- ZIP upload, project create, discovery, filters, persist files
- **Ingestion refactor** — `app/ingestion/` (`SourceType`, `ExtractedDocument`, `BaseImporter` / `BaseExtractor`, `IngestionPipeline`)
- **Git URL ingestion** — `GitImporter`, URL validation, shallow clone, `POST .../import`; frontend **Repository URL** tab
- **Docker** — `git` installed in backend image for clone inside containers

### Phase 2 — Code Indexing

Chunks via `ExtractedDocument` / `build_document_chunks`, parsers, optional embeddings, pgvector + migration `0004` HNSW.

### Phase 3 — Semantic Search

`search_similar_chunks`, search API, Search UI (`frontend/components/search/`).

### Phase 4 — AI Code Assistant

`app/llm/`, `app/prompts/`, `assistant_service`, ask API/schemas, Explain UI (`frontend/components/assistant/`), citation alignment hardening.

| Area | Path |
|------|------|
| Ingestion | `backend/app/ingestion/` |
| Retrieval | `backend/app/retrieval/` |
| LLM | `backend/app/llm/` |
| Prompts | `backend/app/prompts/` |
| Orchestration | `backend/app/services/assistant_service.py`, `backend/app/ingestion/service.py` |
| Routes | `backend/app/api/routes/projects.py` |
| Shell / workspace | `frontend/components/code-context-app.tsx` |
| Connect UI | `frontend/components/repository/repository-uploader.tsx` |
| API client | `frontend/lib/api.ts` |

---

## Current limitations

Features that **do not exist** today (do not assume they work):

**Product & access**

- **Authentication** / login
- **Multi-user** or multi-tenant projects
- **Deployment** guide or production hosting setup in-repo (Docker Compose is for local/dev)

**Ingestion & indexing**

- **Private Git** remotes (SSH keys, tokens, GitHub App) — public HTTP(S) URLs only
- **Non-Git sources** in the UI (PDF, single-file upload, etc.) — pipeline-ready but not exposed
- **Re-index** or refresh index **without** re-importing or re-uploading
- **Background indexing** workers (ingest is synchronous from the user’s perspective)
- UI **embedding coverage** indicators (empty search vs missing vectors)

**Assistant UX**

- **Streaming** AI responses
- **Conversation history** / multi-turn threads (roadmap Phase 4 stretch; not built)

**Advanced search & platform**

- Hybrid retrieval, **re-ranking**, repository **maps**, **dependency graphs**
- **Usage analytics** / billing
- Public chunk listing API

---

## Recommended next priorities

### High priority

- **Authentication** — secure projects and API before any shared deployment
- **Re-index workflow** — re-chunk / re-embed without full re-upload or re-clone; surface status in UI
- **Deployment** — documented path to staging/production (env, migrations, secrets)

### Medium priority

- **Private Git** — credentials, shallow clone for private GitHub/GitLab repos
- **Streaming** Explain responses
- **Conversation history** for follow-up questions
- **Retrieval improvements** — thresholds, optional re-rank before RAG
- **Embedding / indexing status** in UI after ingest

### Future (Phase 5+)

- Additional source types (PDF, Markdown files, plain text) via new importers
- Repository maps and navigation
- Dependency / relationship insights
- Background workers for large repos
- Hybrid retrieval and re-ranking at scale
- Multi-repository or org-wide chat (depends on auth)

---

## Development notes

### Run locally

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000 (`/api/v1/health`)  
- Backend entrypoint: `alembic upgrade head` then uvicorn  
- Rebuild backend after Dockerfile changes so **git** is available for Git import

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW.

Legacy DBs from `init_db()` only: `alembic stamp 0002_create_code_chunks` then `alembic upgrade head`.

### Tests

```bash
cd backend && python -m pytest -q    # 66 passed, 1 skipped (default)
cd frontend && npm run build
```

Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

---

*When Phase 5 or major platform work ships, update **Phase overview**, **Completed work**, **Current MVP capabilities**, and **Recommended next priorities**.*
