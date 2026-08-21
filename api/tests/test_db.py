"""SQLite connectivity smoke."""

from flow_forge.db import check_sqlite_connection, get_engine


def test_sqlite_engine_connects(tmp_path) -> None:
    db_path = tmp_path / "flow_forge.db"
    engine = get_engine(f"sqlite:///{db_path}")

    assert check_sqlite_connection(engine) is True
