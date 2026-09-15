# Architecture — The Lenny Growth Assistant

## 1. System overview

The system is a layered full-stack application:

```text
React + TypeScript
       │
       │ HTTP/JSON
       ▼
FastAPI
       │
       ├─────────────── Session / Message APIs
       │
       ├─────────────── Artifact API
       │
       └─────────────── Agent Router
                              │
                              ├── Growth Q&A
                              ├── Ship30 Skill
                              └── Artifact Generator
                                      │
                                      ▼
                              Provider abstraction
                                │            │
                              Ollama       Claude
                                │
                                ▼
                           Model generation

Retrieval:
Query → semantic + FTS → combined score → diversify → evidence

Persistence:
PostgreSQL + pgvector
```

## 2. Component boundaries

### `backend/app/api`

HTTP boundary.

Responsibilities:

- request validation
- response schemas
- session/message/artifact routes
- HTTP error handling

### `backend/app/agents`

Agent boundary.

Responsibilities:

- intent routing
- grounded Q&A
- Agent SDK runtime
- retrieval tool

### `backend/app/skills`

Dedicated task skills.

Current:

```text
ship30.py
```

### `backend/app/retrieval`

Knowledge boundary.

Responsibilities:

- embedding generation
- semantic search
- keyword search
- hybrid ranking
- context formatting

### `backend/app/providers`

LLM boundary.

```text
base.py
ollama.py
claude.py
factory.py
```

Application code does not need to know the provider-specific HTTP/API contract.

### `backend/app/artifacts`

Artifact security/generation.

```text
generator.py
sanitizer.py
```

### `backend/app/models`

Persistence models.

## 3. Database

### Sessions

```text
sessions
---------
id UUID PK
title
mode
created_at
updated_at
```

### Messages

```text
messages
--------
id UUID PK
session_id UUID FK
role
content
created_at
```

### Documents

Stores transcript-level metadata.

Representative fields:

```text
id
episode_id
title
guest
source_url
metadata
```

### Chunks

Stores retrieval units.

Representative fields:

```text
id
document_id
chunk_index
content
embedding vector(768)
episode_id
guest
source_url
```

Indexes include:

- vector index
- FTS GIN index
- guest index
- episode index

### Artifacts

```text
artifacts
---------
id UUID PK
session_id UUID FK
title
artifact_type
content_format
content
sanitized_content
created_at
updated_at
```

### Retrieval logs

Stores/records retrieval diagnostics where configured.

## 4. Knowledge ingestion

```text
Raw transcript
    ↓
Metadata parser
    ↓
Text normalization
    ↓
Chunker
    ↓
Embedding service
    ↓
PostgreSQL
```

The ingestion process is designed to be repeatable.

The current corpus contains 269 documents and 6,076 chunks.

## 5. Retrieval

### Step 1 — Normalize

Strip accidental formatting noise and normalize query text.

### Step 2 — Semantic search

Embed the query using `nomic-embed-text`.

Compare against stored vectors using cosine distance.

### Step 3 — Keyword search

PostgreSQL FTS provides lexical matching.

### Step 4 — Combine

Current baseline:

```text
70% semantic
30% keyword
```

### Step 5 — Diversify

Prefer evidence from different episodes before filling remaining slots.

This reduces the risk that the answer is dominated by one episode.

### Step 6 — Format evidence

Every evidence item is passed with:

```text
source number
title
guest
episode ID
source URL
relevance
evidence text
```

## 6. Grounded agent

The growth agent receives:

1. system grounding policy
2. retrieved evidence
3. recent conversation
4. current user question

The system prompt explicitly tells the model:

- answer the actual question
- use supplied evidence
- do not invent facts
- distinguish synthesis from direct evidence
- acknowledge insufficient evidence

## 7. Agent SDK integration

Claude Agent SDK integration is implemented through:

```text
claude_runtime.py
tools.py
```

