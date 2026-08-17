import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging import logger
from app.database.database import engine, SessionLocal
from app.database.base import Base
from app.database.seed import seed_initial_data
from app.api.router import api_router

# Create database tables automatically if missing
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing MediPolicy_IQ Database tables and seeding initial data...")
    db = SessionLocal()
    try:
        seed_initial_data(db)
        logger.info("Database seeding completed successfully.")
    except Exception as e:
        logger.error(f"Error during startup database seeding: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI-Powered Healthcare Insurance Claims Intelligence Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Static directory path
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["React Frontend App"])
def serve_react_app():
    """Serve modern React Single Page Application (SPA)."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

