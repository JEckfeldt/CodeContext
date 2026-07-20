# CodeContext Roadmap

CodeContext helps developers understand unfamiliar codebases by ingesting repositories, indexing code for semantic search, and answering questions with grounded AI responses and file references.

This document defines **direction and scope**. For what is done and in flight today, see [Project Status](PROJECT_STATUS.md).

---

## Phase 1 — Repository Ingestion

**Goal:** Upload and process repositories.

**Features:**

- Repository upload (ZIP; Git clone later)
- Project management
- Recursive file discovery
- Supported file filtering and ignores
- Persist file metadata and source content

**Outcome:** User can upload a repository and browse its discovered source files.

---

## Phase 2 — Code Indexing

**Goal:** Prepare repositories for intelligent search.

**Features:**

- Language-aware parsing
- Code chunking
- Embedding generation
- Vector storage (pgvector)

**Outcome:** A repository becomes searchable by meaning, not just filenames.

---

## Phase 3 — Semantic Search

**Goal:** Find relevant code using natural language.

**Features:**

- Vector similarity search
- Result ranking and filtering
- Search API and UI
- Context retrieval for downstream AI

**Outcome:** User can search the codebase and quickly find relevant files and snippets.

---

## Phase 4 — AI Code Assistant

**Goal:** Answer questions about a repository.

**Features:**

- LLM integration
- Retrieval-augmented generation (RAG)
- Source citations
- Conversation history

**Outcome:** User can ask questions and get grounded answers linked to real project files.

---

## Phase 5 — Advanced Developer Tools

**Goal:** Improve repository understanding at scale.

**Features:**

- Repository maps and navigation
- Dependency and relationship insights
- Stronger retrieval strategies
- Background indexing and performance tuning

**Outcome:** CodeContext feels like a complete AI workspace for exploring large codebases.
