from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.core.config import settings
from app.core.logging import logger
import urllib.request
import socket

router = APIRouter()


@router.get("/health", tags=["Observability"])
def liveness_probe():
    """Liveness probe: returns execution status of the API instance."""
    return {
        "status": "UP",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready", tags=["Observability"])
def readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe: validates availability of database, Redis cache, and external subsystems."""
    status = "UP"
    details = {}

    # 1. Database Connection Check
    try:
        db.execute(text("SELECT 1"))
        details["database"] = {
            "status": "CONNECTED",
            "type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
        }
    except Exception as e:
        logger.error(f"Readiness probe database connection failure: {e}")
        status = "DOWN"
        details["database"] = {"status": "DISCONNECTED", "error": str(e)}

    # 2. Redis Connection Check (graceful validation)
    if settings.REDIS_URL:
        try:
            # Check Redis connection details if possible
            # Standard libraries are checked. If not imported, simple socket check is done.
            import redis
            r = redis.from_url(settings.REDIS_URL, socket_timeout=1)
            r.ping()
            details["redis"] = {"status": "CONNECTED"}
        except ImportError:
            # Fallback to manual socket connection test
            try:
                # Parse host/port from URL: redis://localhost:6379/0
                clean_url = settings.REDIS_URL.replace("redis://", "")
                parts = clean_url.split("/")[0].split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 6379
                s = socket.create_connection((host, port), timeout=1)
                s.close()
                details["redis"] = {"status": "CONNECTED (Socket verified)"}
            except Exception as se:
                logger.warning(f"Readiness probe Redis connection socket failure: {se}")
                # We do not mark the app DOWN on development cache failure unless strictly required
                details["redis"] = {"status": "DISCONNECTED", "error": str(se)}
        except Exception as e:
            logger.warning(f"Readiness probe Redis ping failure: {e}")
            details["redis"] = {"status": "DISCONNECTED", "error": str(e)}

    # 3. Vector database endpoint check
    if settings.VECTOR_DATABASE_URL:
        try:
            req = urllib.request.Request(settings.VECTOR_DATABASE_URL, method="GET")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status in [200, 404]: # qdrant returns 200 or 404 depending on endpoint
                    details["vector_db"] = {"status": "REACHABLE"}
                else:
                    details["vector_db"] = {"status": "UNREACHABLE", "code": response.status}
        except Exception as e:
            # In development vector DB might not be started yet
            details["vector_db"] = {"status": "UNREACHABLE", "error": str(e)}

    return {
        "status": status,
        "details": details
    }
