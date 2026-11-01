from flask import Blueprint, jsonify
from sqlalchemy import text
try:
    from ..extensions import db
except (ImportError, ValueError):
    from extensions import db

health_bp = Blueprint("health", __name__, url_prefix="")

@health_bp.get("/healthz")
def liveness():
    """
    Liveness Probe (Slide 34 & 35): 'Tôi còn sống không?'
    Probe siêu nhẹ, không phụ thuộc vào Database hay tài nguyên bên ngoài.
    Trả về HTTP 200 khi tiến trình service đang hoạt động.
    """
    return jsonify({"status": "ok"}), 200

@health_bp.get("/ready")
def readiness():
    """
    Readiness Probe (Slide 34 & 35): 'Tôi nhận traffic được chưa?'
    Kiểm tra kết nối tới cơ sở dữ liệu.
    Trả về HTTP 200 nếu sẵn sàng nhận request, hoặc 503 nếu dependency bị lỗi.
    """
    checks = {}
    try:
        db.session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as err:
        checks["db"] = "err"
        checks["db_error"] = str(err)

    is_ready = checks.get("db") == "ok"
    return jsonify({
        "status": "ok" if is_ready else "degraded",
        "checks": checks
    }), (200 if is_ready else 503)
