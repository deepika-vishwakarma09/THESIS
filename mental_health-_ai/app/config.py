
from pydantic_settings import BaseSettings
from functools import lru_cache
 
 
class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────
    APP_NAME: str = "Mental Health AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
 
    # ── Security ───────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
 
    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./mental_health.db"
 
    # ── Groq ───────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"
 
    # ── HuggingFace ────────────────────────────────────────────
    HF_TOKEN: str = ""
 
    # ── Model Paths ────────────────────────────────────────────
    MODEL_DIR: str = "./ml/saved_models"
    MENTAL_HEALTH_MODEL_PATH: str = "./ml/saved_models/mental_health_classifier"
    CAUSE_MODEL_PATH: str = "./ml/saved_models/cause_classifier"
 
    # ── CORS ───────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8081"
 
    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
 
    class Config:
        env_file = ".env"
        case_sensitive = True
 
 
# Single instance — import this everywhere
@lru_cache()
def get_settings() -> Settings:
    return Settings()
 
 
settings = get_settings()