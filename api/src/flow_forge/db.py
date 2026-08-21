"""Database engine helpers (SQLite first)."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from flow_forge.models import Base

DEFAULT_DB_DIR = Path(__file__).resolve().parents[2] / "data"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_DIR / 'flow_forge.db'}"


def get_engine(url: str | None = None) -> Engine:
    database_url = url or os.environ.get("FLOW_FORGE_DATABASE_URL", DEFAULT_DB_URL)
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.removeprefix("sqlite:///")
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(database_url)


def check_sqlite_connection(engine: Engine) -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def init_db(engine: Engine) -> sessionmaker[Session]:
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
