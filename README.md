# The Lenny Growth Assistant

> Evidence-grounded product and growth copilot powered by Lenny's Podcast transcripts.

<img width="1918" height="967" alt="image" src="https://github.com/user-attachments/assets/e33c3f33-6289-427f-803d-bb28e610a8b3" />

<img width="1920" height="970" alt="image" src="https://github.com/user-attachments/assets/488501bb-fda0-47d3-89a8-d29195ed1344" />


## 1. What this is

The Lenny Growth Assistant is a full-stack AI product that turns Lenny's Podcast knowledge into three practical workflows:

- **ASK** — grounded product/growth Q&A with session memory and transcript source tracing.
- **CREATE** — a dedicated Ship 30 for 30 writing skill that turns retrieved evidence into a practical essay.
- **BUILD** — generated decision artifacts rendered beside the conversation in a sandboxed viewer.

The product is designed as a small forward-deployment engagement: the evaluator should be able to understand the problem, run the system, inspect the evidence trail, diagnose failures, and extend the architecture without understanding prompt engineering.

## 2. Why it exists

Product and growth teams often have large amounts of expert content but struggle to turn it into a decision at the moment of need. The assistant removes the need to search transcripts manually or understand model infrastructure.

The product optimizes for:

1. **Trust** — retrieved evidence and source metadata are visible.
2. **Actionability** — answers end in practical next steps rather than generic summaries.
3. **Continuity** — each session preserves its own conversation context.
4. **Reuse** — answers can become essays or structured artifacts.
5. **Operability** — health endpoints, configuration, logs, tests, and documented failure modes are included.

## 3. Architecture at a glance

```text
                         ┌─────────────────────────┐
                         │       React UI          │
                         │ Ask / Sources / Artifact│
                         └────────────┬────────────┘
                                      │ HTTP/JSON
                         ┌────────────▼────────────┐
                         │       FastAPI API       │
                         │ sessions / messages /   │
                         │ artifacts / health      │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────▼───┐  ┌──▼────────────────┐
                    │ Agent / Skills │  │ Artifact Security │
                    │ Router         │  │ sanitize + iframe │
                    └───────┬────────┘  └───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Hybrid Retrieval│
                    │ semantic + FTS  │
                    └───────┬────────┘
                            │
                ┌───────────▼────────────┐
                │ PostgreSQL + pgvector  │
                │ sessions/messages/docs │
                │ chunks/artifacts/logs  │
                └───────────┬────────────┘
                            │
              ┌─────────────┴──────────────┐
              │                            │
       ┌──────▼──────┐              ┌──────▼─────────┐
       │ Ollama      │              │ Anthropic      │
       │ qwen3:4b    │              │ Claude SDK/API │
       │ mandatory   │              │ cloud option   │
       └─────────────┘              └────────────────┘
```

## 4. Tech stack

### Frontend
- React
- TypeScript
- Vite
- Lucide React
- Sandboxed iframe artifact viewer

### Backend
- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy async
- asyncpg
- Alembic
- structlog
- httpx

### AI
- Ollama for the required local demo
- `qwen3:4b` for local generation
- `nomic-embed-text` for 768-dimensional embeddings
- Anthropic Python SDK
- Anthropic Claude Agent SDK integration with a custom retrieval tool

### Data
- PostgreSQL 16
- pgvector
- Full-text search using PostgreSQL FTS

## 5. Knowledge base

The knowledge base is built from a Lenny's Podcast transcript repository.

Current ingestion result:

- **269 documents**
- **6,076 chunks**
- **768-dimensional embeddings**
- Source metadata retained with each chunk

Each chunk retains provenance such as:

- episode ID
- guest
- episode title
- source URL
- chunk ID/content

### Ingestion flow

```text
Transcript repository
        ↓
Parse metadata + transcript
        ↓
Normalize text
        ↓
Chunk transcript
        ↓
Generate embeddings with nomic-embed-text
        ↓
Store document + chunk + embedding
        ↓
Create vector / FTS indexes
```

### Retrieval flow

```text
User query
   ↓
query normalization
   ↓
semantic vector retrieval
   +
PostgreSQL full-text retrieval
   ↓
70% semantic + 30% keyword score
   ↓
episode diversification
   ↓
top evidence
   ↓
grounded agent prompt
   ↓
answer + source metadata
```

## 6. LLM configuration

The selected provider is configuration-driven.

