
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
 
from app.database import get_db
from app.models.user import User
from app.models.mood_log import MoodLog
from app.schemas.mood_chat import (
    MoodLogCreate, MoodLogResponse, MoodHistoryResponse,
    DashboardResponse, DayMood,
)
from app.services.auth_service import get_current_user
 
# ════════════════════════════════════════════════════════════
#  MOOD ROUTER
# ════════════════════════════════════════════════════════════
mood_router = APIRouter(prefix="/api/mood", tags=["Mood"])
 
MOOD_LABELS = {
    1: "Angry", 2: "Anxious", 3: "Tired",
    4: "Okay",  5: "Joyful",  6: "Happy", 7: "Excited"
}
 
 
@mood_router.post("/log", response_model=MoodLogResponse, status_code=201)
async def log_mood(
    payload: MoodLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a quick mood (without chat). Used for fast daily check-in."""
    log = MoodLog(
        user_id=current_user.id,
        mood_level=payload.mood_level,
        mood_label=MOOD_LABELS[payload.mood_level],
        notes=payload.notes,
    )
    db.add(log)
    await db.flush()
    return log
 
 
@mood_router.get("/history", response_model=MoodHistoryResponse)
async def get_history(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get mood log history for the current user."""
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id)
        .order_by(MoodLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
 
    avg_mood = round(sum(l.mood_level for l in logs) / len(logs), 1) if logs else None
 
    # Most common mental state
    analyzed = [l for l in logs if l.mental_state]
    most_common = None
    if analyzed:
        from collections import Counter
        most_common = Counter(l.mental_state for l in analyzed).most_common(1)[0][0]
 
    return MoodHistoryResponse(
        logs=logs,
        total=len(logs),
        avg_mood=avg_mood,
        most_common_state=most_common,
    )
 
 
# ════════════════════════════════════════════════════════════
#  DASHBOARD ROUTER
# ════════════════════════════════════════════════════════════
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
 
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
RISK_STATES = {"Anxiety", "Depression", "Stress"}
 
 
@dashboard_router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all data needed for the Dashboard screen:
    - 7-day mood history (one entry per day)
    - Streak count
    - Average mood
    - Risk alert (if negative mental state detected recently)
    - Current mood (today's latest log)
    """
    today = datetime.now(timezone.utc).date()
    week_ago = today - timedelta(days=6)
 
    # ── All logs in the last 7 days ────────────────────────────
    result = await db.execute(
        select(MoodLog)
        .where(
            MoodLog.user_id == current_user.id,
            MoodLog.created_at >= datetime.combine(week_ago, datetime.min.time()),
        )
        .order_by(MoodLog.created_at.asc())
    )
    logs = result.scalars().all()
 
    # ── Build 7-day slot array ─────────────────────────────────
    week_data: list[DayMood] = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_logs = [l for l in logs if l.created_at.date() == day]
        latest = day_logs[-1] if day_logs else None
        week_data.append(DayMood(
            date=day.isoformat(),
            day=DAY_NAMES[day.weekday()],
            mood_level=latest.mood_level if latest else 4,
            mood_label=latest.mood_label if latest else "Okay",
            mental_state=latest.mental_state if latest else None,
        ))
 
    # ── Streak ─────────────────────────────────────────────────
    streak = 0
    for i in range(7):
        check_day = today - timedelta(days=i)
        if any(l.created_at.date() == check_day for l in logs):
            streak += 1
        else:
            break
 
    # ── Stats ──────────────────────────────────────────────────
    avg_mood = round(sum(l.mood_level for l in logs) / len(logs), 1) if logs else 4.0
    total_result = await db.execute(
        select(func.count(MoodLog.id)).where(MoodLog.user_id == current_user.id)
    )
    total_sessions = total_result.scalar_one()
 
    # ── Current mood (today's last entry) ─────────────────────
    today_logs = [l for l in logs if l.created_at.date() == today]
    current_mood = today_logs[-1] if today_logs else None
 
    # ── Risk alert ─────────────────────────────────────────────
    recent_states = {l.mental_state for l in logs[-5:] if l.mental_state}
    risk_state = next((s for s in recent_states if s in RISK_STATES), None)
 
    return DashboardResponse(
        week_data=week_data,
        streak=streak,
        avg_mood=avg_mood,
        total_sessions=total_sessions,
        current_mood=current_mood,
        risk_alert=risk_state is not None,
        risk_state=risk_state,
    )
 