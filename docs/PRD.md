# PRD — The Lenny Growth Assistant

## 1. Discovery brief

### User

Primary user: a product manager, growth lead, founder, or product/growth team member who wants to use Lenny's Podcast knowledge to make a concrete decision or produce reusable work.

### Job to be done

> When I face a product or growth decision, help me quickly find relevant expert evidence from Lenny's content, understand the implications, and turn that evidence into an actionable decision, essay, or artifact.

### Pain removed

Today the user must:

- remember which episode discussed the topic
- search transcripts manually
- distinguish relevant evidence from unrelated content
- synthesize multiple perspectives
- turn the answer into a reusable document
- manage formatting and rendering separately

The assistant compresses those steps into one workflow.

## 2. Success metrics

### Primary product metric

**Evidence-grounded task completion rate**

Percentage of evaluation tasks where the assistant:

1. answers the requested question,
2. returns at least one relevant source when evidence exists,
3. preserves context for a follow-up,
4. and produces a useful next action.

Target for the take-home demo: **>= 80% across a manually defined evaluation set.**

### Operational metrics

- `/health` returns healthy when dependencies are available.
- Retrieval latency is visible in diagnostic output.
- Artifact sanitizer test passes.
- Local Ollama generation completes without a cloud dependency.
- A fresh evaluator can run the documented setup.

## 3. Assumptions

1. The primary corpus is Lenny's Podcast transcript material.
2. Users value traceability over a purely conversational answer.
3. The local demo can use a small Ollama model.
4. PostgreSQL is already acceptable as the system of record.
5. Generated HTML is untrusted.
6. Sessions are anonymous in the take-home scope; persistent authentication is intentionally deferred.
7. The evaluator primarily needs a local, reproducible deployment rather than production cloud infrastructure.
8. The model may synthesize across multiple transcript chunks but must not invent unsupported facts.

## 4. Scope

### Included

- FastAPI backend
- PostgreSQL persistence
- pgvector retrieval
- transcript ingestion
- hybrid retrieval
- independent sessions
- conversational follow-ups
- Ollama local model
- Anthropic provider/configuration
- Claude Agent SDK retrieval-tool integration
- dedicated Ship30 skill
- artifact generation
- HTML sanitization
- sandboxed artifact viewer
- health/system-status endpoints
- automated tests
- operational documentation

### Intentionally excluded

- full user authentication
- billing
- multi-tenant permissions
- production cloud deployment
- real-time streaming tokens
- collaborative editing
- external artifact publishing

These are intentionally excluded to preserve a reliable end-to-end core within the take-home time constraint.

## 5. Product principles

### Trust before cleverness

Every answer should be anchored in retrieved evidence where available.

### Make the evidence visible

Source metadata should be accessible without asking the user to inspect prompts.

### Optimize for decisions

The assistant should help users decide what to do next, not merely summarize transcripts.

### Keep modes explicit

ASK, CREATE, and BUILD have different output contracts.

### Fail honestly

When evidence is insufficient, the system should say so instead of inventing an answer.

## 6. User flows

### Flow A — Ask

```text
Open app
  ↓
Create/select session
  ↓
Ask question
  ↓
Retrieve evidence
  ↓
Generate grounded response
  ↓
Show Evidence Trail
  ↓
Ask follow-up
  ↓
Continue same session
```

### Flow B — Ship 30

```text
Question/topic
  ↓
Retrieve transcript evidence
  ↓
Ship30Skill
  ↓
Hook + narrative + skimmable structure
  ↓
~1,250-word essay
  ↓
Rendered artifact
```

### Flow C — Decision Canvas

```text
Conversation/context
  ↓
Artifact request
  ↓
Retrieve evidence
  ↓
Generate HTML/CSS
  ↓
Sanitize
  ↓
Sandboxed iframe
  ↓
Artifact Viewer beside chat
```

## 7. Acceptance criteria

### Conversational assistant

- User can create a new session.
- Sessions have independent context.
- User messages are persisted.
- Assistant messages are persisted.
- Follow-up questions use prior conversation context.
- Retrieved evidence is visible.
- Unsupported questions are not answered with fabricated transcript claims.

### Model configuration

- Provider/model are configurable.
- Ollama is supported.
- Ollama is used for the local demo.
- A cloud provider is integrated.
- Provider/model are visible to the evaluator.

### Knowledge base

- Transcript data is ingested.
- Chunks are indexed.
- Embeddings are stored.
- Retrieval returns source metadata.
- Source URL is retained.

### Ship30

- Dedicated skill exists.
- Output targets approximately 1,250 words.
- Hook exists.
- Narrative progression exists.
- Output is skimmable.
- Takeaway is specific.
- Claims are grounded in retrieved evidence.

### Artifacts

- HTML/CSS can be generated.
- Artifact is persisted.
- Artifact is shown beside chat.
- Generated HTML is sanitized.
- Viewer uses sandboxing.
- Unsafe tags/attributes are blocked.

### Operations

- `/health` exists.
- `/api/system/status` exists.
- Configuration is documented.
- `.env.example` contains safe defaults.
- Secrets are not committed.
- Tests exist.
- Troubleshooting is documented.

## 8. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hallucination | High | Retrieval-first prompts + evidence trail |
| Incorrect citations | High | Server-returned source metadata is authoritative |
| Local model quality | Medium | Small model for demo; provider abstraction |
| Local latency | Medium | Generous timeout + visible status |
| Cloud cost | Medium | Ollama default |
| Unsafe HTML | High | Sanitizer + sandboxed iframe |
| DB failure | High | Health endpoint + structured API errors |
| Empty retrieval | High | Explicit insufficient-evidence behavior |
| Stale corpus | Medium | Re-runnable ingestion pipeline |
| Data leakage | High | No secrets in repository; generated HTML isolation |

## 9. Implementation plan

### Phase 1 — Foundation

- FastAPI
- configuration
- PostgreSQL
- Alembic
- models
- health endpoints

### Phase 2 — Knowledge

- transcript ingestion
- chunking
- embeddings
- pgvector
- FTS
- hybrid retrieval

### Phase 3 — Agent

- provider abstraction
- Ollama
- Claude provider
- Agent SDK retrieval tool
- growth agent
- Ship30 skill

### Phase 4 — Product

- sessions
- message API
- artifact API
- React UI
- Evidence Trail
- Artifact Viewer

### Phase 5 — Security and handoff

- sanitizer
- iframe sandbox
- tests
- Docker
- README/docs
- demo

## 10. Product decisions

### Why evidence trail?

Because the main customer problem is not just generating an answer. It is knowing whether the answer is grounded enough to trust.

### Why artifacts?

The customer needs work product, not just conversation. A decision canvas can be taken directly into a planning meeting.

### Why separate Ship30?

Writing has a different quality contract from Q&A. A dedicated skill makes those constraints explicit and testable.
