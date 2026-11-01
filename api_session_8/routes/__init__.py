try:
    from .products import products_bp
    from .orders import orders_bp
    from .health import health_bp
except (ImportError, ValueError):
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.health import health_bp

__all__ = ["products_bp", "orders_bp", "health_bp"]
