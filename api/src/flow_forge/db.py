"""数据库引擎与建表。

默认使用项目下 ``api/data/flow_forge.db``；可用环境变量 ``FLOW_FORGE_DATABASE_URL``
或 ``create_app(database_url=...)`` 覆盖（测试常用临时文件）。
"""

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
    """创建 SQLAlchemy Engine；若是 sqlite 文件路径则自动建父目录。"""

    database_url = url or os.environ.get("FLOW_FORGE_DATABASE_URL", DEFAULT_DB_URL)
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.removeprefix("sqlite:///")
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(database_url)


def check_sqlite_connection(engine: Engine) -> bool:
    """启动时探测数据库是否可连（``SELECT 1``）。"""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def init_db(engine: Engine) -> sessionmaker[Session]:
    """按模型建表（学习向用 create_all；正式迁移可后置），并返回 Session 工厂。"""

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
