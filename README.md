# CodeContext

AI-powered codebase assistant that helps developers understand unfamiliar repositories. It ingests ZIP archives, indexes source into semantic chunks, embeds them with OpenAI, and supports **natural-language search** over your code via pgvector.

Phase 4 (LLM answers / RAG chat) is not implemented yet.

## MVP today

- Upload a code repository (ZIP)
- Browse discovered source files
- **Search the codebase by meaning** (semantic similarity)
- *(Planned)* Ask questions and receive grounded AI answers with citations

## Documentation

- [Roadmap](docs/ROADMAP.md) — phased plan and scope
- [Project Status](docs/PROJECT_STATUS.md) — handoff and current capabilities

## Semantic search

CodeContext embeds code **chunks** (not whole files) and finds the closest matches to a natural-language query using **cosine similarity** in PostgreSQL.

### Search workflow

1. **Upload** a ZIP → files are discovered and stored.
2. **Index** → parsers build `code_chunks`; optional **embeddings** run when enabled.
3. **Search** → the query is embedded with the same model; pgvector returns the top similar chunks for that project.
4. **UI** → results show file path, symbol, line range, snippet, and similarity score.

```text
ZIP upload → files → chunks → (optional) embeddings → HNSW index
                                    ↑
User query ── embed query ──────────┴── cosine search → ranked chunks
```

### Search API

**`POST /api/v1/projects/{project_id}/search`**

Request:

```json
{
  "query": "Where is authentication implemented?"
}
```

Response:

```json
{
  "project_id": "…",
  "query": "Where is authentication implemented?",
  "results": [
    {
      "file_path": "src/auth.py",
      "content": "def login(): …",
      "start_line": 1,
      "end_line": 12,
      "symbol_name": "login",
      "similarity": 0.87
    }
  ]
}
```

| Status | Meaning |
|--------|---------|
| 200 | Success (empty `results` is valid) |
| 404 | Project not found |
| 422 | Invalid body (empty query) |
| 503 | PostgreSQL/pgvector unavailable, or embedding provider not configured |

Search requires **PostgreSQL with pgvector** in production (SQLite is used only for unit tests).

### pgvector + HNSW architecture

- **Storage:** `code_chunks.embedding` — `vector(1536)` for `text-embedding-3-small`
- **Index:** `ix_code_chunks_embedding_hnsw` using **`vector_cosine_ops`**
- **Query:** `ORDER BY embedding <=> query_vector` (cosine distance); similarity reported as `1 - distance` for normalized vectors
- **Scope:** all searches filter by `project_id` and `embedding IS NOT NULL`

Migrations: Alembic `0001`–`0004` (see [Project Status](docs/PROJECT_STATUS.md)).

### Required environment variables

Copy [`.env.example`](.env.example) to `.env`.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Backend → PostgreSQL (async) |
| `NEXT_PUBLIC_API_URL` | Frontend → backend API |
| `CORS_ORIGINS` | Browser origin for API (e.g. `http://localhost:3000`) |
| `EMBEDDING_ENABLED` | Set `true` to embed chunks **on upload** and to embed **search queries** |
| `OPENAI_API_KEY` | Required when embeddings are enabled |
| `EMBEDDING_MODEL` | Default `text-embedding-3-small` |
| `EMBEDDING_BATCH_SIZE` | Batch size for chunk embedding (default `64`) |

Without `EMBEDDING_ENABLED=true` and a valid key, upload succeeds but search returns **503** (no query embedding provider).

## Run locally

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000 (health: `/api/v1/health`)  
- Backend runs **`alembic upgrade head`** on container start.

## Screenshots

<!-- TODO: add screenshot — repository upload and file list -->
<!-- TODO: add screenshot — semantic search results -->

## Tests

```bash
cd backend && python -m pytest -q
cd frontend && npm run build
```

Optional Postgres integration tests:

```bash
CODECONTEXT_INTEGRATION_DATABASE_URL=postgresql+asyncpg://... pytest -m integration
```

## License

See [LICENSE](LICENSE).
