from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CreateSessionRequest,
    MessageResponse,
    SessionResponse,
)
from app.db.session import get_db
from app.models.message import Message
from app.models.session import Session


router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"],
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    payload: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    session = Session(
        title=payload.title.strip(),
        mode=payload.mode.strip().lower(),
    )

    db.add(session)

    await db.commit()
    await db.refresh(session)

    return session


@router.get(
    "",
    response_model=list[SessionResponse],
)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Session)
        .order_by(Session.updated_at.desc())
    )

    return list(result.scalars().all())


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    return session


@router.get(
    "/{session_id}/messages",
    response_model=list[MessageResponse],
)
async def get_session_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    # Verify session exists.
    session_result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
    )

    session = session_result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )

    return list(result.scalars().all())