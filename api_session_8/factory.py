import os
from flask import Flask

try:
    from .extensions import db, migrate
    from .config import DefaultConfig
    from .logging_config import configure_logging
    from .errors import register_error_handlers
    from .routes.products import products_bp
    from .routes.orders import orders_bp
    from .routes.health import health_bp
except ImportError:
    from extensions import db, migrate
    from config import DefaultConfig
    from logging_config import configure_logging
    from errors import register_error_handlers
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.health import health_bp

def create_app(config=None):
    """
    Application Factory Pattern (Slide 11 & 14)
    Lợi ích:
    1. Cấu hình linh hoạt theo từng môi trường (Test, Dev, Prod).
    2. Tránh triệt để import vòng.
    3. Hỗ trợ tạo app độc lập cho pytest test runner.
    """
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)

    # Đọc thêm biến môi trường dạng APP_* (Slide 31)
    app.config.from_prefixed_env("APP")

    # 1. Cấu hình structured logging
    configure_logging(app)

    # 2. Khởi tạo các extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. Đăng ký global error handlers
    register_error_handlers(app)

    # 4. Đăng ký các blueprints
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)

    return app

