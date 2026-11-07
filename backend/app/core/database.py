from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def build_engine(database_url: str | None) -> Engine | None:
    if not database_url:
        return None
    return create_engine(
        _normalize_database_url(database_url),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )


engine = build_engine(get_settings().database_url)


def check_database_connection() -> bool:
    if engine is None:
        return False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        # Never expose connection strings or provider exception details in health responses.
        return False
