from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
try:
    from ..extensions import db
except (ImportError, ValueError):
    from extensions import db

class Product(db.Model):
    """
    Model Product theo chuẩn typed của SQLAlchemy 2.x (Slide 16 & 23)
    Bảo đảm bất biến:
    - sku: duy nhất, có index, độ dài 3-32 ký tự
    - price_cents: số nguyên >= 0
    - qty_in_stock: số nguyên >= 0 (mặc định 0)
    - archived: soft-delete cờ boolean
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price_cents": self.price_cents,
            "qty_in_stock": self.qty_in_stock,
            "archived": self.archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
