# CodeContext Roadmap

**Related documentation:** [Architecture](ARCHITECTURE.md#overview) · [AI Pipeline](AI_PIPELINE.md#overview) · [Database Schema](DATABASE_SCHEMA.md#overview) · [Project Status](PROJECT_STATUS.md#project-status)

## Phase 1 — Repository Ingestion

- Upload/storage workflow
- [File discovery and filtering](AI_PIPELINE.md#repository-ingestion)
- [Backend API scaffolding](ARCHITECTURE.md#backend-api)
- [Project](DATABASE_SCHEMA.md#project) and [File](DATABASE_SCHEMA.md#file) persistence

## Phase 2 — Code Indexing

- [Parse and chunk files](AI_PIPELINE.md#code-parsing)
- [Generate embeddings](AI_PIPELINE.md#embeddings)
- [Code Chunk](DATABASE_SCHEMA.md#code-chunk) and [Embedding](DATABASE_SCHEMA.md#embedding) records in [PostgreSQL](DATABASE_SCHEMA.md#postgresql)

## Phase 3 — Semantic Search

- [pgvector similarity search](AI_PIPELINE.md#vector-retrieval)
- Return relevant chunks; expose search API to [frontend](ARCHITECTURE.md#frontend)

## Phase 4 — AI-Powered Explanations

- [LLM integration](ARCHITECTURE.md#llm-layer)
- [Grounded prompt templates](AI_PIPELINE.md#llm-response-generation)
- [Conversation](DATABASE_SCHEMA.md#conversation) and [Message](DATABASE_SCHEMA.md#message) persistence
- Answers with [file references](AI_PIPELINE.md#llm-response-generation)

## Phase 5 — Advanced Developer Tools

- Better retrieval and context selection
- Richer project exploration
- [Cost optimization](AI_PIPELINE.md#cost-optimization)
- [Future pipeline](AI_PIPELINE.md#future-improvements) and [schema](DATABASE_SCHEMA.md#future-considerations) enhancements
