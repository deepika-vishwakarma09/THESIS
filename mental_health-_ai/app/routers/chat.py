
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
 
from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.schemas.mood_chat import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user
from app.services.groq_service import get_chat_reply
 
router = APIRouter(prefix="/api/chat", tags=["Chat"])
 
 
@router.post("/send", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message and get an AI reply.
 
    - If session_id is None → creates a new chat session
    - If session_id provided → continues existing session
    """
 
    # ── Get or create session ──────────────────────────────────
    if payload.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == payload.session_id,
                ChatSession.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            user_id=current_user.id,
            selected_mood=payload.selected_mood,
            mood_level=payload.mood_level,
            messages_json="[]",
        )
        db.add(session)
        await db.flush()
 
    # ── Load existing messages ─────────────────────────────────
    messages: list[dict] = json.loads(session.messages_json or "[]")
 
    # ── Append user message ────────────────────────────────────
    messages.append({"role": "user", "content": payload.message})
 
    # ── Get reply from Groq ────────────────────────────────────
    reply = await get_chat_reply(messages, selected_mood=payload.selected_mood)
 
    # ── Append assistant reply ─────────────────────────────────
    messages.append({"role": "assistant", "content": reply})
 
    # ── Save updated messages back to DB ───────────────────────
    session.messages_json = json.dumps(messages)
    db.add(session)
 
    return ChatResponse(
        session_id=session.id,
        reply=reply,
        message_count=len([m for m in messages if m["role"] == "user"]),
    )
 
 
@router.get("/session/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all messages in a chat session."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
 
    return {
        "session_id": session.id,
        "messages": json.loads(session.messages_json or "[]"),
        "selected_mood": session.selected_mood,
        "mood_level": session.mood_level,
        "is_completed": bool(session.is_completed),
        "created_at": session.created_at,
    }
 