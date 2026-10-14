from collections.abc import Generator

from app.config import Settings, get_settings
from app.db.session import get_db

__all__ = ["get_db", "get_settings_dep"]


def get_settings_dep() -> Settings:
    return get_settings()


def get_db_dep() -> Generator:
    yield from get_db()
