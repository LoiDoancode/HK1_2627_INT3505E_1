# Lab 4 — Phân tích kết quả Load Test (Locust)

> **Môi trường đo:** Localhost (`http://127.0.0.1:5000`), Flask 3.1.3 development server (Werkzeug threaded WSGI), SQLite (`instance/books.db`).
> **Cấu hình task:** `GET /books` (weight 3), `GET /books/{id}` (weight 2), `GET /books?year={year}` (weight 2, có 1% client-side failure injection), `POST /books` (weight 1). `wait_time = between(1, 3)`.

## Bảng tổng hợp kết quả đo thực tế

| Kịch bản | Users | Spawn rate | Duration | Tổng reqs | p50 (ms) | p95 (ms) | p99 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **A** (Baseline) | 10 | 2/s | 30s | 125 | 5 | 24 | 29 | 0.00% (0/125) | 4.78 |
| **B** (Load test) | 50 | 5/s | 60s | 1396 | 6 | 27 | 46 | 0.36% (5/1396) | 23.54 |
| **C** (Spike test) | 200 | 50/s | 30s | 2851 | 12 | 130 | 250 | 0.35% (10/2851) | 96.63 |

### Chi tiết theo từng endpoint (Kịch bản C — 200 users)

| Endpoint | Reqs | Fails | Avg (ms) | p50 (ms) | p95 (ms) | Max (ms) | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `GET /books` | 1057 | 0 (0.00%) | 27 | 12 | 140 | 382 | 35.82 |
| `GET /books/{id}` | 715 | 0 (0.00%) | 26 | 11 | 140 | 291 | 24.23 |
| `GET /books?year={year}` | 739 | 10 (1.35%) | 23 | 11 | 93 | 297 | 25.05 |
| `POST /books` | 340 | 0 (0.00%) | 44 | 29 | 150 | 403 | 11.52 |

---

## Trả lời các câu hỏi phân tích

### 1. Trong 3 kịch bản, kịch bản nào có p95 cao nhất? Vì sao?

- **Kịch bản C (Spike test, 200 users, spawn rate 50/s)** có `p95` cao nhất: **130 ms** (so với **24 ms** ở A và **27 ms** ở B).
- **Giải thích dựa trên số liệu:**
  - Khi tăng từ 10 users (A) lên 50 users (B), `p95` chỉ tăng nhẹ từ `24 ms` lên `27 ms` (+12.5%), cho thấy hệ thống vẫn còn nhiều headroom ở mức ~23.5 RPS.
  - Khi tăng đột ngột lên 200 users với tốc độ spawn `50 users/s` (C), `p95` tăng phi tuyến gần **4.8 lần** lên `130 ms` (và `p99` nhảy lên `250 ms`, `max` đạt `403 ms`). Đặc biệt trong 3 giây đầu ramp-up (đạt đủ 200 users), độ trễ trung bình vọt lên `107–115 ms` do các request đến cùng lúc phải xếp hàng chờ Flask development server (single-process threaded) và khóa ghi SQLite (`POST /books` có `p95 = 150 ms`, cao nhất trong các endpoint).

### 2. Có endpoint nào fail rate tăng theo số user? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.

- **Không có endpoint nào tăng failure rate do lỗi hệ thống theo số user.**
  - Toàn bộ lỗi ghi nhận được chỉ xuất hiện trên `GET /books?year={year}`:
    - Kịch bản A: `0/34` (`0.00%`)
    - Kịch bản B: `5/351` (`1.42%`)
    - Kịch bản C: `10/739` (`1.35%`)
  - Mọi endpoint còn lại (`GET /books`, `GET /books/{id}`, `POST /books`) đều đạt **0.00% failure** ở cả 3 kịch bản (lưu ý `GET /books/{id}` có `404` khi random id chưa tồn tại nhưng đã được `catch_response=True` coi là `response.success()` đúng theo nghiệp vụ).
