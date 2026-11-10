import json

def test_list_products_pagination(client, sample_products):
    """Test: GET /api/v1/products có phân trang"""
    res = client.get("/api/v1/products?page=1&size=2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 2

def test_get_product_by_id_success(client, sample_products):
    """Test: GET /api/v1/products/<id> lấy sản phẩm thành công"""
    pid = sample_products[0]
    res = client.get(f"/api/v1/products/{pid}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == pid
    assert data["sku"] == "IPHONE-15"

def test_get_product_not_found(client):
    """Test: GET /api/v1/products/<id> 404 nếu không tìm thấy"""
    res = client.get("/api/v1/products/99999")
    assert res.status_code == 404
    data = res.get_json()
    assert data["code"] == "not_found"

def test_create_product_success(client):
    """Test: POST /api/v1/products tạo sản phẩm thành công (201)"""
    payload = {
        "sku": "SAMSUNG-S24",
        "name": "Samsung Galaxy S24",
        "price_cents": 89900,
        "qty_in_stock": 15,
        "description": "Flagship Android phone"
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["sku"] == "SAMSUNG-S24"
    assert data["price_cents"] == 89900
    assert data["qty_in_stock"] == 15

def test_create_product_duplicate_sku(client, sample_products):
    """Test: POST /api/v1/products 409 nếu trùng SKU"""
    payload = {
        "sku": "IPHONE-15",
        "name": "iPhone 15 Fake",
        "price_cents": 10000,
        "qty_in_stock": 1
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 409
    data = res.get_json()
    assert data["code"] == "conflict"

def test_reserve_product_success(client, sample_products):
    """Test: POST /api/v1/products/<id>/reserve đặt hàng thành công"""
    pid = sample_products[0]  # Tồn kho ban đầu = 10
    res = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 3})
    assert res.status_code == 200
    data = res.get_json()
    assert data["product"]["qty_in_stock"] == 7

def test_reserve_product_out_of_stock(client, sample_products):
    """Test: POST /api/v1/products/<id>/reserve 409 nếu số lượng vượt quá tồn kho"""
    pid = sample_products[0]  # Tồn kho = 10
    res = client.post(f"/api/v1/products/{pid}/reserve", json={"qty": 999})
    assert res.status_code == 409
    data = res.get_json()
    assert data["code"] == "out_of_stock"

def test_patch_product(client, sample_products):
    """Test: PATCH /api/v1/products/<id> cập nhật một phần"""
    pid = sample_products[1]
    res = client.patch(f"/api/v1/products/{pid}", json={"price_cents": 119900})
    assert res.status_code == 200
    data = res.get_json()
    assert data["price_cents"] == 119900
    assert data["sku"] == "MACBOOK-M3"  # Các trường khác giữ nguyên

def test_delete_product_soft_delete(client, sample_products):
    """Test: DELETE /api/v1/products/<id> soft-delete"""
    pid = sample_products[2]
    res = client.delete(f"/api/v1/products/{pid}")
    assert res.status_code == 204

    # Sau khi xóa soft-delete, truy vấn GET phải trả về 404
    get_res = client.get(f"/api/v1/products/{pid}")
    assert get_res.status_code == 404

