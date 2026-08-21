"""探活接口：确认进程已启动、路由已挂载。"""

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health() -> tuple[dict[str, str], int]:
    """返回 ``{"status": "ok"}``。"""

    return jsonify(status="ok"), 200
