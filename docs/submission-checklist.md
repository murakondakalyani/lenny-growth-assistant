# Submission Checklist

## Repository

- [ ] Public GitHub repository
- [ ] No `.env` or API keys committed
- [ ] README complete
- [ ] PRD complete
- [ ] design.md complete
- [ ] architecture.md complete
- [ ] agent transcripts included
- [ ] tests included
- [ ] docs explain local Ollama
- [ ] docs explain artifact security

## Product

- [ ] FastAPI running
- [ ] PostgreSQL running
- [ ] pgvector enabled
- [ ] transcript corpus ingested
- [ ] RAG retrieval working
- [ ] source metadata visible
- [ ] sessions working
- [ ] follow-up context working
- [ ] Ollama visible in UI
- [ ] Ship30 skill tested
- [ ] artifact viewer working
- [ ] sanitizer tested
- [ ] iframe sandbox active

## Demo

- [ ] camera enabled
- [ ] 2–3 minutes
- [ ] explain customer problem
- [ ] show grounded question
- [ ] show Evidence Trail
- [ ] show follow-up
- [ ] show Ship30
- [ ] show artifact
- [ ] show Ollama/local model
- [ ] explain one technical trade-off
- [ ] upload to YouTube

## Final verification

Fresh-clone test:

```text
Clone → configure → start → health → UI → ask → evidence → artifact
```

The evaluator should not need undocumented manual steps.
