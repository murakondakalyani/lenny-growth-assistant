from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentRouter
from app.api.schemas import (
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    SourceResponse,
)
from app.db.session import get_db
from app.models.message import Message
from app.models.session import Session


router = APIRouter(
    prefix="/api/sessions",
    tags=["messages"],
)

agent_router = AgentRouter()


@router.post(
    "/{session_id}/messages",
    response_model=SendMessageResponse,
)
async def send_message(
    session_id: UUID,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    content = payload.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty.",
        )

    # ---------------------------------------------------------
    # 1. Find session
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 2. Load previous conversation
    # ---------------------------------------------------------

    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )

    previous_messages = list(
        history_result.scalars().all()
    )

    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in previous_messages
    ]

    # ---------------------------------------------------------
    # 3. Save user message
    # ---------------------------------------------------------

    user_message = Message(
        session_id=session_id,
        role="user",
        content=content,
    )

    db.add(user_message)

    await db.flush()

    # ---------------------------------------------------------
    # 4. Run agent
    # ---------------------------------------------------------

    try:
        result = await agent_router.answer(
            session=db,
            query=content,
            conversation_history=conversation_history,
        )

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    # ---------------------------------------------------------
    # 5. Save assistant message
    # ---------------------------------------------------------

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=result.answer,
    )

    db.add(assistant_message)

    # ---------------------------------------------------------
    # 6. Update session timestamp
    # ---------------------------------------------------------

    session.updated_at = datetime.now(timezone.utc)

    await db.commit()

    await db.refresh(assistant_message)

    # ---------------------------------------------------------
    # 7. Build source response
    # ---------------------------------------------------------

    sources = []

    for index, evidence in enumerate(
        result.evidence,
        start=1,
    ):
        sources.append(
            SourceResponse(
                source_number=index,
                title=evidence.title,
                guest=evidence.guest,
                episode=evidence.episode,
                source_url=evidence.source_url,
                relevance=float(evidence.final_score),
            )
        )

    # ---------------------------------------------------------
    # 8. Return API response
    # ---------------------------------------------------------

    return SendMessageResponse(
        message=MessageResponse.model_validate(
            assistant_message
        ),
        provider=result.provider,
        model=result.model,
        sources=sources,
    )