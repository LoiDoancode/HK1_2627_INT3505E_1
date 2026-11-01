from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
try:
    from marshmallow.exceptions import ValidationError as MarshmallowValidationError
except ImportError:
    MarshmallowValidationError = None

try:
    from ..extensions import db
    from ..models import Order, OrderItem, Product
    from ..errors import NotFound, OutOfStock, ValidationError
    from ..schemas import OrderIn, OrderOut
except (ImportError, ValueError):
    from extensions import db
    from models import Order, OrderItem, Product
    from errors import NotFound, OutOfStock, ValidationError
    from schemas import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

def _validate_schema(schema, data):
    """Tiện ích validate an toàn với mã lỗi 422"""
    try:
        return schema.load(data)
    except Exception as err:
        if MarshmallowValidationError and isinstance(err, MarshmallowValidationError):
            raise ValidationError(
                message="Dữ liệu đơn hàng không hợp lệ",
                detail=str(err.messages)
            )
        elif isinstance(err, ValidationError):
            raise err
        raise ValidationError(message=str(err))

@orders_bp.post("")
def create_order():
    """
    Tạo đơn hàng mới gồm nhiều OrderItem (Bài tập 2 - Slide 40)
    Một Order liên kết nhiều OrderItem, mỗi OrderItem liên kết 1 Product.
    Trừ tồn kho atomic trong 1 transaction; raise OutOfStock (409) nếu thiếu hàng.
    """
    payload = request.get_json(silent=True) or {}
    data = _validate_schema(OrderIn(), payload)

    customer_name = data["customer_name"]
    customer_email = data.get("customer_email")
    items_input = data["items"]

    total_amount_cents = 0
    order_items = []

    # Xử lý atomic: kiểm tra từng sản phẩm và trừ tồn kho
    for item in items_input:
        pid = item["product_id"]
        qty = item["quantity"]

        product = db.session.scalar(
            db.select(Product).where(Product.id == pid, Product.archived.is_(False))
        )
        if not product:
            db.session.rollback()
            raise NotFound(
                message=f"Sản phẩm ID {pid} không tồn tại hoặc đã ngừng kinh doanh"
            )

        if product.qty_in_stock < qty:
            db.session.rollback()
            raise OutOfStock(
                message=f"Sản phẩm '{product.name}' (SKU: {product.sku}) không đủ tồn kho",
                detail=f"Yêu cầu: {qty}, hiện còn: {product.qty_in_stock}"
            )

        # Trừ tồn kho sản phẩm
        product.qty_in_stock -= qty

        # Lưu đơn giá snapshot tại thời điểm mua
        subtotal = qty * product.price_cents
        total_amount_cents += subtotal

        order_item = OrderItem(
            product=product,
            product_id=product.id,
            quantity=qty,
            unit_price_cents=product.price_cents
        )
        order_items.append(order_item)

    # Khởi tạo Order và liên kết các OrderItem
    order = Order(
        customer_name=customer_name,
        customer_email=customer_email,
        total_amount_cents=total_amount_cents,
        status="COMPLETED",
        items=order_items
    )

    db.session.add(order)
    db.session.commit()

    return jsonify(OrderOut().dump(order)), 201

@orders_bp.get("")
def list_orders():
    """
    Lấy danh sách đơn hàng có phân trang
    ÁP DỤNG EAGER LOADING (selectinload) để triệt tiêu bẫy N+1 query (Slide 18 & 19).
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        size = min(100, max(1, int(request.args.get("size", 20))))
    except (ValueError, TypeError):
        size = 20

    # Eager load items và product trong 2-3 query SELECT IN thay vì 1 + 2N query
    stmt = (
        db.select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .order_by(Order.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    orders = db.session.execute(stmt).scalars().all()

    total = db.session.scalar(
        db.select(db.func.count()).select_from(Order)
    ) or 0

    return jsonify({
        "items": [OrderOut().dump(o) for o in orders],
        "page": page,
        "size": size,
        "total": total,
    }), 200

@orders_bp.get("/<int:id>")
def get_order(id):
    """
    Lấy chi tiết 1 đơn hàng kèm toàn bộ OrderItem và Product
    Sử dụng selectinload để eager-load quan hệ 1-N.
    """
    stmt = (
        db.select(Order)
        .where(Order.id == id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    order = db.session.scalar(stmt)
    if not order:
        raise NotFound(message="Không tìm thấy đơn hàng")

    return jsonify(OrderOut().dump(order)), 200