Example:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen3:4b
```

Cloud configuration is also supported:

```env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=
```

The UI displays the selected provider/model.

### Local demo

Ollama is the recommended demo provider because it satisfies the assignment's mandatory local-model requirement and avoids depending on cloud credits.

Claude Agent SDK integration is implemented, but the live cloud-agent test reached Anthropic and returned an insufficient-credit response. Therefore this repository does not claim a successful Claude generation demo.

## 7. Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop
- Ollama

Install the local models:

```powershell
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

### Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### Environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Never commit `.env`.

Important local values:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

For Docker backend containers, use:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7775cf7a-23da-44d8-86e4-c329b6d0173c" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a6307075-9d2c-43aa-8cb8-4b251a0122ab" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9f19f665-de71-4012-9d6d-02d0a5e28f3f" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/c022a81a-5564-4d76-aa57-90a59c3fcd4f" />



## 8. Run locally

### Start PostgreSQL

```powershell
docker compose up -d postgres
```

### Start backend

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

### Start frontend

```powershell
cd frontend
npm install
npm run dev
```

Vite may select port 5173 or 5174 if the first port is occupied.

The frontend API base is currently:

```text
http://127.0.0.1:8000
```

If the frontend runs on 5174, ensure CORS contains both:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

## 9. Docker

The intended reproducible startup path is:

```powershell
docker compose up -d
```

Then:

```powershell
docker compose ps
```

Check backend health:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

Check system status:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/system/status"
```

## 10. API

### Health

```text
GET /health
```

Returns application and database health.

### System status

```text
GET /api/system/status
```

Reports:

- provider
- model
- database
- retrieval configuration
- artifact sanitization

### Sessions

```text
POST /api/sessions
GET  /api/sessions
GET  /api/sessions/{session_id}
GET  /api/sessions/{session_id}/messages
```

### Messages

```text
POST /api/sessions/{session_id}/messages
```

### Artifacts

```text
POST /api/sessions/{session_id}/artifacts
GET  /api/artifacts/{artifact_id}
```

## 11. Artifact security

Generated HTML is treated as untrusted.

The backend sanitizer:

- removes `script`
- removes `iframe`
- removes `object`
- removes `embed`
- removes `applet`
- removes `form`
- removes `base`
- removes `meta`
- removes `link`
- removes inline event handlers such as `onclick`
- removes dangerous `javascript:`, `vbscript:`, and `data:` URL schemes
- removes `srcdoc`
- fails closed if sanitization encounters an unexpected parser error

The frontend adds a second defense:

```html
<iframe sandbox="">
```

No script, same-origin, forms, popups, downloads, or external execution permissions are granted.

This is defense in depth: sanitization reduces dangerous markup before display, while iframe sandboxing limits the execution environment.

## 12. Ship 30 skill

The Ship 30 workflow is implemented as a dedicated skill in:

```text
backend/app/skills/ship30.py
```

The skill:

1. retrieves transcript evidence
2. injects evidence into a dedicated writing prompt
3. asks for approximately 1,250 words
4. requires a hook
5. requires narrative progression
6. uses headings/bullets/selective emphasis
7. requires a specific takeaway
8. requires transcript-grounded claims
9. validates output length

An independent local test produced a successful essay in the expected range using Ollama.

## 13. Agent architecture

The agent layer is intentionally separated into:

- provider abstraction
- retrieval tool
- growth/Q&A agent
- Ship30 skill
- artifact generator

The Claude Agent SDK integration exposes a custom retrieval tool through an SDK MCP server. This keeps knowledge retrieval outside the model's private world knowledge and makes the source boundary explicit.

## 14. Session context

A session contains:

- UUID
- title
- mode
- timestamps

Messages contain:

- UUID
- session UUID
- role
- content
- timestamp

The growth agent includes recent conversation history with the current retrieval context. This allows follow-up questions such as:

```text
User: How should I find product-market fit?

