# CodeContext Project Status

Handoff document for continuing development. **Scope and phased goals** are defined in the [Roadmap](ROADMAP.md). This file describes **what is shipped**, **what works today**, **what is missing**, and **recommended next steps**.

---

## Development summary

| | |
|--|--|
| **Current phase** | Post–Phase 4 MVP with **auth & multi-user projects** (Phases 1–4 complete; Phase 5 not started) |
| **Completed phases** | 1 Repository Ingestion · 2 Code Indexing · 3 Semantic Search · 4 AI Code Assistant · **Platform auth & project ownership** |
| **Recommended next milestone** | **Deployment**, **re-index workflow**, and **private Git** credentials |
| **Approximate MVP maturity** | **Multi-user local/demo MVP** — register/login, owned projects, multiple source types per project, search/explain with Docker, Postgres, pgvector, and OpenAI; not production-hardened (no hosted deploy guide, streaming, or conversation history) |

---

## Summary

CodeContext is a **multi-user AI workspace** for project content. Users **register and log in**, **create projects they own**, **import sources** (Git URL, ZIP, or individual files), then **Search** and **Explain** over all indexed content in that project.

Phases **1–4** remain **complete**. Ingestion is **source-agnostic** via `app/ingestion/` (Importer → `ExtractedDocument` → shared chunking, optional embeddings, search, RAG). Successful imports are recorded as **`project_sources`** rows (Git, ZIP, or file batch).

The frontend provides **`/register`**, **`/login`**, JWT session storage, **project create/select**, source import tabs, and a tabbed **Search / Explain** workspace. Backend tests: **82 passed, 1 skipped** (default). Frontend: **`npm run build`** verified.

**Phase 5** (advanced developer tools) and several UX/platform items (streaming, re-index UI, etc.) are **not** implemented.

---

## Phase overview

| Phase | Roadmap goal | Status |
|-------|----------------|--------|
| 1 — Repository Ingestion | Ingest and browse project content | **Complete** (ZIP, Git URL, individual files; owned projects) |
| 2 — Code Indexing | Prepare content for semantic search | **Complete** |
| 3 — Semantic Search | Find relevant content with natural language | **Complete** |
| 4 — AI Code Assistant | Grounded answers with citations | **Complete** |
| Platform — Auth & ownership | Users own projects; protected API | **Complete** |
| 5 — Advanced Developer Tools | Scale and deeper repo insights | **Not started** |

---

## Current state

| Layer | Stack |
|--------|--------|
| Frontend | Next.js — auth pages, project picker, ZIP / Git / file import, **Search** / **Explain** |
| Backend | FastAPI, JWT auth, SQLAlchemy async, Alembic, ingestion pipeline, retrieval, LLM + RAG |
| Database | PostgreSQL 16 + **pgvector** + **HNSW**; `users`, `projects.user_id`, `project_sources` |

**Product data model:**

```text
User
  └── Project (workspace)
        ├── ProjectSource[]   (git | zip | file — audit of imports)
        ├── File[]
        └── CodeChunk[] → optional embeddings → Search / Explain
```

**Backend ingestion flow:**

```text
Authenticated user selects owned Project
        ↓
Source (Git URL | ZIP | uploaded files)
        ↓
Importer (GitImporter | ZipImporter | FileImporter)
        ↓
ExtractedDocument[]  (CodeExtractor for trees; FileImporter direct)
        ↓
Persist / merge files → chunk → optional embed → record ProjectSource
        ↓
Search / Explain (JWT + ownership checks on every project route)
```

---

## UI workflow (today)

```text
Register or log in (/register, /login) → JWT stored client-side
        ↓
Create or select a project (owned by current user)
        ↓
Import sources: Upload ZIP | Repository URL | Individual Files
        ↓
Browse discovered files in that project
        ↓
Project workspace — Search | Explain (tabbed)
        ↓
Results (ranked hits or RAG answer + citations)
```

### Search (UI label)

**Purpose:** Locate relevant files, documents, and code in the **active project**.

**Backend:** `POST /api/v1/projects/{id}/search` (auth required; ownership enforced).

### Explain (UI label)

**Purpose:** Understand the project via AI answers tied to indexed content.

**Backend:** `POST /api/v1/projects/{id}/ask` (auth required; ownership enforced).

---

## Current MVP capabilities

Requires Docker (or equivalent), PostgreSQL + pgvector, **`JWT_SECRET_KEY`**, backend **git** for clone, and OpenAI flags as documented.

**Authentication & access**

