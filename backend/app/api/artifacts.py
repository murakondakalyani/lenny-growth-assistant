from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.schemas import (
    ArtifactResponse,
    CreateArtifactRequest,
)
from app.artifacts.generator import ArtifactGenerator
from app.db.session import AsyncSessionLocal
from app.models.artifact import Artifact
from app.models.session import Session


router = APIRouter(
    prefix="/api",
    tags=["artifacts"],
)


# ============================================================
# CREATE ARTIFACT
# ============================================================

@router.post(
    "/sessions/{session_id}/artifacts",
    response_model=ArtifactResponse,
)
async def create_artifact(
    session_id: UUID,
    request: CreateArtifactRequest,
):

    async with AsyncSessionLocal() as db:

        # ----------------------------------------------------
        # Verify session exists
        # ----------------------------------------------------

        result = await db.execute(
            select(Session).where(
                Session.id == session_id
            )
        )

        session = result.scalar_one_or_none()

        if session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found.",
            )

        try:

            # ------------------------------------------------
            # Generate artifact
            # ------------------------------------------------

            generator = ArtifactGenerator()

            result = await generator.generate(
                session=db,
                prompt=request.prompt,
                artifact_type=request.artifact_type,
            )

            # ------------------------------------------------
            # Persist artifact
            # ------------------------------------------------

            artifact = Artifact(
                session_id=session_id,
                title=result.title,
                artifact_type=result.artifact_type,
                content_format=result.content_format,
                content=result.content,
                sanitized_content=result.sanitized_content,
            )

            db.add(artifact)

            await db.commit()
            await db.refresh(artifact)

            return artifact

        except ValueError as exc:

            await db.rollback()

            raise HTTPException(
                status_code=422,
                detail=str(exc),
            ) from exc

        except Exception as exc:

            await db.rollback()

            raise HTTPException(
                status_code=503,
                detail=f"Artifact generation failed: {exc}",
            ) from exc


# ============================================================
# GET ARTIFACT
# ============================================================

@router.get(
    "/artifacts/{artifact_id}",
    response_model=ArtifactResponse,
)
async def get_artifact(
    artifact_id: UUID,
):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Artifact).where(
                Artifact.id == artifact_id
            )
        )

        artifact = result.scalar_one_or_none()

        if artifact is None:
            raise HTTPException(
                status_code=404,
                detail="Artifact not found.",
            )

        return artifact