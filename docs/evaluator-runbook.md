# Evaluator Runbook

## Fast path

### 1. Clone

```powershell
git clone <PUBLIC_REPOSITORY_URL>
cd lenny-growth-assistant
```

### 2. Configure

```powershell
Copy-Item .env.example .env
```

For local demo:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### 3. Start dependencies

```powershell
docker compose up -d postgres
```

Start Ollama on the host.

### 4. Backend

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

### 5. Frontend

```powershell
cd frontend
npm install
npm run dev
```

### 6. Verify

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
Invoke-RestMethod "http://127.0.0.1:8000/api/system/status"
```

### 7. Demo

Open the Vite URL and:

1. ask PMF question
2. inspect evidence
3. ask follow-up
4. generate Ship30
5. generate Decision Canvas

## Troubleshooting

### API unavailable

Check:

```powershell
Get-NetTCPConnection -LocalPort 8000
```

### Ollama unavailable

Check:

```powershell
ollama list
```

Expected local models include:

```text
qwen3:4b
nomic-embed-text
```

### PostgreSQL

Check:

```powershell
docker compose ps
```

### CORS

If Vite uses 5174, ensure:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

Then restart FastAPI.

### Slow generation

The local model can take time for long-form generation. Wait for completion before retrying.

## Security note

Never put:

- Anthropic API keys
- passwords
- tokens
- `.env`
- personal credentials

into the repository.
