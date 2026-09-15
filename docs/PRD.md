# The Lenny Growth Assistant
## Product Requirements Document

**Version:** 1.0  
**Status:** Take-Home Assessment  
**Product:** The Lenny Growth Assistant  
**Role:** Forward Deployed Engineer  

---

# 1. Executive Summary

The Lenny Growth Assistant is an AI-powered internal knowledge assistant designed to help product managers, founders, and growth practitioners turn Lenny's Podcast transcript knowledge into grounded answers, actionable decisions, reusable written content, and rendered artifacts.

The product combines conversational retrieval, agentic routing, source-grounded generation, structured content skills, local LLM inference through Ollama, optional cloud inference, PostgreSQL persistence, and an isolated artifact viewer.

The central product principle is:

> Move users from question → evidence → decision → deliverable without requiring them to understand prompts, models, retrieval systems, or infrastructure.

The assistant is intentionally designed as a forward-deployed internal tool rather than a generic chatbot.

---

# 2. Forward Deployment Discovery Brief

## 2.1 User and Problem

### Primary users

The primary users are:

- Product managers
- Growth practitioners
- Startup founders
- Product leaders
- Internal strategy teams

### User job

Users frequently face product and growth questions such as:

- How should we prioritize opportunities?
- How should we approach product-market fit?
- How should we structure growth experiments?
- How should product teams make difficult prioritization decisions?
- How can an expert product insight be turned into something reusable?

The underlying job is:

> When facing a product or growth decision, I want to quickly find relevant expert knowledge and convert it into an actionable next step.

### Problem

Expert knowledge is difficult to use efficiently when it is distributed across long-form podcast transcripts.

Users may need to:

1. Search multiple transcripts.
2. Read large sections of conversations.
3. Identify relevant evidence.
4. Compare perspectives.
5. Translate insights into their own context.
6. Create reusable written material.

This creates friction between **knowledge discovery** and **knowledge application**.

The assistant removes that friction by providing a single interface for:

**Question → Evidence → Synthesis → Action**

---

# 3. Product Vision

The product vision is to create a trustworthy product-growth intelligence layer over Lenny's Podcast knowledge.

Rather than positioning the system as an all-knowing AI assistant, the product emphasizes:

- Grounding
- Evidence
- Transparency
- Actionability
- Reusability
- Operational reliability

The assistant should make it easy for a user to understand not only **what the answer is**, but also **where the answer came from**.

---

# 4. Product Principles

## 4.1 Evidence before confidence

The assistant should prefer an honest limitation over an unsupported answer.

## 4.2 Separate source knowledge from synthesis

The system should distinguish between:

- What the source material supports.
- What the assistant synthesizes from those sources.

## 4.3 Make complex AI behavior understandable

Users should not need to understand:

- embeddings
- retrieval
- agents
- model providers
- prompts

The interface should expose useful outcomes instead.

## 4.4 Local-first demonstration

Ollama is the default demonstration provider because local inference is a mandatory assessment requirement.

## 4.5 Design for handoff

The system should be understandable and operable by another engineer without requiring the original developer.

---

# 5. Success Metrics

## 5.1 Grounded Answer Acceptance Rate

Percentage of evaluation questions for which the answer is judged:

1. Relevant
2. Useful
3. Supported by retrieved transcript evidence

### Target

≥ 85% on the curated evaluation set.

---

## 5.2 Evidence Hit Rate

Percentage of evaluation queries where at least one relevant source passage appears in the top-k retrieval results.

### Target

≥ 90% on the curated retrieval evaluation set.

---

## 5.3 Citation Coverage

Percentage of source-dependent factual claims that contain identifiable supporting source references.

### Target

≥ 95%.

---

## 5.4 Fresh Installation Success

Percentage of clean environments where a new evaluator can:

1. Clone the repository.
2. Configure environment variables.
3. Start the application.
4. Open the UI.
5. Run a grounded query.

### Target

100% following the documented setup path.

---

## 5.5 Operational Visibility

Model, retrieval, database, and artifact failures should produce actionable logs and user-facing errors rather than silent failures.

---

# 6. Assumptions

Because the original client brief does not specify every product detail, the following assumptions are made:

1. The primary use case is an internal product/growth knowledge assistant.
2. Lenny's Podcast transcripts are the authoritative knowledge source for claims attributed to the podcast.
3. The assistant should not invent opinions and attribute them to Lenny or podcast guests.
4. The local Ollama model is the default demo model.
5. A cloud model is an optional higher-quality inference path.
6. Users may ask questions that are not sufficiently supported by the transcript repository.
7. Generated HTML must be treated as untrusted content.
8. Authentication and enterprise identity management are outside the take-home scope.
9. The application is designed primarily for local evaluation and small-team internal use rather than internet-scale production traffic.
10. Artifacts are persisted for the associated session so users can revisit generated work.

---

# 7. Scope

## 7.1 In Scope

### Core assistant

- Conversational chat
- Independent sessions
- Follow-up questions
- PostgreSQL persistence
- Transcript retrieval
- Grounded answers
- Source citations
- Abstention when evidence is insufficient

### AI infrastructure

- Local Ollama provider
- Cloud LLM provider
- Provider abstraction
- Model switching
- Agent routing

### Content generation

- Ship 30 for 30 skill
- Approximately 1,250-word essays
- Grounded content generation
- Structured decision frameworks

### Artifacts

- Markdown generation
- HTML/CSS generation
- In-app artifact viewer
- Preview/source views
- Artifact persistence
- Secure rendering

### Operations

- Docker Compose
- Environment configuration
- Structured logs
- Health endpoints
- Error handling
- Automated tests
- Operational documentation

---

# 8. Out of Scope

The following are intentionally excluded:

- Enterprise SSO
- Multi-tenant authorization
- Billing
- Public user registration
- Autonomous web research
- Arbitrary external website ingestion
- Production-scale distributed inference
- Fully autonomous product decision-making

These exclusions keep the implementation focused on the evaluation objectives while leaving clear extension points.

---

# 9. Differentiating Product Features

In addition to the required functionality, the following features are planned where implementation time permits.

## 9.1 Evidence Trail

Every grounded answer exposes the sources used to produce it.

Users can inspect:

- Episode
- Guest
- Source
- Relevant passage
- Retrieval relevance

---

## 9.2 Grounding Indicator

Each response can communicate an interpretable grounding state:

- High
- Medium
- Limited

The indicator is based on retrieval evidence rather than model self-confidence.

---

## 9.3 Challenge My Answer

Users can ask the assistant to critically examine its response against the retrieved evidence.

The system should identify:

- Unsupported claims
- Weak evidence
- Alternative interpretations
- Missing context

---

## 9.4 Decision Canvas

The assistant can transform knowledge into a structured decision artifact containing:

- Problem
- Evidence
- Options
- Trade-offs
- Recommendation
- Next experiment

---

## 9.5 Knowledge Explorer

Users can browse major product, growth, and leadership topics and launch grounded questions from those topics.

---

## 9.6 System Health

The application exposes operational status for:

- API
- PostgreSQL
- Ollama
- Knowledge base
- Retrieval
- Artifact rendering

This helps an evaluator diagnose issues without inspecting the codebase first.

---

# 10. User Flows

## 10.1 New Conversation

```text
Open application
      ↓
Create new session
      ↓
Ask question
      ↓
Retrieve evidence
      ↓
Generate grounded answer
      ↓
Display citations