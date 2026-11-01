from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
try:
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
except ImportError:
    MarshmallowValidationError = None

try:
    from ..extensions import db
    from ..models import Product
    from ..errors import Conflict, NotFound, OutOfStock, ValidationError
    from ..schemas import (
        ProductOut,
        ProductIn,
        ProductPatch,
        ReserveIn,
    )
except (ImportError, ValueError):
    from extensions import db
    from models import Product
    from errors import Conflict, NotFound, OutOfStock, ValidationError
    from schemas import (
        ProductOut,
        ProductIn,
        ProductPatch,
        ReserveIn,
    )

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")

def _validate_schema(schema, data, partial=False):
    """Tiện ích validate schema an toàn với mã lỗi 422 (Slide 27)"""
    try:
        if partial:
            return schema.load(data, partial=True)
        return schema.load(data)
    except Exception as err:
        if MarshmallowValidationError and isinstance(err, MarshmallowValidationError):
            raise ValidationError(
                message="Dữ liệu đầu vào không hợp lệ",
                detail=str(err.messages)
            )
        elif isinstance(err, ValidationError):
            raise err
        raise ValidationError(message=str(err))

@products_bp.get("")
def list_products():
    """
    1. Lấy danh sách sản phẩm có phân trang (Slide 22 & 25)
    Query params: ?page=1&size=20
    Mặc định loại trừ các sản phẩm đã bị soft-delete (archived=True).
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        size = min(100, max(1, int(request.args.get("size", 20))))
    except (ValueError, TypeError):
        size = 20

    base = db.select(Product).where(Product.archived.is_(False))
    rows = db.session.execute(
        base.order_by(Product.id).offset((page - 1) * size).limit(size)
    ).scalars().all()

    total = db.session.scalar(
        db.select(db.func.count()).select_from(Product).where(Product.archived.is_(False))
    ) or 0

    return jsonify({
        "items": [ProductOut().dump(p) for p in rows],
        "page": page,
        "size": size,
        "total": total,
    }), 200

@products_bp.get("/<int:id>")
def get_product(id):
    """
    2. Lấy 1 sản phẩm theo ID (Slide 22)
    Trả về 404 nếu không tìm thấy hoặc đã bị soft-delete.
    """
    p = db.session.scalar(
        db.select(Product).where(Product.id == id, Product.archived.is_(False))
    )
    if not p:
        raise NotFound(message="Không tìm thấy sản phẩm")
    return jsonify(ProductOut().dump(p)), 200

@products_bp.post("")
def create_product():
    """
    3. Tạo sản phẩm mới (Slide 22 & 26)
    Validate body JSON qua ProductIn schema.
    Trả về 409 nếu SKU đã tồn tại (IntegrityError).
    """
    payload = request.get_json(silent=True) or {}
    body = _validate_schema(ProductIn(), payload)

    p = Product(**body)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict(message="sku already exists")

    return jsonify(ProductOut().dump(p)), 201

@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    """
    4. Đặt trước (reserve) sản phẩm - trừ tồn kho (Slide 22)
    Body: {"qty": 1}
    Trả về 404 nếu không tìm thấy sản phẩm hoặc đã archived.
    Trả về 409 nếu kho không đủ (qty_in_stock < qty).
    """
    payload = request.get_json(silent=True) or {}
    body = _validate_schema(ReserveIn(), payload)
    qty = body["qty"]

    p = db.session.scalar(
        db.select(Product).where(Product.id == id, Product.archived.is_(False))
    )
    if not p:
        raise NotFound(message="Không tìm thấy sản phẩm")

    if p.qty_in_stock < qty:
        raise OutOfStock(
            message=f"only {p.qty_in_stock} left",
            detail=f"Số lượng yêu cầu ({qty}) vượt quá tồn kho hiện có ({p.qty_in_stock})"
        )

    p.qty_in_stock -= qty
    db.session.commit()

    return jsonify({
        "message": f"Đặt trước thành công {qty} sản phẩm",
        "reserved_qty": qty,
        "product": ProductOut().dump(p),
    }), 200

@products_bp.patch("/<int:id>")
def patch_product(id):
    """
    5. Cập nhật một phần sản phẩm (Slide 22 & 26)
    Chỉ field có trong body mới được cập nhật.
    """
    payload = request.get_json(silent=True) or {}
    body = _validate_schema(ProductPatch(), payload, partial=True)

    p = db.session.scalar(
        db.select(Product).where(Product.id == id, Product.archived.is_(False))
    )
    if not p:
        raise NotFound(message="Không tìm thấy sản phẩm")

    for k, v in body.items():
        setattr(p, k, v)

    db.session.commit()
    return jsonify(ProductOut().dump(p)), 200

@products_bp.delete("/<int:id>")
def delete_product(id):
    """
    6. Soft-delete sản phẩm (Slide 22 & 26)
    Đánh dấu archived=True.
    """
    p = db.session.scalar(
        db.select(Product).where(Product.id == id, Product.archived.is_(False))
    )
    if not p:
        raise NotFound(message="Không tìm thấy sản phẩm")

    p.archived = True
    db.session.commit()
    return "", 204
