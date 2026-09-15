# Agent / Development Transcript Log

This log records representative implementation attempts, failures, corrections, and validation steps. Secrets and API keys are intentionally omitted.

## 1. Project foundation

### Attempt

Created the application structure:

```text
backend/
frontend/
data/
docs/
scripts/
skills/
tests/
```

### Correction

Kept backend concerns separated into API, models, providers, retrieval, agents, skills, and artifacts.

---

## 2. PostgreSQL + pgvector

### Attempt

Started PostgreSQL using:

```text
pgvector/pgvector:pg16
```

### Issue

The host already had PostgreSQL on port 5432.

### Correction

Mapped Docker PostgreSQL to host port 15432.

Verified:

```text
PostgreSQL connection succeeded
pgvector version 0.8.6
```

---

## 3. Alembic

### Issue

Initial migration tooling required a PostgreSQL driver.

### Correction

Installed the required driver and applied the initial migration.

---

## 4. Transcript ingestion

### Attempt

Ingested the Lenny transcript repository.

### Issue

The parser/chunker initially handled some transcript headings/metadata incorrectly.

### Correction

Adjusted parsing and heading detection.

The ingestion was rerun.

### Result

```text
269 documents
6076 chunks
768-dimensional embeddings
```

---

## 5. Embeddings

### Attempt

Used Ollama `nomic-embed-text`.

### Validation

Batch embedding test:

```text
3 texts → 3 embeddings
768 dimensions
```

---

## 6. Retrieval

### Implementation

Hybrid retrieval:

```text
semantic + PostgreSQL FTS
70% semantic
30% keyword
```

### Validation

Retrieval test returned multiple relevant PMF episodes and reported latency/candidate counts.

---

## 7. Growth agent prompt

### Failure

The local model initially responded as though no user question had been supplied.

Example failure:

```text
I don't see a specific user question...
```

### Cause

The prompt structure made the evidence block more prominent than the explicit question.

### Correction

Added a clearly labeled:

```text
USER QUESTION
```

section and explicit instruction to answer it directly.

### Result

The agent produced a substantive PMF answer.

---

## 8. Citation mismatch

### Observed failure

The server returned retrieved sources in one order, while the local model sometimes labeled its prose citations with a different source number.

### Decision

Do not silently claim that model-generated citation numbers are authoritative.

The UI's Evidence Trail uses server-returned retrieval metadata as the provenance source of truth.

### Future correction

Introduce a server-side citation normalization layer or stable source IDs in generated output.

---

## 9. Claude Agent SDK

### Attempt

Implemented:

```text
ClaudeAgentOptions
custom retrieval tool
SDK MCP server
max turns
```

### Failure

The live cloud call reached Anthropic but returned:

```text
Credit balance is too low
```

### Decision

Keep the integration implemented and use Ollama for the required demo.

No API key or secret is stored in the repository.

---

## 10. Ship30 skill

### Initial failure

The test initially failed because the dedicated skill module was missing/not imported correctly.

### Correction

Created:

```text
backend/app/skills/ship30.py
```

### Second failure

Long-form generation exceeded the original HTTP read timeout.

### Correction

Increased Ollama read timeout to 600 seconds with explicit timeout/request error handling.

### Result

Ship30 test passed using Ollama.

Observed output:

```text
Provider: ollama
Model: qwen3:4b
Word count: 1043
```

The output contained hook, narrative sections, practical guidance, and source section.

---

## 11. Artifact sanitizer

### Goal

Generated HTML is untrusted.

### Test payload

Contained:

- script
- iframe
- onclick
- javascript URL
- safe headings/buttons/text

### Result

Dangerous content was removed while safe content remained.

```text
SANITIZER TEST PASSED
```

---

## 12. Artifact model/API

### Failure

Artifact router initially imported models from:

```text
app.db.models
```

but the actual project structure stores models under:

```text
app.models
```

### Correction

Updated imports to:

```python
from app.models.artifact import Artifact
from app.models.session import Session
```

### Result

Artifact API import passed.

---

## 13. FastAPI routes

### Initial issue

A route inspection test assumed every route object exposed `.path`.

### Correction

Changed route inspection to safely inspect included router objects.

### Result

Confirmed routes include:

```text
/api/sessions
/api/sessions/{session_id}
/api/sessions/{session_id}/messages
/api/sessions/{session_id}/artifacts
/api/artifacts/{artifact_id}
/health
/api/system/status
```

---

## 14. Backend health

Validated:

```text
GET /health
```

Result:

```json
{
  "status": "ok",
  "service": "lenny-growth-assistant",
  "environment": "development",
  "database": "healthy"
}
```

System status:

```json
{
  "status": "ok",
  "provider": "ollama",
  "model": "qwen3:4b",
  "database": "healthy",
  "retrieval": "configured",
  "artifact_sanitization": true
}
```

---

## 15. Session context

### Test

Asked:

```text
How should an early-stage startup find product-market fit?
```

Then asked a follow-up about the 25% very-disappointed case.

### Result

The second request used the same session's prior conversation context.

---

## 16. React frontend

### Initial issue

The Vite scaffold command detected that `frontend` was not empty.

### Correction

Completed the React/TypeScript scaffold rather than overwriting the existing directory blindly.

### Additional issue

The frontend started on:

```text
localhost:5174
```

because 5173 was occupied.

### CORS issue

Backend CORS originally allowed only:

```text
http://localhost:5173
```

### Correction

Allowed:

```text
http://localhost:5173,http://localhost:5174
```

### React lint issue

React's current lint rules flagged:

```text
react-hooks/immutability
react-hooks/exhaustive-deps
react-hooks/set-state-in-effect
```

### Correction

Refactored data-loading functions using `useCallback` and scoped the initialization lint exception to the mount-time API loading effect.

---

## 17. Current known limitations

1. Local model can produce formatting/spacing artifacts.
2. Model-generated source numbering can mismatch server retrieval ordering.
3. Claude cloud generation could not be demonstrated because the API account had insufficient credit.
4. Docker/Ollama connectivity depends on the host Ollama service being available.

These limitations are documented rather than hidden.
