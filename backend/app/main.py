from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database
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
                conn.commit()
                logger.info("Added original_summary column to articles table.")
    except Exception as e:
        logger.warning(f"Column migration notice: {e}")

    logger.info("Database tables initialized. Ready for news ingestion.")
    
    yield
    # Shutdown logic if any
    logger.info("Application shutting down.")

app = FastAPI(
    title="Multilingual News Digest API",
    description="Backend API for international multilingual news aggregation, LLM translation (NVIDIA Nemotron), and personalized feeds.",
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
    return {
        "status": "healthy",
        "service": "Multilingual News Digest API",
        "version": "1.0.0",
        "llm_provider": "NVIDIA Nemotron",
        "database": "Ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
