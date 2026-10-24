"""
Social Network API - Session 7 Demo Implementation
Phục vụ minh họa và kiểm thử 3 endpoints theo đặc tả openapi.yaml & SecurityAudit.md:
  1. POST /api/v1/auth/login
  2. POST /api/v1/auth/refresh
  3. GET  /api/v1/posts/<id>
"""

from datetime import datetime, timezone
import re
import time
import uuid
from flask import Flask, jsonify, request, send_file, render_template_string
import os

app = Flask(__name__)

# Giả lập Database trong bộ nhớ
MOCK_USERS = {
    "Loi@socialnetwork.vn": {
        "id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
        "email": "Loi@socialnetwork.vn",
        "username": "Loi_Doan",
        "display_name": "Doãn Duy Lợi",
        "password": "DoanDuyLoi@123",
        "avatar_url": "https://cdn.socialnetwork.vn/avatars/Loi_Doan.png",
        "role": "USER",
        "is_active": True,
        # Dữ liệu nhạy cảm tuyệt đối không trả về qua API:
        "phone_number": "+84912345678",
        "password_hash": "$2b$12$e8k9J9M9...",
    }
}

MOCK_POSTS = {
    "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d": {
        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "author_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
        "content": "chucmungthanglon",
        "media_urls": ["https://cdn.socialnetwork.vn/posts/sunset.jpg"],
        "privacy": "PUBLIC",  # PUBLIC | FRIENDS | PRIVATE
        "created_at": "2026-10-24T08:30:00Z",
        "updated_at": "2026-10-24T08:35:00Z",
        "likes_count": 42,
        "comments_count": 7,
    },
    "11111111-2222-3333-4444-555555555555": {
        "id": "11111111-2222-3333-4444-555555555555",
        "author_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
        "content": "Nhật ký cá nhân: secret.",
        "media_urls": [],
        "privacy": "PRIVATE",
        "created_at": "2026-10-24T08:40:00Z",
        "updated_at": "2026-10-24T08:40:00Z",
        "likes_count": 0,
        "comments_count": 0,
    },
}

# Quản lý danh sách Refresh Token hợp lệ (hỗ trợ Refresh Token Rotation - RTR)
VALID_REFRESH_TOKENS = set()
REVOKED_REFRESH_TOKENS = set()

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def make_error_response(code: int, error_type: str, message: str, details=None):
    """Chuẩn hóa response lỗi theo chuẩn, không làm lộ stack trace."""
    payload = {
        "code": code,
        "error": error_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": f"trace-{int(time.time())}-{uuid.uuid4().hex[:6]}",
    }
    if details:
        payload["errors"] = details
    return jsonify(payload), code


# ---------------------------------------------------------------------------
# Xử lý CORS để Swagger UI gọi API không bị lỗi "Failed to fetch"
# ---------------------------------------------------------------------------
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = jsonify({"status": "ok"})
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return res, 200


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Swagger UI - Social Network API</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.yaml',
        dom_id: '#swagger-ui',
      });
    };
  </script>
