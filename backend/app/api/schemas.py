from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================
# SESSION SCHEMAS
# ============================================================

class CreateSessionRequest(BaseModel):
    title: str = Field(
        default="New Lenny Session",
        min_length=1,
        max_length=120,
    )

    mode: str = Field(
        default="ask",
        min_length=1,
        max_length=30,
    )


class SessionResponse(BaseModel):
    id: UUID
    title: str
    mode: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


# ============================================================
# MESSAGE SCHEMAS
# ============================================================

class SendMessageRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=12000,
    )


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


# ============================================================
# SOURCE / RETRIEVAL SCHEMAS
# ============================================================

class SourceResponse(BaseModel):
    source_number: int
    title: str
    guest: str | None
    episode: str | None
    source_url: str | None
    relevance: float


# ============================================================
# SEND MESSAGE RESPONSE
# ============================================================

class SendMessageResponse(BaseModel):
    message: MessageResponse
    provider: str
    model: str
    sources: list[SourceResponse]


# ============================================================
# ERROR RESPONSE
# ============================================================

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict | None = None


# ============================================================
# ARTIFACT SCHEMAS
# ============================================================

class CreateArtifactRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=12000,
    )

    artifact_type: str = Field(
        default="decision_canvas",
        min_length=1,
        max_length=50,
    )


class ArtifactResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: str
    artifact_type: str
    content_format: str
    content: str
    sanitized_content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }