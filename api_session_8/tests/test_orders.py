import pytest
try:
    from extensions import db
    from models import Product
except (ImportError, ValueError):
    from api_session_8.extensions import db
    from api_session_8.models import Product

def test_post_order_endpoint_success(client, sample_products):
    """
    Test Bài tập 5: POST endpoint (/api/v1/orders)
    - Tạo đơn hàng có nhiều OrderItem liên kết Product
    - Kiểm tra trừ tồn kho của từng sản phẩm tương ứng
    - Kiểm tra tính toán total_amount_cents chuẩn xác
    """
    p1_id, p2_id = sample_products[0], sample_products[1]

    payload = {
        "customer_name": "Doãn Duy Lợi",
        "customer_email": "loi.dd@example.com",
        "items": [
            {"product_id": p1_id, "quantity": 2},  # 2 * 79900 = 159800
            {"product_id": p2_id, "quantity": 1},  # 1 * 129900 = 129900
        ]
    }

    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 201
    data = res.get_json()

    # Kiểm tra tính toán tổng tiền
    expected_total = (2 * 79900) + (1 * 129900)
    assert data["total_amount_cents"] == expected_total
    assert data["customer_name"] == "Doãn Duy Lợi"
    assert len(data["items"]) == 2

    # Kiểm tra tồn kho của từng Product đã được trừ chính xác
    res_p1 = client.get(f"/api/v1/products/{p1_id}").get_json()
    res_p2 = client.get(f"/api/v1/products/{p2_id}").get_json()
    assert res_p1["qty_in_stock"] == 10 - 2  # 8
    assert res_p2["qty_in_stock"] == 5 - 1   # 4

def test_post_order_insufficient_stock(client, sample_products):
    """
    Test POST /api/v1/orders thất bại và rollback khi không đủ hàng tồn kho (409)
    """
    p1_id = sample_products[0]  # Tồn kho = 10

    payload = {
        "customer_name": "Nguyen Van B",
        "items": [
            {"product_id": p1_id, "quantity": 999}
        ]
    }
    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 409
    data = res.get_json()
    assert data["code"] == "out_of_stock"

    # Kiểm tra tồn kho không bị trừ (được rollback an toàn)
    res_p1 = client.get(f"/api/v1/products/{p1_id}").get_json()
    assert res_p1["qty_in_stock"] == 10

def test_get_order_eager_loading_prevents_n_plus_one(client, sample_products, query_counter):
    """
    Test Bài tập 5: GET endpoint có EAGER LOADING và kiểm tra số truy vấn để phát hiện N+1 (Slide 18, 19, 40)
    
    Kịch bản:
    - Tạo 3 đơn hàng, mỗi đơn hàng chứa nhiều OrderItem liên kết các Product.
    - Gọi GET /api/v1/orders để lấy danh sách đơn hàng kèm chi tiết items và product.
    - Với bẫy N+1 (Lazy loading): Số câu query SQL sẽ tăng theo số đơn hàng và items:
      1 (lấy orders) + N (lấy items) + M (lấy products) => hàng chục queries!
    - Với Eager Loading (selectinload): Số câu query SQL là HẰNG SỐ (chỉ 2 hoặc 3 queries)
      dù danh sách có bao nhiêu đơn hàng!
    """
    p1, p2, p3 = sample_products

    # 1. Tạo 3 đơn hàng
    for i in range(3):
        client.post("/api/v1/orders", json={
            "customer_name": f"Khách hàng {i+1}",
            "items": [
                {"product_id": p1, "quantity": 1},
                {"product_id": p2, "quantity": 1},
                {"product_id": p3, "quantity": 1},
            ]
        })

    # 2. Đo số câu truy vấn khi gọi GET /api/v1/orders
    with query_counter as qc:
        res = client.get("/api/v1/orders?page=1&size=10")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["items"]) == 3

        # Đảm bảo dữ liệu quan hệ được tải đầy đủ
        for order in data["items"]:
            assert len(order["items"]) == 3
            for item in order["items"]:
                assert "product" in item
                assert "name" in item["product"]

    # 3. Khẳng định số truy vấn SQL:
    # 1 query: SELECT count() (cho phân trang)
    # 1 query: SELECT orders
    # 1 query: SELECT order_items WHERE order_id IN (...)
    # 1 query: SELECT products WHERE id IN (...)
    # Tổng cộng chỉ 4 câu truy vấn cố định, KHÔNG PHẢI 1 + 3*(1 + 3) = 13 câu truy vấn nếu bị bẫy N+1!
    print(f"\n[EAGER LOADING TEST] Số câu truy vấn SELECT phát ra: {qc.count}")
    for idx, sql in enumerate(qc.statements, 1):
        print(f"Query {idx}: {sql.strip()[:100]}...")

    assert qc.count <= 6, f"Phát hiện bẫy N+1 query! Số query thực thi: {qc.count}"

def test_healthz_and_ready_probes(client):
    """
    Test Bài tập 4: Kiểm tra 2 probe /healthz và /ready riêng biệt (Slide 34 & 35)
    """
    # 1. Liveness Probe
    res_liveness = client.get("/healthz")
    assert res_liveness.status_code == 200
    assert res_liveness.get_json() == {"status": "ok"}

    # 2. Readiness Probe
    res_readiness = client.get("/ready")
    assert res_readiness.status_code == 200
    data = res_readiness.get_json()
    assert data["status"] == "ok"
    assert data["checks"]["db"] == "ok"

