"""Flask application factory."""

from flask import Flask

from flow_forge.controllers.health import bp as health_bp
from flow_forge.db import check_sqlite_connection, get_engine


def create_app() -> Flask:
    app = Flask(__name__)
    engine = get_engine()
    check_sqlite_connection(engine)
    app.extensions["db_engine"] = engine
    app.register_blueprint(health_bp)
    return app