- **Phân biệt lỗi HTTP thực vs lỗi đánh dấu trong Locust:**
  - Các lỗi trên `GET /books?year={year}` trong `performance/locustfile.py` **KHÔNG phải HTTP 500 thực tế từ Flask server**, mà là **client-side artificial failure** do `random.random() < 0.01` gọi `response.failure("Simulated 500 (client-side 1% failure injection)")` dù server vẫn trả về `200 OK`.
  - Tỉ lệ ~1.35%–1.42% ở B và C dao động quanh mức 1% kỳ vọng do kích thước mẫu ngẫu nhiên (không phải do quá tải tăng theo số user). Nếu backend thực sự quá tải (VD: SQLite `database is locked` hoặc timeout), server sẽ trả HTTP `500` hoặc `ReadTimeout` thật và failure rate sẽ tăng vọt ở kịch bản C (đặc biệt trên `POST /books`).

### 3. Với SLO giả định `p95 < 300 ms`, kịch bản nào đạt? Đề xuất baseline cho CI gate & giới hạn phép đo.

- **Kết quả theo SLO `p95 < 300 ms`:**
  - **Cả 3 kịch bản A (`24 ms`), B (`27 ms`), C (`130 ms`) đều đạt** ngưỡng `p95 < 300 ms` trên tổng hợp (`Aggregated`) cũng như từng endpoint riêng lẻ (endpoint cao nhất ở C là `POST /books` với `p95 = 150 ms`).
  - Tuy nhiên ở kịch bản C, `p99 = 250 ms` và `max = 403 ms` đã tiệm cận/vượt ngưỡng 300 ms, báo hiệu bắt đầu xuất hiện tail latency khi có spike 200 users.
- **Đề xuất baseline cho CI gate:**
  - Dùng cấu hình tương đương **Kịch bản B** (ví dụ: `50 users`, `spawn rate 5/s`, `30s–60s`) làm smoke/load gate trong CI với ngưỡng:
    - `p95 < 100 ms` (hiện tại là `27 ms`, giữ margin an toàn ~3.5x để bắt regression sớm)
    - Real HTTP `5xx` error rate = `0%` (tách biệt với artificial failure nếu có).
- **Giới hạn của phép đo:**
  - **Không thể dùng kết quả này để khẳng định SLO production** vì test đang chạy trên **Flask development server** (Werkzeug) + **SQLite** file cục bộ trên cùng một máy với Locust (shared CPU/RAM, network loopback `127.0.0.1` có RTT ~0 ms).
  - Production cần đo trên WSGI/ASGI server thực (Gunicorn/uWSGI nhiều worker), database thực (PostgreSQL/MySQL) qua mạng thật, và với dữ liệu lớn hơn (hiện bảng `books` chỉ có vài trăm dòng sinh ra trong lúc test).

### 4. Bonus: Nếu connection pool giới hạn ở 5, điều gì xảy ra khi 200 user truy cập đồng thời? Làm thế nào để xác nhận bằng Locust?

- **Điều gì xảy ra:**
  - Khi 200 users cùng gửi request đồng thời (vượt xa kích thước pool = 5), tối đa chỉ 5 request được giữ kết nối DB cùng lúc; 195 request còn lại phải xếp hàng chờ ở `pool.checkout()` (SQLAlchemy mặc định `pool_size=5, max_overflow=10, pool_timeout=30`).
  - Hệ quả:
    1. **Latency (`p95`, `p99`) tăng vọt** theo thời gian chờ hàng đợi thay vì tăng tuyến tính.
    2. **RPS bị bão hòa (saturation / plateau)** tại mức `5 / avg_db_time` dù tăng thêm user.
    3. Nếu thời gian chờ vượt `pool_timeout`, SQLAlchemy ném `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 0 reached`, dẫn đến **HTTP 500 thực tế tăng mạnh**.
- **Cách xác nhận bằng Locust:**
  1. Giảm `wait_time` xuống nhỏ (ví dụ `between(0.1, 0.3)`) hoặc tăng concurrency lên 200 users để tạo áp lực đồng thời thực sự vào DB pool.
  2. Theo dõi biểu đồ **RPS vs Users** và **Response Time (p95/p99)** trên Locust HTML/Web UI: sẽ thấy đường RPS đi ngang (plateau) trong khi p95/p99 dựng đứng.
  3. Kiểm tra bảng **Error report** cuối run: xuất hiện `HTTPError("500 INTERNAL SERVER ERROR")` thật từ server (khác với lỗi giả lập client-side).
