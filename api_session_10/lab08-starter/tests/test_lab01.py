"""LAB 1 — Test suite for Books API.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema


# Test A: GET /books khi CSDL rỗng trả về mảng rỗng (không phải null)
def test_get_books_empty_db(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert data == []
    assert data is not None
    assert isinstance(data, list)


# Test B: GET /books/<id> với id không tồn tại trả về 404 + JSON chứa "code": "NOT_FOUND"
def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == "NOT_FOUND"


# Test C: POST /books thiếu title trả về 400 + trong errors có field "title"
def test_post_book_missing_title(client):
    response = client.post("/books", json={"author": "Robert C. Martin"})
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("code") == "VALIDATION_ERROR"
    assert "errors" in data
    error_fields = [err["field"] for err in data["errors"]]
    assert "title" in error_fields


# Test D: Xoá rồi GET cùng id — phải trả về 404
def test_delete_then_get_same_id(client):
    # 1. Tạo một cuốn sách hợp lệ
    post_res = client.post(
        "/books",
        json={"title": "Design Patterns", "author": "GoF", "year": 1994}
    )
    assert post_res.status_code == 201
    book_id = post_res.get_json()["id"]

    # 2. Xoá cuốn sách vừa tạo
    del_res = client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204

    # 3. GET lại cùng id đó -> phải trả về 404
    get_res = client.get(f"/books/{book_id}")
    assert get_res.status_code == 404
    assert get_res.get_json().get("code") == "NOT_FOUND"


# Bước 2 - BONUS: Test chứng minh backend không lộ password_hash
@pytest.fixture
def book_with_password_hash(client, sample_book):
    """Fixture giả lập dữ liệu response bị inject/lộ field lạ password_hash."""
    response = client.get(f"/books/{sample_book}")
    data = response.get_json().copy()
    data["password_hash"] = "pbkdf2:sha256:260000$fakepasswordhash"
    return data


def test_response_extra_field_blocked(client, sample_book, book_with_password_hash):
    """Bonus test: Dùng jsonschema chứng minh backend không lộ password_hash."""
    schema = get_book_schema()

    # 1. Xác nhận response thực tế từ backend tuân thủ schema (không có field thừa)
    real_response = client.get(f"/books/{sample_book}")
    assert real_response.status_code == 200
    real_data = real_response.get_json()
    validate(instance=real_data, schema=schema)
    assert "password_hash" not in real_data

    # 2. Giả lập add field lạ (password_hash) trong fixture -> jsonschema phải chặn và văng ValidationError
    with pytest.raises(ValidationError):
        validate(instance=book_with_password_hash, schema=schema)
