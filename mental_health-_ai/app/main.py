
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
 
from app.config import settings
from app.database import create_tables
 
# ── Import all routers ─────────────────────────────────────────────────────────
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.analyze import router as analyze_router
from app.routers.mood_dashboard import mood_router, dashboard_router
 
 
# ── Lifespan: runs on startup and shutdown ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ─────────────────────────────────────────────────
    print(f"\n🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   DB  → {settings.DATABASE_URL}")
    print(f"   MODE → {'DEBUG' if settings.DEBUG else 'PRODUCTION'}\n")
    await create_tables()
    print("✅ Database tables ready\n")
 
    yield   # App is running here
 
    # ── SHUTDOWN ────────────────────────────────────────────────
    print("\n⛔ Shutting down...")
 
 
# ── App instance ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Explainable AI Mental Health Detection System
 
**Backend API** for the MyUni mental health mood tracker.
 
### Features
- 🔐 JWT Authentication (register / login)
- 💬 AI Chatbot powered by Groq (LLaMA 3)
- 🧠 DistilBERT mental health classification
- 💡 SHAP keyword explainability
- 📊 Dashboard with mood trend data
 
### Usage
1. Register → `POST /api/auth/register`
2. Login → `POST /api/auth/login` → copy `access_token`
3. Click **Authorize** → paste token
4. Use all other endpoints
""",
    lifespan=lifespan,
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
)
 
 
# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
# ── Include all routers ────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analyze_router)
app.include_router(mood_router)
app.include_router(dashboard_router)
 
 
# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running ✅",
        "docs": "/docs",
    }
 
 
@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse({"status": "ok"})
 
 
# ── Run directly with: python -m app.main ─────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )