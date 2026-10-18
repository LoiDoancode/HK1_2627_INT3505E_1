import base64
import json
from flask import Blueprint, request, jsonify
from sqlalchemy import select, func, tuple_
from models import db, Book, Category

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

ALLOWED_SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title,
    "created_at": Book.created_at,
    "stock": Book.stock
}

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def encode_cursor(payload: dict) -> str:
    """Mã hóa payload cursor sang URL-safe base64 không padding."""
    return base64.urlsafe_b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8").rstrip("=")


def decode_cursor(raw_token: str) -> dict:
    """Giải mã cursor token."""
    pad = "=" * (-len(raw_token) % 4)
    return json.loads(
        base64.urlsafe_b64decode((raw_token + pad).encode("utf-8")).decode("utf-8")
    )


def parse_sort(sort_param: str):
    """
    Xử lý chuỗi sort đa khóa (multi-key), ví dụ: '-price,title' hoặc 'price,-id'.
    Trả về:
      - primary_field_name: tên cột chính làm cursor value
      - primary_column: đối tượng cột SQLAlchemy của primary sort
      - is_desc: chiều sắp xếp của cột chính
      - order_clauses: danh sách biểu thức ORDER BY của SQLAlchemy
      - error_message: thông báo lỗi nếu có
    """
    if not sort_param:
        sort_param = "-id"

    parts = [item.strip() for item in sort_param.split(",") if item.strip()]
    if not parts:
        parts = ["-id"]

    order_clauses = []
    primary_field_name = None
    primary_column = None
    is_desc = False

    for index, token in enumerate(parts):
        descending = token.startswith("-")
        col_name = token.lstrip("-")

        if col_name not in ALLOWED_SORT_FIELDS:
            return None, None, None, None, f"Trường sắp xếp không hợp lệ: '{col_name}'"

        col = ALLOWED_SORT_FIELDS[col_name]
        order_clauses.append(col.desc() if descending else col.asc())

        if index == 0:
            primary_field_name = col_name
            primary_column = col
            is_desc = descending

    if primary_field_name != "id":
        order_clauses.append(Book.id.desc() if is_desc else Book.id.asc())

    return primary_field_name, primary_column, is_desc, order_clauses, None


@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor").lower()
    genre = request.args.get("genre")
    raw_sort = request.args.get("sort", "-id")

    #Kiểm tra và giới hạn limit
    try:
        limit = min(max(request.args.get("limit", DEFAULT_LIMIT, type=int), 1), MAX_LIMIT)
    except ValueError:
        limit = DEFAULT_LIMIT

    query = select(Book)

    #Filter theo genre (Category slug hoặc name)
    if genre:
        query = query.join(Book.category).filter(
            (Category.slug == genre.strip().lower()) | (Category.name.ilike(f"%{genre.strip()}%"))
        )

    # Xử lý Multi-key Sort
    p_name, p_col, is_desc, order_clauses, sort_err = parse_sort(raw_sort)
    if sort_err:
        return jsonify({"error": "bad_request", "message": sort_err}), 400

    query = query.order_by(*order_clauses)

    #Chiến lược OFFSET
    if strategy == "offset":
        offset = max(request.args.get("offset", 0, type=int), 0)

        # Tính tổng số bản ghi thỏa mãn điều kiện filter
        total_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = db.session.scalar(total_stmt)

        rows = db.session.scalars(query.offset(offset).limit(limit)).all()

        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_next": (offset + limit) < total
            }
        }), 200

    #Chiến lược CURSOR (Seek pagination)
    elif strategy == "cursor":
        raw_cursor = request.args.get("cursor")

        if raw_cursor:
            try:
                cursor_state = decode_cursor(raw_cursor)
            except Exception:
                return jsonify({
                    "error": "invalid_cursor",
                    "message": "Cursor không đúng định dạng base64"
                }), 400

            if cursor_state.get("s") != raw_sort:
                return jsonify({
                    "error": "sort_mismatch",
                    "message": "Cursor không hợp lệ do cấu hình sắp xếp (sort) đã thay đổi"
                }), 400

            cursor_val = cursor_state.get("v")
            cursor_id = cursor_state.get("i")

            op = "<" if is_desc else ">"
            seek_filter = tuple_(p_col, Book.id).op(op)((cursor_val, cursor_id))
            query = query.filter(seek_filter)

        # Áp dụng trick limit + 1
        records = db.session.scalars(query.limit(limit + 1)).all()
        has_more = len(records) > limit
        items = records[:limit]

        next_cursor = None
        if items and has_more:
            last_record = items[-1]
            # Lấy giá trị của trường sort chính
            if p_name == "price":
                val = last_record.price_vnd
            elif p_name == "created_at":
                val = last_record.created_at.isoformat()
            elif p_name == "id":
                val = last_record.id
            else:
                val = getattr(last_record, p_name)

            next_cursor = encode_cursor({
                "s": raw_sort,
                "v": val,
                "i": last_record.id
            })

        return jsonify({
            "data": [b.to_dict() for b in items],
            "pagination": {
                "strategy": "cursor",
                "limit": limit,
                "has_more": has_more,
                "next_cursor": next_cursor
            }
        }), 200

    else:
        return jsonify({
            "error": "bad_request",
            "message": f"Strategy '{strategy}' không hỗ trợ. Chỉ hỗ trợ 'offset' hoặc 'cursor'."
        }), 400