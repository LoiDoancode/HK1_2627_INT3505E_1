import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .factory import create_app
    from .extensions import db
except ImportError:
    from factory import create_app
    from extensions import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Tự động tạo bảng nếu chưa có (trong môi trường development/demo)
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))
    print(f" * Starting Product & Order API service on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

