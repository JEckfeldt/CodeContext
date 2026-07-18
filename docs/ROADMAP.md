# CodeContext Roadmap

## Phase 1 — Repository Ingestion

- Define repository upload and storage workflow
- Implement file discovery and supported file filtering
- Establish backend project and API scaffolding

## Phase 2 — Code Indexing

- Parse supported source files into chunks
- Generate and store embeddings
- Persist indexed metadata in PostgreSQL

## Phase 3 — Semantic Search

- Enable vector similarity search with pgvector
- Return relevant code chunks for user queries
- Expose search endpoints to the frontend

## Phase 4 — AI-Powered Explanations

- Integrate LLM provider
- Build prompt templates for grounded responses
- Return answers with file references

## Phase 5 — Advanced Developer Tools

- Improve retrieval quality and context selection
- Add richer project exploration features
- Optimize cost and performance (caching, reuse)