A custom retrieval tool is exposed through an SDK MCP server.

Conceptually:

```text
Claude Agent
     │
     └── retrieve_knowledge(query)
                 │
                 ▼
           HybridRetriever
                 │
                 ▼
           PostgreSQL/pgvector
```

This gives the agent an explicit knowledge-access mechanism instead of assuming the model knows the corpus.

## 8. Provider abstraction

```python
class LLMProvider:
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> LLMResponse:
        ...
```

Implementations:

- `OllamaProvider`
- `ClaudeProvider`

Factory:

```text
LLM_PROVIDER=ollama
```

selects Ollama without changing application logic.

## 9. Ship30 architecture

The Ship30 skill is a dedicated module.

```text
Topic
 ↓
HybridRetriever
 ↓
top evidence
 ↓
Ship30 system contract
 ↓
Ollama/Claude
 ↓
word-count validation
 ↓
Ship30 result
```

The skill encodes writing constraints rather than relying on the general Q&A prompt.

## 10. Artifact architecture

```text
Artifact request
      ↓
Retrieve evidence
      ↓
Generate HTML/CSS
      ↓
Strip code fences
      ↓
sanitize_html()
      ↓
persist original + sanitized
      ↓
React iframe sandbox
```

## 11. Artifact security

Blocked:

- script
- iframe
- object
- embed
- applet
- form
- base
- meta
- link
- event handlers
- dangerous URL schemes
- srcdoc

Defense in depth:

```text
Untrusted model output
       ↓
HTML sanitizer
       ↓
sandbox=""
       ↓
Browser rendering
```

The iframe is not granted `allow-scripts` or `allow-same-origin`.

## 12. API contracts

### Create session

```text
POST /api/sessions
```

Request:

```json
{
  "title": "New Lenny Session",
  "mode": "ask"
}
```

### Send message

```text
POST /api/sessions/{session_id}/messages
```

Request:

```json
{
  "content": "How should an early-stage startup find product-market fit?"
}
```

Response contains:

```text
message
provider
model
sources[]
```

### Create artifact

```text
POST /api/sessions/{session_id}/artifacts
```

Request:

```json
{
  "prompt": "Create a product-market fit decision canvas.",
  "artifact_type": "decision_canvas"
}
```

## 13. Health

```text
GET /health
```

Tests basic application/database health.

```text
GET /api/system/status
```

Reports:

```text
status
provider
model
database
retrieval
artifact_sanitization
```

## 14. Failure behavior

### Ollama unavailable

Provider raises a clear runtime error; API returns an error response rather than hanging indefinitely.

### Ollama timeout

Long-form generation uses a generous read timeout and reports a meaningful timeout message.

### Empty retrieval

Agent receives an explicit no-evidence context and is instructed not to fabricate transcript claims.

### Database unavailable

Health endpoint reports unhealthy database status.

### Missing Claude key

Claude provider fails with a configuration error.

### Artifact sanitization failure

Sanitizer fails closed instead of returning untrusted content.

## 15. Deployment topology

Local:

```text
Windows host
│
├── Browser
│    └── React/Vite
│
├── FastAPI
│
├── Ollama
│    ├── qwen3:4b
│    └── nomic-embed-text
│
└── Docker Desktop
     └── PostgreSQL + pgvector
```

Docker backend reaches host Ollama through:

```text
host.docker.internal:11434
```

## 16. Operational trade-offs

### One database

PostgreSQL handles relational persistence, FTS, and vectors. This reduces operational overhead.

### Small local model

qwen3:4b is practical on the development machine but may be slower and less precise than a large cloud model.

### Server-side provenance

Source metadata returned by retrieval is treated as more authoritative than model-generated source numbering.

## 17. Extension points

A future engineer can add:

- another provider
- another skill
- reranking model
- streaming
- authentication
- multi-tenant isolation
- Knowledge Explorer
- artifact editing
- evaluation harness

without changing the core database or API boundaries.
