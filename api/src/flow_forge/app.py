"""Flask 应用工厂：组装引擎、建表、挂载各 Blueprint。

测试与生产共用 ``create_app``，通过 ``database_url`` 注入临时库路径。
"""

from flask import Flask

from flow_forge.controllers.health import bp as health_bp
from flow_forge.controllers.runs import bp as runs_bp
from flow_forge.controllers.workflows import bp as workflows_bp
from flow_forge.db import check_sqlite_connection, get_engine, init_db


def create_app(database_url: str | None = None) -> Flask:
    """创建并返回可运行的 Flask 应用。"""

    app = Flask(__name__)
    engine = get_engine(database_url)
    check_sqlite_connection(engine)
    session_factory = init_db(engine)
    # 供 controllers / services 取出同一套 Session 工厂
    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = session_factory
    app.register_blueprint(health_bp)
    app.register_blueprint(workflows_bp)
    app.register_blueprint(runs_bp)
    return app
