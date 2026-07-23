# CodeContext Roadmap

CodeContext helps developers understand project content—code, docs, and other indexed sources—by ingesting multiple source types into **owned projects**, indexing for semantic search, and answering questions with grounded AI responses and file citations.

This document defines **direction and scope**. For what is done and in flight today, see [Project Status](PROJECT_STATUS.md).

---

## Phase 1 — Repository Ingestion

**Goal:** Bring content into user-owned projects and browse what was indexed.

**Features (shipped):**

- **User accounts** with JWT authentication; projects owned by users
- **Project sources** tracking (Git, ZIP, file imports)
- **ZIP upload**, **public Git URL import**, **individual files** (Markdown, text, text-based PDF)
- Source-agnostic ingestion pipeline (`Importer` → `ExtractedDocument`)
- Recursive discovery, filters, `.gitignore` respect
- Persist file metadata and content per project

**Outcome:** A signed-in user creates a project, imports one or more sources, and browses discovered files in that workspace.

---

## Phase 2 — Code Indexing

**Goal:** Prepare project content for intelligent search.

**Features:**

- Language-aware parsing (where applicable)
- Code and document chunking
- Optional embedding generation
- Vector storage (pgvector)

**Outcome:** Project content becomes searchable by meaning, not just filenames.

---

## Phase 3 — Semantic Search

**Goal:** Find relevant content using natural language.

**Features:**

- Vector similarity search
- Result ranking
- Search API and UI (authenticated, project-scoped)
- Context retrieval for downstream AI

**Outcome:** Users search within a project and quickly find relevant files and snippets.

---

## Phase 4 — AI Code Assistant

**Goal:** Answer questions about a project’s indexed content.

**Features:**

- LLM integration
- Retrieval-augmented generation (RAG)
- Source citations
- Conversation history *(not yet implemented)*

**Outcome:** Users ask questions and get grounded answers linked to real project files and documents.

---

## Phase 5 — Advanced Developer Tools

**Goal:** Improve project understanding at scale.

**Features:**

- Repository maps and navigation
- Dependency and relationship insights
- Stronger retrieval strategies
- Background indexing and performance tuning

**Outcome:** CodeContext feels like a complete AI workspace for exploring large, multi-source projects.

---

## Platform (cross-cutting)

**Authentication & ownership (shipped):** Registration, login, JWT bearer API, bcrypt password hashing, project ownership enforcement, authenticated frontend workflow.

**Still planned at platform level:** Production deployment guidance, private Git credentials, re-index without full re-import, streaming, and multi-turn chat history.
