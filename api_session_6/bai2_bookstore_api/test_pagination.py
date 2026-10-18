import pytest
from app import create_app
from models import db, Book, Category

@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    with app.app_context():
        c_tech = Category(name="Technology", slug="tech")
        c_sci = Category(name="Science", slug="science")
        db.session.add_all([c_tech, c_sci])
        db.session.commit()

        for i in range(1, 36):
            b = Book(
                title=f"Sample Book {i:02d}",
                isbn=f"9780000000{i:03d}",
                price_vnd=float(50000 + (i % 4) * 20000),
                stock=i,
                category_id=c_tech.id if i % 2 == 0 else c_sci.id
            )
            db.session.add(b)
        db.session.commit()

        yield app.test_client()

def test_offset_pagination_success(client):
    """Kiểm tra chiến lược Offset trang đầu và metadata tổng quan."""
    res = client.get("/api/v1/books?strategy=offset&offset=0&limit=10")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) == 10
    assert body["pagination"]["strategy"] == "offset"
    assert body["pagination"]["total"] == 35
    assert body["pagination"]["has_next"] is True

def test_offset_pagination_last_page(client):
    """Kiểm tra chiến lược Offset ở trang cuối cùng."""
    res = client.get("/api/v1/books?strategy=offset&offset=30&limit=10")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) == 5
    assert body["pagination"]["has_next"] is False

def test_cursor_pagination_flow(client):
    """Kiểm tra duyệt cursor tuần tự qua các trang, đảm bảo không trùng lặp và không sót."""
    # Lấy trang 1
    res1 = client.get("/api/v1/books?strategy=cursor&limit=15&sort=-id")
    assert res1.status_code == 200
    body1 = res1.get_json()
    assert len(body1["data"]) == 15
    assert body1["pagination"]["has_more"] is True
    cursor1 = body1["pagination"]["next_cursor"]
    assert cursor1 is not None

    # Lấy trang 2 bằng next_cursor
    res2 = client.get(f"/api/v1/books?strategy=cursor&limit=15&sort=-id&cursor={cursor1}")
    assert res2.status_code == 200
    body2 = res2.get_json()
    assert len(body2["data"]) == 15
    assert body2["pagination"]["has_more"] is True

    # Xác minh các ID giữa 2 trang hoàn toàn không giao nhau
    page1_ids = {item["raw_id"] for item in body1["data"]}
    page2_ids = {item["raw_id"] for item in body2["data"]}
    assert page1_ids.isdisjoint(page2_ids)

def test_cursor_sort_mismatch_rejection(client):
    """Đảm bảo trả về HTTP 400 nếu client đổi sort giữa chừng khi đang dùng cursor."""
    res = client.get("/api/v1/books?strategy=cursor&limit=10&sort=-id")
    cursor = res.get_json()["pagination"]["next_cursor"]

    # Thay đổi sort sang -price nhưng dùng cursor cũ
    res_err = client.get(f"/api/v1/books?strategy=cursor&limit=10&sort=-price&cursor={cursor}")
    assert res_err.status_code == 400
    assert res_err.get_json()["error"] == "sort_mismatch"

def test_filter_by_genre(client):
    """Kiểm tra bộ lọc theo genre."""
    res = client.get("/api/v1/books?strategy=offset&genre=tech")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) > 0
    for book in body["data"]:
        assert book["category"]["slug"] == "tech"

def test_multi_key_sorting(client):
    """Kiểm tra sort đa khóa: ?sort=price,-id."""
    res = client.get("/api/v1/books?strategy=offset&limit=20&sort=price,-id")
    assert res.status_code == 200
    body = res.get_json()
    prices = [b["price"]["amount"] for b in body["data"]]
    # Danh sách giá phải tăng dần
    assert prices == sorted(prices)

def test_invalid_sort_field_whitelist(client):
    """Kiểm tra ngăn chặn trường sắp xếp không nằm trong whitelist."""
    res = client.get("/api/v1/books?sort=password_hash")
    assert res.status_code == 400
    assert "Trường sắp xếp không hợp lệ" in res.get_json()["message"]