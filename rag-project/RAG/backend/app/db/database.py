import psycopg

from app.core.config import settings

def get_connection() -> psycopg.Connection:
    """Open a direct PostgreSQL connection using DATABASE_URL."""
    return psycopg.connect(settings.DATABASE_URL)
