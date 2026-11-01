from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
try:
    from ..extensions import db
    from .product import Product
except (ImportError, ValueError):
    from extensions import db
    from models.product import Product

class Order(db.Model):
    """
    Model Order (Bài tập về nhà 2 - Slide 40)
    Một Order có nhiều OrderItem (quan hệ 1-N).
    Tránh bẫy N+1 bằng eager loading selectinload khi truy vấn.
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    total_amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )

    # Quan hệ 1-N với OrderItem
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderItem.id"
    )

    def __init__(
        self,
        customer_name: str = "",
        customer_email: Optional[str] = None,
        status: str = "COMPLETED",
        total_amount_cents: int = 0,
        items: Optional[List["OrderItem"]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.status = status
        self.total_amount_cents = total_amount_cents
        if items is not None:
            self.items = items

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "status": self.status,
            "total_amount_cents": self.total_amount_cents,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }

class OrderItem(db.Model):
    """
    Bảng trung gian OrderItem liên kết Order và Product (N-1 với mỗi phía)
    Lưu snapshot đơn giá unit_price_cents tại thời điểm đặt hàng.
    """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

    def __init__(
        self,
        product_id: int = 0,
        quantity: int = 0,
        unit_price_cents: int = 0,
        product: Optional["Product"] = None,
        order_id: Optional[int] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        if product is not None:
            self.product = product
        if order_id is not None:
            self.order_id = order_id

    @property
    def subtotal_cents(self) -> int:
        return self.quantity * self.unit_price_cents

    def to_dict(self):
        data = {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price_cents": self.unit_price_cents,
            "subtotal_cents": self.quantity * self.unit_price_cents,
        }
        if self.product:
            data["product"] = {
                "id": self.product.id,
                "sku": self.product.sku,
                "name": self.product.name,
                "price_cents": self.product.price_cents,
            }
        return data