User: What should I do next?
```

to remain within the same decision context.

## 15. Error handling

The application is designed to handle:

- empty user messages
- missing provider/model configuration
- unavailable Ollama
- Ollama timeouts
- empty model responses
- empty retrieval
- missing sessions
- database failures
- invalid artifact requests
- unsafe generated HTML

API errors use structured HTTP responses rather than exposing raw stack traces to users.

## 16. Observability

Useful diagnostic information includes:

- health status
- provider/model
- retrieval latency
- semantic/keyword candidate counts
- final evidence count
- artifact sanitization status

Retrieval tests print metrics such as:

```text
semantic=8 keyword=0 combined=8 final=5 latency_ms=...
```

## 17. Tests

Important tests include:

```powershell
python backend\test_embeddings_batch.py
python backend\test_retrieval.py
python backend\test_ollama_provider.py
python backend\test_growth_agent.py
python backend\test_ship30.py
python backend\test_sanitizer.py
python -m pytest
```

Manual UI checklist:

1. Open the frontend.
2. Confirm provider/model is visible.
3. Confirm API becomes Healthy.
4. Ask a PMF question.
5. Confirm an answer appears.
6. Confirm Evidence Trail appears.
7. Ask a follow-up.
8. Confirm session context is preserved.
9. Generate Decision Canvas.
10. Confirm artifact appears beside chat.
11. Confirm Sanitized indicator.
12. Confirm artifact is rendered in sandboxed iframe.
13. Create a new session.
14. Confirm the previous session remains independent.

## 18. Known limitations

### Citation numbering

Retrieved evidence is returned by the API with authoritative source metadata. The local Qwen model has occasionally produced citation labels that do not match the server's retrieved source numbering. This is a known limitation and should be addressed before treating model-generated inline citation numbers as authoritative.

The UI therefore emphasizes the server-returned Evidence Trail as the source-of-truth provenance layer.

### Cloud Claude

The Claude Agent SDK integration is implemented, but the live cloud test was blocked by insufficient Anthropic credit. Ollama is the verified demo provider.

### Local model latency

A 4B local model can take longer for long-form generation. Ollama requests therefore use a generous read timeout.

## 19. Trade-offs

### PostgreSQL + pgvector instead of a separate vector database

Chosen because the application already needs PostgreSQL for persistence. Keeping vectors, FTS, metadata, sessions, and artifacts in one database reduces operational complexity.

### Hybrid retrieval instead of vector-only retrieval

Semantic search handles conceptual similarity; PostgreSQL FTS helps with exact terms and names. Combining them gives a more robust baseline without introducing another service.

### Local Ollama as demo default

This makes the demo reproducible and satisfies the local-model requirement, but the quality/latency trade-off is worse than a larger cloud model.

### Sanitization + sandbox instead of trusting generated HTML

Generated artifacts are untrusted. Two defensive layers are inexpensive and easy for a client engineer to understand.

## 20. Handoff

A new engineer should be able to:

1. clone the repository
2. copy `.env.example` to `.env`
3. install prerequisites
4. start PostgreSQL/Ollama
5. run the backend
6. run the frontend
7. verify `/health`
8. verify `/api/system/status`
9. run the tests
10. inspect the retrieval and artifact code
11. extend a skill or provider without rewriting the application

## 21. Demo narrative

A 2–3 minute demo should show:

1. The product problem.
2. A grounded PMF question.
3. The Evidence Trail.
4. A follow-up question demonstrating session context.
5. Ship 30 generation.
6. Decision Canvas artifact rendering.
7. Visible `ollama / qwen3:4b`.
8. One security/architecture trade-off.
9. Final statement about customer-facing forward deployment.

## 22. Repository hygiene

Before pushing:

```powershell
git status
git add .
git commit -m "feat: complete Lenny growth assistant"
```

Confirm `.env` is ignored and no API key is present in tracked files.







------------------------
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r backend/requirements.txt

python -m py_compile backend\app\models\message.py

python -m py_compile backend\app\models\document.py

python -c "import sys; sys.path.insert(0, 'backend'); from app.db.base import Base; from app.models.session import Session; from app.models.message import Message; from app.models.document import Document; print(Base.metadata.tables.keys())"

python -c "import sys; sys.path.insert(0, 'backend'); from app.db.base import Base; from app.models.session import Session; from app.models.message import Message; from app.models.document import Document; from app.models.chunk import Chunk; print(Base.metadata.tables.keys())"

python -m alembic init backend\alembic

Then display the answer:

$response.message.content

Display the provider:

$response.provider

Display the model:

$response.model

And display the sources:

$response.sources
---------------------------

python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000


Then in another PowerShell:

Invoke-RestMethod http://127.0.0.1:8000/health | ConvertTo-Json

Then:

Invoke-RestMethod http://127.0.0.1:8000/api/system/status | ConvertTo-Json



cd frontend
npm install
npm install lucide-react
npm run dev

npm run build - connect react

