"""HTTP controllers (thin Flask blueprints)."""

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health() -> tuple[dict[str, str], int]:
    return jsonify(status="ok"), 200
