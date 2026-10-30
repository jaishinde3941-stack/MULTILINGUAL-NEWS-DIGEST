from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database
from app.services.llm_pipeline import llm_pipeline
from app.routers import auth_router, users_router, articles_router, ingest_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("news_digest")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and migration columns are present
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            res = conn.execute(text("PRAGMA table_info(articles)"))
            cols = [r[1] for r in res.fetchall()]
            if "original_summary" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN original_summary TEXT"))
                logger.info("Added original_summary column to articles table.")
            if "processing_status" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN processing_status VARCHAR(30) DEFAULT 'completed'"))
                logger.info("Added processing_status column to articles table.")
            if "processing_error" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN processing_error TEXT"))
                logger.info("Added processing_error column to articles table.")
            if "summary_word_count" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN summary_word_count INTEGER DEFAULT 0"))
                logger.info("Added summary_word_count column to articles table.")
            conn.commit()
    except Exception as e:
        logger.warning(f"Column migration notice: {e}")

    logger.info("Database tables initialized. Ready for news ingestion.")
    
    yield
    # Shutdown logic if any
    logger.info("Application shutting down.")

app = FastAPI(
    title="Multilingual News Digest API",
    description="Backend API for international multilingual news aggregation, local LLM translation (Ollama), and personalized feeds.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(ingest_router)

@app.get("/")
def health_check():
    ollama_status = llm_pipeline.check_ollama_status()
    return {
        "status": "healthy",
        "service": "Multilingual News Digest API",
        "version": "1.0.0",
        "llm_provider": "Ollama",
        "llm_model": settings.OLLAMA_MODEL,
        "ollama_connected": ollama_status["available"],
        "ollama_info": ollama_status.get("message", "Connected and model ready"),
        "database": "Ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
