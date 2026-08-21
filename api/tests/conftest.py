"""Shared fixtures for API tests."""

from __future__ import annotations

import pytest

from flow_forge.app import create_app
from sample_data import sample_graph

__all__ = ["app", "client", "sample_graph"]


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.db"
    application = create_app(database_url=f"sqlite:///{db_path}")
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
