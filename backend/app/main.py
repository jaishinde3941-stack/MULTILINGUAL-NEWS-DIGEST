from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA busy_timeout=30000"))
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
            if "canonical_url" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN canonical_url VARCHAR(1000)"))
                logger.info("Added canonical_url column to articles table.")
            if "article_fingerprint" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN article_fingerprint VARCHAR(64)"))
                logger.info("Added article_fingerprint column to articles table.")
            if "batch_id" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN batch_id VARCHAR(50)"))
                logger.info("Added batch_id column to articles table.")
            if "batch_state" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN batch_state VARCHAR(20) DEFAULT 'active'"))
                logger.info("Added batch_state column to articles table.")
            if "displayed_at" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN displayed_at DATETIME"))
                logger.info("Added displayed_at column to articles table.")
            if "consumed_at" not in cols:
                conn.execute(text("ALTER TABLE articles ADD COLUMN consumed_at DATETIME"))
                logger.info("Added consumed_at column to articles table.")
            conn.commit()
    except Exception as e:
        logger.warning(f"Column migration notice: {e}")

    logger.info("Database tables initialized. Ready for news ingestion.")

    # Automatic startup news ingestion & prefetching in non-blocking background daemon
    try:
        from app.services.ingestion_manager import ingestion_manager
        import threading
        threading.Thread(target=ingestion_manager.on_startup, daemon=True, name="startup-prefetch-worker").start()
    except Exception as e:
        logger.warning(f"Startup prefetch worker could not be spawned: {e}")
    
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    origin = request.headers.get("origin")
    allowed_origin = origin if origin else "*"
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error": str(exc),
            "status": "error"
        },
        headers={
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Register Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)
app.include_router(ingest_router)

@app.get("/health")
def liveness_probe():
    return {
        "status": "ok",
        "service": "Multilingual News Digest API",
        "port": settings.PORT
    }

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
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
