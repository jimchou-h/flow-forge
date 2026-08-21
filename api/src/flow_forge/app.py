"""Flask application factory."""

from flask import Flask

from flow_forge.controllers.health import bp as health_bp
from flow_forge.controllers.runs import bp as runs_bp
from flow_forge.controllers.workflows import bp as workflows_bp
from flow_forge.db import check_sqlite_connection, get_engine, init_db


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    engine = get_engine(database_url)
    check_sqlite_connection(engine)
    session_factory = init_db(engine)
    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = session_factory
    app.register_blueprint(health_bp)
    app.register_blueprint(workflows_bp)
    app.register_blueprint(runs_bp)
    return app
