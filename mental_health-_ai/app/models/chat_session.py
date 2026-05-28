
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
 
 
class ChatSession(Base):
    __tablename__ = "chat_sessions"
 
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
 
    # ── Conversation stored as JSON string ─────────────────────
    # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    messages_json   = Column(Text, default="[]")
 
    # ── AI analysis result (after /analyze) ───────────────────
    analysis_json   = Column(Text, nullable=True)
 
    # ── Session metadata ───────────────────────────────────────
    selected_mood   = Column(String(20), nullable=True)        # Pre-chat mood selection
    mood_level      = Column(Integer, nullable=True)           # 1–7
    is_completed    = Column(Integer, default=0)               # 0=ongoing, 1=analyzed
 
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
 
    # ── Relationships ───────────────────────────────────────────
    user            = relationship("User", back_populates="chat_sessions")
    mood_log        = relationship("MoodLog", back_populates="chat_session", uselist=False)
 
    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} user={self.user_id} completed={self.is_completed}>"