</body>
</html>
"""

# Trang chủ và Giao diện Swagger UI
@app.route("/")
def index():
    return jsonify({
        "system": "Social Network API - Session 7",
        "docs": "http://localhost:5000/docs",
        "openapi_spec": "http://localhost:5000/openapi.yaml"
    })


@app.route("/docs")
def swagger_ui():
    return render_template_string(SWAGGER_UI_HTML)


@app.route("/openapi.yaml")
@app.route("/api/v1/openapi.yaml")
def get_spec():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(base_dir, "openapi.yaml")
    return send_file(spec_path, mimetype="text/yaml")


# Phục vụ các file schema/response khi Swagger UI parse các thẻ $ref: "./components/..."
@app.route("/components/<path:subpath>")
def get_component(subpath):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "components", subpath)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="text/yaml")
    return jsonify({"error": "Component not found"}), 404

# 1. POST /api/v1/auth/login
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return make_error_response(400, "BAD_REQUEST", "Body request rỗng hoặc không đúng định dạng JSON")

    email = data.get("email")
    password = data.get("password")

    # Validation
    validation_errors = []
    if not email:
        validation_errors.append({"field": "email", "issue": "Trường email không được để trống"})
    if not password:
        validation_errors.append({"field": "password", "issue": "Trường password không được để trống"})
    if validation_errors:
        return make_error_response(422, "VALIDATION_FAILED", "Dữ liệu gửi lên không đúng định dạng", validation_errors)

    user = MOCK_USERS.get(email)

    # Giảm thiểu Timing Attack & User Enumeration:
    # Luôn thực hiện so sánh mật khẩu an toàn và thông báo lỗi đồng nhất
    if not user or user["password"] != password:
        # Giả lập thời gian xử lý đồng đều
        time.sleep(0.05)
        return make_error_response(401, "UNAUTHORIZED", "Tài khoản hoặc mật khẩu không chính xác")

    if not user.get("is_active"):
        return make_error_response(403, "FORBIDDEN", "Tài khoản đã bị tạm khóa")

    # Cấp cặp token
    access_token = f"mock-access-token-for-{user['id']}-{uuid.uuid4().hex}"
    refresh_token = f"mock-refresh-token-{uuid.uuid4().hex}"
    VALID_REFRESH_TOKENS.add(refresh_token)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 900,  # 15 phút
    }), 200

# 2. POST /api/v1/auth/refresh
@app.route("/api/v1/auth/refresh", methods=["POST"])
def refresh():
    data = request.get_json(silent=True)
    if not data or "refresh_token" not in data:
        return make_error_response(400, "BAD_REQUEST", "Thiếu trường refresh_token trong request body")

    refresh_token = data.get("refresh_token")

    # Kiểm tra Token Reuse Detection (bảo vệ chống Replay Attack)
    if refresh_token in REVOKED_REFRESH_TOKENS:
        # Phát hiện token cũ bị dùng lại -> có thể hacker đã đánh cắp token -> Hủy toàn bộ token
        VALID_REFRESH_TOKENS.clear()
        return make_error_response(
            403,
            "FORBIDDEN",
            "Cảnh báo an ninh: Phát hiện tái sử dụng Token đã bị thu hồi. Phiên làm việc đã bị hủy.",
        )

    if refresh_token not in VALID_REFRESH_TOKENS:
        return make_error_response(401, "UNAUTHORIZED", "Refresh Token không hợp lệ hoặc đã hết hạn")

    # Kỹ thuật Refresh Token Rotation (RTR):
    # 1. Hủy token hiện tại
    VALID_REFRESH_TOKENS.remove(refresh_token)
    REVOKED_REFRESH_TOKENS.add(refresh_token)

    # 2. Cấp cặp token hoàn toàn mới
    new_access_token = f"mock-access-token-{uuid.uuid4().hex}"
    new_refresh_token = f"mock-refresh-token-{uuid.uuid4().hex}"
    VALID_REFRESH_TOKENS.add(new_refresh_token)

    return jsonify({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer",
        "expires_in": 900,
    }), 200


# 3. GET /api/v1/posts/<id>
@app.route("/api/v1/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    # 1. Kiểm tra UUID hợp lệ (chống SQL Injection / Path traversal)
    if not UUID_REGEX.match(post_id):
        return make_error_response(400, "BAD_REQUEST", "Định dạng ID bài viết không hợp lệ (yêu cầu chuẩn UUID)")

    # 2. Kiểm tra Header xác thực Bearer Token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return make_error_response(401, "UNAUTHORIZED", "Yêu cầu cung cấp Bearer Access Token hợp lệ")

    token = auth_header.split(" ")[1]
    if not token.startswith("mock-access-token"):
        return make_error_response(401, "UNAUTHORIZED", "Access token không hợp lệ hoặc đã hết hạn")

    # Giả định user hiện tại qua token
    current_user_id = "4fa85f64-5717-4562-b3fc-2c963f66afa6"

    # 3. Tìm bài viết
    post = MOCK_POSTS.get(post_id)
    if not post:
        return make_error_response(404, "NOT_FOUND", "Không tìm thấy bài viết hoặc bài viết không tồn tại")

    # 4. Kiểm tra phân quyền cấp đối tượng (BOLA / IDOR protection)
    if post["privacy"] == "PRIVATE" and post["author_id"] != current_user_id:
        # Trả về 404 thay vì 403 để không làm lộ sự tồn tại của ID riêng tư
        return make_error_response(404, "NOT_FOUND", "Không tìm thấy bài viết hoặc bài viết không tồn tại")

    # 5. Khử dữ liệu nhạy cảm (Excessive Data Exposure protection):
    # Chỉ trả về AuthorSummary, không trả về email, phone, mật khẩu
    author_raw = next((u for u in MOCK_USERS.values() if u["id"] == post["author_id"]), None)
    author_summary = {
        "id": author_raw["id"] if author_raw else post["author_id"],
        "username": author_raw["username"] if author_raw else "anonymous",
        "display_name": author_raw["display_name"] if author_raw else "Người dùng ẩn danh",
        "avatar_url": author_raw["avatar_url"] if author_raw else "",
    }

    response_payload = {
        "id": post["id"],
        "author": author_summary,
        "content": post["content"],
        "media_urls": post["media_urls"],
        "privacy": post["privacy"],
        "created_at": post["created_at"],
        "updated_at": post["updated_at"],
        "likes_count": post["likes_count"],
        "comments_count": post["comments_count"],
    }
    return jsonify(response_payload), 200


if __name__ == "__main__":
    print("Khởi động Social Network API Demo tại http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
