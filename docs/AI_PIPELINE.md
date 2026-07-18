# CodeContext AI Pipeline

## Overview

The AI pipeline transforms an uploaded repository into a searchable knowledge base and uses an LLM to answer questions about it. LLMs cannot practically receive an entire codebase on every request—context limits, latency, and cost make that infeasible. CodeContext indexes once, stores semantic representations, and retrieves only relevant sections per question.

**MVP scope:** upload repository, index supported files, semantic search, Q&A, grounded answers with file references.

**Related documentation:** [Architecture Overview](ARCHITECTURE.md#overview) · [Database Schema](DATABASE_SCHEMA.md#overview) · [Roadmap](ROADMAP.md#codecontext-roadmap)

---

# Pipeline Flow

```
Repository Upload → File Discovery → File Parsing → Code Chunking
→ Embedding Generation → Vector Storage → Semantic Retrieval
→ Context Assembly → LLM Generation → Response with File References
```

**Ingestion (indexing):** Discover supported files, parse, chunk, embed, store in [PostgreSQL + pgvector](DATABASE_SCHEMA.md#database-technology).

**Query (Q&A):** Embed the question, retrieve similar [code chunks](DATABASE_SCHEMA.md#code-chunk), assemble context, generate an LLM response with source file references.

Indexing runs once per repository; retrieval and generation run per question.

---

# Repository Ingestion

Reads uploaded repositories and identifies files worth indexing.

## Scanning repositories

Walk the directory tree; skip dependency/build folders and binaries; focus on parseable text source and config. MVP uses user uploads only—no VCS integration or continuous sync assumed.

## Identifying supported files

**Initial support:** Python, JavaScript, TypeScript, Markdown, JSON, configuration files.

Store path, type, and size metadata for each accepted file. See [File entity](DATABASE_SCHEMA.md#file). Other files may be ignored early on.

## Why source code needs specialized handling

Code is not flat prose. Meaning lives in syntax, imports, and structure; context spans files; small identifier changes alter behavior; dependencies and generated artifacts add noise without retrieval value. CodeContext treats repositories as structured technical artifacts.

---

# Code Parsing

Converts raw files into indexable structured text.

## Why code should not be chunked like a normal PDF

Fixed-size or paragraph splits break functions, orphan imports, and destroy logical units—returning fragments that look relevant but mislead the LLM and inflate prompt cost.

## Future support for language-specific parsing

MVP may start with file-type-aware extraction; later, language-specific boundaries:

- **Python:** modules, classes, functions
- **JavaScript/TypeScript:** modules, components, exports, functions
- **Markdown:** sections and headings
- **JSON/config:** key groups or whole-file units

## Extracting meaningful units

Target units: functions, classes, modules, UI components, config blocks, doc sections. Preserve file paths and structural hints for traceability. Feeds [chunking](#chunking-strategy), [embedding](#embeddings), and [retrieval](#vector-retrieval).

---

# Chunking Strategy

Splits parsed content into embeddable, retrievable pieces stored as [Code Chunk](DATABASE_SCHEMA.md#code-chunk) records.

## Why large files need to be split

Embeddings and context windows work best on focused passages. Splitting enables precise retrieval and lower LLM cost.

## The importance of preserving context

Each chunk needs coherent meaning **and** enough context to stand alone. Minimum metadata: file path, language/type, line range or structural label.

## Potential chunking strategies for source code

- **Structure-aware:** split at functions, classes, headings
- **Size-bounded fallback:** subdivide oversized units; keep shared metadata/overlap
- **Whole-file:** small config/doc files as one chunk
- **Path/type metadata:** on every chunk for interpretable retrieval

---

# Embeddings

Numerical vectors capturing semantic meaning. Similar meaning → nearby vectors (e.g., "database connection setup" near ORM config or env vars).

## What embeddings represent

Fixed-length vectors for code chunks or user questions.

## Why embeddings are created

Enable search by meaning, not exact keywords—developers ask questions in different terms than the code uses.

## How they enable semantic search

Index time: store chunk vectors in [pgvector](DATABASE_SCHEMA.md#pgvector) with metadata. Query time: embed the question, find nearest neighbors. See [Embedding entity](DATABASE_SCHEMA.md#embedding). Question embeddings need not be persisted for MVP.

---

# Vector Retrieval

Selects chunks most likely to answer a question.

## Converting questions into searches

Embed the question with the same model used at index time; compare against stored chunk vectors.

## Retrieving relevant code chunks

Return ranked chunks with text and source metadata (path, location) for references. Limit results to the LLM context window. Semantic retrieval is the MVP's primary context mechanism.

## Why retrieval reduces LLM costs

Without retrieval, large repo sections must be sent per question. Retrieval narrows input to a relevant subset—lower tokens, better focus.

---

# LLM Response Generation

Generates user-facing answers from retrieved chunks.

## Providing retrieved context to the LLM

Combine question, selected chunks, and grounding instructions. Prompt templates stay separate from retrieval logic for provider swapability.

## Why responses should be grounded in repository information

Answers must reflect the uploaded codebase, not generic assumptions—reducing hallucinated paths and invented APIs. See [Grounded Responses](ARCHITECTURE.md#grounded-responses).

## Why source references are important

MVP responses cite source files for verification, navigation, and trust. References are required, not optional.

---

# Cost Optimization

## Reusing embeddings

Generate at index time; store in the [database](DATABASE_SCHEMA.md#embedding); reuse until chunk content changes.

## Caching responses

Cache LLM or retrieval results per repository; invalidate when indexed content changes.

## Sending only relevant context

Pass only top-ranked chunks—not broad excerpts or unrelated files.

## Using smaller models when possible

Use cheaper models where sufficient; reserve capable models for complex answers. See [Modularity](ARCHITECTURE.md#modularity).

---

# Future Improvements

Post-MVP enhancements (not required for first release):

## AST-based parsing

Reliable structure-aware chunk boundaries for supported languages.

## Hybrid search (keyword + vector)

Better retrieval for exact identifiers, function names, env vars, and paths.

## Repository relationship graphs

Retrieve structurally related code (imports, dependencies) that vector search alone may miss.

## Background indexing jobs

Async workers for large repos and re-indexing. See [Indexing jobs](DATABASE_SCHEMA.md#indexing-jobs).

## Multiple LLM providers

Provider-agnostic pipeline with cost/latency/capability tradeoffs.
