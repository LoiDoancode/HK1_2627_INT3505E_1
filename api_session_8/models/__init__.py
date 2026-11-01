try:
    from .product import Product
    from .order import Order, OrderItem
except (ImportError, ValueError):
    from models.product import Product
    from models.order import Order, OrderItem

__all__ = ["Product", "Order", "OrderItem"]
