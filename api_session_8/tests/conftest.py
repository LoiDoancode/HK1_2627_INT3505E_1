import os
import sys
import pytest
from sqlalchemy import event

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from config import TestConfig
    from factory import create_app
    from extensions import db
    from models import Product, Order, OrderItem
except (ImportError, ValueError):
    from api_session_8.config import TestConfig
    from api_session_8.factory import create_app
    from api_session_8.extensions import db
    from api_session_8.models import Product, Order, OrderItem

class QueryCounter:
    """
    Context Manager hỗ trợ đếm số câu truy vấn SQL (Slide 18, 19, 40)
    Sử dụng event listener của SQLAlchemy để bắt các câu lệnh SELECT.
    """
    def __init__(self, engine):
        self.engine = engine
        self.count = 0
        self.statements = []

    def __enter__(self):
        self.count = 0
        self.statements.clear()
        event.listen(self.engine, "before_cursor_execute", self._callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        event.remove(self.engine, "before_cursor_execute", self._callback)

    def _callback(self, conn, cursor, statement, parameters, context, executemany):
        clean_stmt = statement.strip().upper()
        # Chỉ tính các câu lệnh SELECT liên quan đến dữ liệu (loại bỏ PRAGMA và SAVEPOINT)
        if clean_stmt.startswith("SELECT") and "PRAGMA" not in clean_stmt:
            self.count += 1
            self.statements.append(statement)

@pytest.fixture
def app():
    """Khởi tạo Flask App với TestConfig (SQLite in-memory)"""
    test_app = create_app(TestConfig)
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client cho HTTP requests"""
    return app.test_client()

@pytest.fixture
def query_counter(app):
    """Fixture trả về QueryCounter liên kết với database engine hiện tại"""
    with app.app_context():
        counter = QueryCounter(db.engine)
        yield counter

@pytest.fixture
def sample_products(app):
    """Fixture nạp sẵn một số sản phẩm mẫu vào DB phục vụ test"""
    with app.app_context():
        p1 = Product(
            sku="IPHONE-15",
            name="iPhone 15 128GB",
            price_cents=79900,
            qty_in_stock=10,
            description="Apple smartphone",
            archived=False,
        )
        p2 = Product(
            sku="MACBOOK-M3",
            name="MacBook Air M3",
            price_cents=129900,
            qty_in_stock=5,
            description="Apple laptop",
            archived=False,
        )
        p3 = Product(
            sku="AIRPODS-PRO",
            name="AirPods Pro 2",
            price_cents=24900,
            qty_in_stock=20,
            description="Apple earbuds",
            archived=False,
        )
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        return [p1.id, p2.id, p3.id]

