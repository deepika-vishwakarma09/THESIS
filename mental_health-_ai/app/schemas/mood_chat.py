
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
 
 
# ════════════════════════════════════════════════════════════
#  MOOD SCHEMAS
# ════════════════════════════════════════════════════════════
 
VALID_MOODS = {
    1: "Angry", 2: "Anxious", 3: "Tired",
    4: "Okay",  5: "Joyful",  6: "Happy", 7: "Excited"
}
 
 
class MoodLogCreate(BaseModel):
    mood_level: int
    notes: Optional[str] = None
 
    @field_validator("mood_level")
    @classmethod
    def mood_in_range(cls, v: int) -> int:
        if v not in VALID_MOODS:
            raise ValueError("mood_level must be between 1 and 7")
        return v
 
    @property
    def mood_label(self) -> str:
        return VALID_MOODS[self.mood_level]
 
 
class MoodLogResponse(BaseModel):
    id: int
    mood_level: int
    mood_label: str
    notes: Optional[str]
    is_analyzed: bool
    mental_state: Optional[str]
    cause: Optional[str]
    confidence: Optional[float]
    keywords: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime
 
    model_config = {"from_attributes": True}
 
 
class MoodHistoryResponse(BaseModel):
    logs: list[MoodLogResponse]
    total: int
    avg_mood: Optional[float]
    most_common_state: Optional[str]
 
 
# ════════════════════════════════════════════════════════════
#  CHAT SCHEMAS
# ════════════════════════════════════════════════════════════
 
class ChatMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str
 
 
class ChatRequest(BaseModel):
    session_id: Optional[int] = None  # None = start new session
    message: str
    selected_mood: Optional[str] = None
    mood_level: Optional[int] = None
 
 
class ChatResponse(BaseModel):
    session_id: int
    reply: str
    message_count: int
 
 
# ════════════════════════════════════════════════════════════
#  ANALYSIS SCHEMAS
# ════════════════════════════════════════════════════════════
 
class AnalysisRequest(BaseModel):
    session_id: int
 
 
class AnalysisResponse(BaseModel):
    session_id: int
    mental_state: str            # "Anxiety" | "Depression" | "Stress" | "Loneliness" | "Normal"
    confidence: float            # 0.0 – 1.0
    cause: str                   # "Academic Stress" etc.
    keywords: list[str]          # SHAP-extracted keywords
    mood_level: int              # 1–7
    summary: str                 # One-line human-readable summary
    suggestions: list[str]       # Coping strategies
 
 
# ════════════════════════════════════════════════════════════
#  DASHBOARD SCHEMAS
# ════════════════════════════════════════════════════════════
 
class DayMood(BaseModel):
    date: str           # "2024-05-20"
    day: str            # "Mon"
    mood_level: int
    mood_label: str
    mental_state: Optional[str]
 
 
class DashboardResponse(BaseModel):
    week_data: list[DayMood]
    streak: int
    avg_mood: float
    total_sessions: int
    current_mood: Optional[MoodLogResponse]
    risk_alert: bool
    risk_state: Optional[str]