"""
app/routers/analyze.py
───────────────────────
Analysis endpoint — uses BOTH DistilBERT models:
  1. Mental State Model  → Anxiety / Depression / Stress / Suicidal / Normal
  2. Cause Model         → Academic Stress / Social Isolation / etc.
  3. SHAP Keywords       → explainable AI keywords
"""
 
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
 
from app.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.mood_log import MoodLog
from app.schemas.mood_chat import AnalysisRequest, AnalysisResponse
from app.services.auth_service import get_current_user
from app.services.ml_service import full_predict, MODEL_LOADED
from app.services.groq_service import analyze_conversation as groq_analyze
 
router = APIRouter(prefix="/api/analyze", tags=["Analysis"])
 
 
@router.post("/session", response_model=AnalysisResponse)
async def analyze_session(
    payload: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a completed chat session.
 
    Pipeline:
      1. Load chat session messages from DB
      2. Combine all user messages into one text
      3. Run DistilBERT Mental State Model  → mental_state + confidence
      4. Run DistilBERT Cause Model         → cause + cause_confidence
      5. Extract SHAP keywords              → explainability
      6. Fallback to Groq if models not loaded
      7. Save result to MoodLog table
      8. Return full AnalysisResponse
    """
 
    # ── 1. Load session from DB ────────────────────────────────────────────────
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == payload.session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
 
    # ── 2. Load messages ───────────────────────────────────────────────────────
    messages: list[dict] = json.loads(session.messages_json or "[]")
    user_messages = [m for m in messages if m["role"] == "user"]
 
    if not user_messages:
        raise HTTPException(
            status_code=400,
            detail="No messages found in session to analyze"
        )
 
    # ── 3. Combine all user messages into one text ────────────────────────────
    full_text = " ".join(m["content"] for m in user_messages)
 
    # ── 4. Run Analysis ────────────────────────────────────────────────────────
    if MODEL_LOADED:
        # ── Real DistilBERT Models (Phase 2) ──────────────────────────────────
        print(f"[Analyze] Using DistilBERT models for session {session.id}")
        ml_result = full_predict(full_text)
 
        mental_state     = ml_result["mental_state"]
        confidence       = ml_result["confidence"]
        cause            = ml_result["cause"]
        cause_confidence = ml_result["cause_confidence"]
        keywords         = ml_result["keywords"]
        mood_level       = ml_result["mood_level"]
        suggestions      = ml_result["suggestions"]
        summary = (
            f"Analysis shows signs of {mental_state} "
            f"likely caused by {cause}."
        )
 
    else:
        # ── Groq LLM Fallback (Phase 1) ────────────────────────────────────────
        print(f"[Analyze] Models not loaded — using Groq fallback")
        analysis = await groq_analyze(
            messages=messages,
            selected_mood=session.selected_mood,
            mood_level=session.mood_level,
        )
        mental_state     = analysis.get("mental_state", "Normal")
        confidence       = float(analysis.get("confidence", 0.7))
        cause            = analysis.get("cause", "Unknown")
        cause_confidence = 0.0
        keywords         = analysis.get("keywords", [])
        mood_level       = int(analysis.get("mood_level", session.mood_level or 4))
        summary          = analysis.get("summary", "")
        suggestions      = analysis.get("suggestions", [])
 
    # ── 5. Save result to MoodLog table ───────────────────────────────────────
    mood_log = MoodLog(
        user_id=current_user.id,
        mood_level=mood_level,
        mood_label=session.selected_mood or "Unknown",
        is_analyzed=True,
        mental_state=mental_state,
        cause=cause,
        confidence=confidence,
        keywords=json.dumps(keywords),
        ai_summary=summary,
        chat_session_id=session.id,
    )
    db.add(mood_log)
 
    # ── 6. Mark session as completed ──────────────────────────────────────────
    session.is_completed = 1
    session.analysis_json = json.dumps({
        "mental_state":      mental_state,
        "confidence":        confidence,
        "cause":             cause,
        "cause_confidence":  cause_confidence,
        "keywords":          keywords,
        "mood_level":        mood_level,
        "summary":           summary,
    })
    db.add(session)
 
    # ── 7. Return response ────────────────────────────────────────────────────
    return AnalysisResponse(
        session_id=session.id,
        mental_state=mental_state,
        confidence=round(confidence, 2),
        cause=cause,
        keywords=keywords,
        mood_level=mood_level,
        summary=summary,
        suggestions=suggestions,
    )