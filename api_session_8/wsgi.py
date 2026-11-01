import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .factory import create_app
    from .extensions import db
except (ImportError, ValueError):
    from factory import create_app
    from extensions import db

# Entrypoint cho Gunicorn WSGI Server (Slide 37)
app = create_app()

with app.app_context():
    # Tự động khởi tạo cấu trúc các bảng (products, orders, order_items) nếu chưa tồn tại
    db.create_all()

if __name__ == "__main__":
    app.run()
