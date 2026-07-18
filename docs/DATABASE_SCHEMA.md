# CodeContext Database Schema

## Overview

Persistent storage for CodeContext across three responsibilities:

1. **Repository indexing** — projects, files, chunks, embeddings
2. **Semantic search** — vector storage and nearest-neighbor retrieval
3. **Conversations** — chat history scoped to a project

MVP workflow: upload → index → search → ask questions → grounded answers with file references. No user accounts, versioning, or job orchestration in MVP—room left for later.

**Related documentation:** [Architecture Overview](ARCHITECTURE.md#overview) · [AI Pipeline](AI_PIPELINE.md#overview) · [Roadmap](ROADMAP.md#codecontext-roadmap)

---

# Database Technology

## PostgreSQL

Primary relational store for hierarchical repo data, conversation history, indexing status, and source-reference metadata.

## pgvector

Vector similarity search over code chunk embeddings. Question embeddings are computed at query time and compared against stored vectors. See [Vector Retrieval](AI_PIPELINE.md#vector-retrieval) and [Vector Database](ARCHITECTURE.md#vector-database).

## Why relational metadata and vectors belong together

- **Traceability:** join vectors → chunks → files → projects in one query
- **Scoped search:** limit similarity search to a project or file set
- **Source references:** paths and locations available in the retrieval path
- **Simplicity:** one database for MVP
- **Consistency:** transactional updates across content and embeddings

Standalone vector DBs may help at scale; colocation is the MVP starting point.

---

# Core Entities

Six entities in two domains: indexed repository data and project conversations.

## Project

Top-level container for one uploaded repository. Anchors [ingestion](AI_PIPELINE.md#repository-ingestion), [chunking](AI_PIPELINE.md#chunking-strategy), [embeddings](AI_PIPELINE.md#embeddings), [search](AI_PIPELINE.md#vector-retrieval), and [chat](AI_PIPELINE.md#llm-response-generation).

**Fields:** id, name, description (optional), source info (upload), indexing status, created/last-indexed timestamps, optional file counts

**Relationships:** one Project → many Files, many Conversations. No user ownership in MVP.

## File

Metadata for one discovered repository file; links structure to chunks and file references.

**Fields:** relative path, type/language, size, content hash (optional), indexing status, timestamps

Raw content may live on disk/object storage; DB retains lookup metadata. See [Repository Ingestion](AI_PIPELINE.md#repository-ingestion).

**Relationships:** many Files → one Project

## Code Chunk

Searchable file segment—the retrieval unit. Holds chunk text and metadata for search and references.

**Why chunks exist:** files are too large to embed or fit in context whole; splitting improves precision and lowers cost. See [Chunking Strategy](AI_PIPELINE.md#chunking-strategy).

**Fields:** chunk text, start/end lines or structural label, chunk index, token/char count, optional structural hint (function, class, section)

**Relationships:** many Code Chunks → one File

## Embedding

Vector representation of a chunk for semantic search. Created at [indexing](AI_PIPELINE.md#embeddings); reused until content changes.

**Fields:** vector values, model identifier, dimensions, created timestamp

**Relationships:** one Embedding → one Code Chunk (MVP). Separate entity supports future re-embedding with different models.

## Conversation

Chat session scoped to one Project; supports the [frontend chat UI](ARCHITECTURE.md#frontend).

**Fields:** title (optional), created/last-activity timestamps, status (active/archived)

**Relationships:** many Conversations → one Project. No user identity in MVP.

## Message

One user question or assistant response in a conversation.

**Fields:** role (user/assistant), content, timestamp, source references (assistant), optional retrieval metadata

Assistant messages are grounded in retrieved context. See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation).

**Relationships:** many Messages → one Conversation (ordered)

---

# Entity Relationships

```
Indexing:  Project → File → Code Chunk → Embedding
Chat:      Project → Conversation → Message
```

Supports [ingestion](AI_PIPELINE.md#pipeline-flow) through vector storage and [query](AI_PIPELINE.md#vector-retrieval) back to [file references](AI_PIPELINE.md#llm-response-generation). Assistant messages may reference retrieved Files/Chunks without merging the hierarchies.

**Runtime query flow:**

1. Identify [Project](#project) and [Conversation](#conversation)
2. Embed question; search [Embeddings](#embedding) scoped to Project
3. Retrieve [Code Chunks](#code-chunk) and parent [Files](#file)
4. LLM generates [Message](#message) with file references

Indexing data stays stable and reusable; conversations are append-only history.

---

# Future Considerations

## Users and authentication

User ownership and access control on projects and conversations.

## Repository versions

Multiple indexed snapshots per repository over time.

## File change tracking

Hash-based incremental re-indexing of changed files only. See [Reusing embeddings](AI_PIPELINE.md#reusing-embeddings).

## Indexing jobs

Background workers for long-running ingestion, retries, and progress. See [Background indexing jobs](AI_PIPELINE.md#background-indexing-jobs).

## Permissions

Project roles, shared access, read-only viewers, audit trails.

Future additions extend—not replace—the Project → File → Code Chunk → Embedding and Project → Conversation → Message chains.
