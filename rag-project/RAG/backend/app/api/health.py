import logging

from fastapi import APIRouter

from app.core.config import settings
from app.db.database import get_connection

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
        database = "up"
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check DB failure: %s", exc)
        database = "down"
    return {
        "status": "ok" if database == "up" else "degraded",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": database,
    }
