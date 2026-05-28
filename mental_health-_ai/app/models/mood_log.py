from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.database import Base
 
 
class MoodLog(Base):
    __tablename__ = "mood_logs"
 
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
 
    # ── Self-reported mood (1–7 scale) ────────────────────────
    mood_level      = Column(Integer, nullable=False)          # 1=Angry … 7=Excited
    mood_label      = Column(String(20), nullable=False)       # "Angry", "Happy", etc.
    notes           = Column(Text, nullable=True)              # Optional free-text note
 
    # ── AI Analysis results (filled after /analyze call) ──────
    is_analyzed     = Column(Boolean, default=False)
    mental_state    = Column(String(50), nullable=True)        # "Anxiety", "Normal", etc.
    cause           = Column(String(100), nullable=True)       # "Academic Stress", etc.
    confidence      = Column(Float, nullable=True)             # 0.0 – 1.0
    keywords        = Column(Text, nullable=True)              # JSON string: ["stressed","exams"]
    ai_summary      = Column(Text, nullable=True)              # One-line summary from AI
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
 
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
 
    # ── Relationships ───────────────────────────────────────────
    user            = relationship("User", back_populates="mood_logs")
    chat_session    = relationship("ChatSession", back_populates="mood_log")
 
    def __repr__(self) -> str:
        return f"<MoodLog id={self.id} user={self.user_id} mood={self.mood_label} state={self.mental_state}>"