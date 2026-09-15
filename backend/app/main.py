from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.messages import router as messages_router
from app.api.sessions import router as sessions_router
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.api.artifacts import router as artifacts_router


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Evidence-grounded product and growth copilot "
        "powered by Lenny's content."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(sessions_router)
app.include_router(messages_router)
app.include_router(artifacts_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():
    database_status = "healthy"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

    except Exception:
        database_status = "unhealthy"

    overall_status = (
        "ok"
        if database_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "service": "lenny-growth-assistant",
        "environment": settings.app_env,
        "database": database_status,
    }


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.get("/api/system/status")
async def system_status():
    database_status = "healthy"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))

    except Exception:
        database_status = "unhealthy"

    if settings.llm_provider == "ollama":
        model = settings.ollama_model
    else:
        model = settings.anthropic_model

    return {
        "status": (
            "ok"
            if database_status == "healthy"
            else "degraded"
        ),
        "provider": settings.llm_provider,
        "model": model,
        "database": database_status,
        "retrieval": "configured",
        "artifact_sanitization": (
            settings.artifact_sanitization_enabled
        ),
    }