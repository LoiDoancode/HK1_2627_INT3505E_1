try:
    from .product_schema import (
        ProductIn,
        ProductOut,
        ProductPatch,
        ReserveIn,
    )
    from .order_schema import (
        OrderIn,
        OrderOut,
        OrderItemIn,
        OrderItemOut,
    )
except (ImportError, ValueError):
    from schemas.product_schema import (
        ProductIn,
        ProductOut,
        ProductPatch,
        ReserveIn,
    )
    from schemas.order_schema import (
        OrderIn,
        OrderOut,
        OrderItemIn,
        OrderItemOut,
    )

__all__ = [
    "ProductIn",
    "ProductOut",
    "ProductPatch",
    "ReserveIn",
    "OrderIn",
    "OrderOut",
    "OrderItemIn",
    "OrderItemOut",
]