- **Register / login** — `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- **JWT bearer** authentication; `GET /api/v1/auth/me`
- Password hashing (**passlib + bcrypt**; **`bcrypt>=4.0.0,<4.1`** pinned for compatibility)
- **Project ownership** — `projects.user_id`; users only see and mutate their projects
- **Authorization tests** — cross-user access returns 404

**Projects & sources**

- **List / create / get** owned projects (`GET/POST /projects`, `GET /projects/{id}`)
- **`project_sources`** — records each Git, ZIP, or file import (`source_type`, `source_name`, optional `source_url`)
- One project can accumulate **multiple imports** (e.g. Git repo + PDF + Markdown); file import **merges** by path; ZIP/Git **replace** project files for that ingest

**Ingestion & browsing**

- **ZIP** — `POST .../upload`
- **Git URL** — validate, shallow clone, `POST .../import`
- **Individual files** — `.md`, `.markdown`, `.txt`, text-based `.pdf` via `POST .../files/import`
- **Source-agnostic pipeline** — `backend/app/ingestion/`
- Discovery rules, `.gitignore`, browse in UI

**Indexing, search, assistant**

- Chunking from `ExtractedDocument`; optional embeddings (`EMBEDDING_ENABLED`, default off)
- pgvector + HNSW; Search and Explain UIs

**Quality & tooling**

- Backend tests (auth, authorization, ingestion, Git/file importers); **82 passed, 1 skipped**
- Pytest ignores repo `.env` for deterministic feature flags
- Frontend production build passes
- Migration **`0005_users_and_project_ownership`**

---

## HTTP API (reference)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/auth/register` | Create account (returns JWT) |
| POST | `/api/v1/auth/login` | Log in (returns JWT) |
| GET | `/api/v1/auth/me` | Current user (Bearer token) |
| GET | `/api/v1/projects` | List current user's projects |
| POST | `/api/v1/projects` | Create project (owned by user) |
| GET | `/api/v1/projects/{id}` | Get owned project |
| POST | `/api/v1/projects/{id}/upload` | Upload ZIP |
| POST | `/api/v1/projects/{id}/import` | Import Git URL |
| POST | `/api/v1/projects/{id}/files/import` | Upload individual files (multipart) |
| GET | `/api/v1/projects/{id}/files` | List files |
| POST | `/api/v1/projects/{id}/search` | Semantic search |
| POST | `/api/v1/projects/{id}/ask` | RAG explain |
| GET | `/api/v1/health` | Health check |

All **`/projects/*`** routes require **`Authorization: Bearer <token>`**.

Search/ask still require **PostgreSQL + pgvector**, **`EMBEDDING_ENABLED`**, and for ask **`LLM_ENABLED`** + **`OPENAI_API_KEY`**. See [README.md](../README.md) and `.env.example`.

---

## Completed work (by phase)

### Phase 1 — Repository Ingestion

- ZIP, Git URL, individual file imports; ingestion refactor (`app/ingestion/`)
- **Project sources** tracking; Docker **git** for clone

### Phase 2 — Code Indexing

- Chunks via `ExtractedDocument`; parsers; optional embeddings; migration `0004` HNSW

### Phase 3 — Semantic Search

- `search_similar_chunks`, search API, Search UI

### Phase 4 — AI Code Assistant

- LLM, RAG prompts, `assistant_service`, ask API, Explain UI, citation alignment

### Platform — Authentication & project ownership

- **`users`** table; **`projects.user_id`**; **`project_sources`**
- JWT auth routes; protected project API; ownership in `project_service`
- Frontend **`/login`**, **`/register`**, token storage, project-first workflow
- Migration **`0005_users_and_project_ownership`**
- **bcrypt pin** (`bcrypt<4.1`) for passlib compatibility

| Area | Path |
|------|------|
| Auth | `backend/app/api/routes/auth.py`, `backend/app/core/security.py`, `backend/app/services/auth_service.py` |
| Ownership | `backend/app/services/project_service.py` |
| Sources | `backend/app/models/project_source.py`, `backend/app/services/project_source_service.py` |
| Ingestion | `backend/app/ingestion/` |
| Shell | `frontend/components/code-context-app.tsx`, `frontend/components/auth/auth-form.tsx` |

---

## Current limitations

**Product & access**

- **No OAuth** / social login, orgs, teams, or roles
- **No password reset** or email verification
- **No deployment** guide for production hosting in-repo (Compose is for local/dev)
- Legacy **`projects` rows with `user_id` NULL** (pre-migration) are not accessible via the API

**Ingestion & indexing**

- **Public Git HTTP(S) only** — no private remotes or tokens
- **PDF** — text extraction only (no OCR); scanned PDFs may fail
- **Re-index** without re-import not supported
- **Synchronous** ingest (no background workers)
- No UI for **embedding coverage** / index health

**Assistant UX**

- **No streaming** responses
- **No conversation history** / multi-turn threads

**Advanced platform**

- Hybrid retrieval, re-ranking, repo maps, dependency graphs, analytics, public chunk API — **not built**

---

## Recommended next priorities

### High priority

- **Deployment** — staging/production path (env, secrets, migrations, `JWT_SECRET_KEY`)
- **Re-index workflow** — re-chunk / re-embed without full re-import; status in UI

### Medium priority

- **Private Git** — tokens / SSH for private remotes
- **Streaming** Explain responses
- **Conversation history**
- **Retrieval tuning** and embedding/index status in UI

### Future (Phase 5+)

- Repository maps and navigation
- Dependency insights
- Background workers for large projects
- Hybrid retrieval at scale

---

## Development notes

### Run locally

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000 (`/api/v1/health`)  
- Run **`alembic upgrade head`** (includes **0005**) before use  
- Set **`JWT_SECRET_KEY`** in `.env` (see `.env.example`)  
- Rebuild backend after **`requirements.txt`** or Dockerfile changes  

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW → **`0005` users, project ownership, project_sources**.

Legacy DBs from `init_db()` only: stamp through current head per existing docs, then `alembic upgrade head`.

### Tests

```bash
cd backend && python -m pytest -q    # 82 passed, 1 skipped (default)
cd frontend && npm run build
```

Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

---

*When Phase 5 or major platform work ships, update **Phase overview**, **Completed work**, **Current MVP capabilities**, and **Recommended next priorities**.*
