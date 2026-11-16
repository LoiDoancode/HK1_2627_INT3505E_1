# Buổi 8 / Session 10 — API Testing và Quality Assurance

Thư mục này chứa bài làm hoàn chỉnh cho các bài Lab (Lab 1 – Lab 4) trong [`lab08-starter/`](./lab08-starter).

## 1. Yêu cầu môi trường & Cài đặt

- **Python**: 3.11+
- **Node.js**: 18+ (để chạy Spectral và Newman CLI)

Di chuyển vào thư mục project và cài đặt thư viện:

```powershell
cd lab08-starter
python -m pip install -r requirements.txt
npm install -g @stoplight/spectral-cli newman
```

---

## 2. Khởi chạy Books API Server (dùng cho Lab 3 & Lab 4)

Trong **Terminal 1**, tạo thư mục `instance` (nếu chưa có) để SQLite lưu database `instance/books.db`, sau đó chạy Flask server tại `http://127.0.0.1:5000`:

```powershell
cd lab08-starter
New-Item -ItemType Directory -Force -Path instance | Out-Null
python -m app --port 5000
```

> Trên Linux/macOS: `mkdir -p instance && python -m app --port 5000`

---

## 3. Cách chạy từng Lab và kết quả thực tế

### Lab 1 — Test Books API với `pytest` & `jsonschema`

- **File chính:** `tests/conftest.py`, `tests/test_smoke.py`, `tests/test_lab01.py`, `pytest.ini`
- **Cách chạy:**
  ```powershell
  cd lab08-starter
  python -m pytest -v
  ```
- **Kết quả thực tế:**
  - `7 passed in 1.75s` (gồm 2 smoke tests + 4 test bắt buộc + 1 bonus test `test_response_extra_field_blocked` dùng `jsonschema`, không in stack trace, thời gian < 2 giây).

---

### Lab 2 — Lint OpenAPI Spec với Spectral

- **File chính:** `openapi.yaml`, `.spectral.yml`
- **Nội dung đã sửa:**
  1. Bổ sung `operationId` cho `GET /books`.
  2. Xóa response body (`content`) trên `DELETE /books/{id}` (HTTP `204`).
  3. Sửa `Book.year` thành `type: integer`.
  4. Bổ sung custom rule trong `.spectral.yml` kiểm tra schema của response `200` phải có nhiều hơn 0 trường (`minProperties: 1`).
- **Cách chạy:**
  ```powershell
  cd lab08-starter
  spectral lint openapi.yaml --ruleset .spectral.yml
  ```
- **Kết quả thực tế:**
  - Không còn lỗi nào (`0 problems`, xem ảnh minh họa trong `lab08-starter/img/run_spectral.png`).

---

### Lab 3 — Automated API Test Suite với Postman & Newman

- **File chính:** `books-api.postman_collection.json`, `postman/books-api.postman_collection.json`, `postman/local.postman_environment.json`, `run_newman.ps1`, `run_newman.sh`
- **Nội dung đã làm:**
  - Folder `books/`: 5 happy-path requests (`GET /books`, `POST /books`, `GET /books/{id}`, `PUT /books/{id}`, `DELETE /books/{id}`), lưu `book_id` vào `collectionVariables`.
  - Folder `error-cases/`: thêm `POST /books — missing title` (kiểm tra `400` + `VALIDATION_ERROR` + field `title`) và `GET /books/9999 — not found` (kiểm tra `404` + `NOT_FOUND`).
- **Cách chạy (khi Flask server đang chạy ở Terminal 1):**
  ```powershell
  cd lab08-starter
  .\run_newman.ps1
  ```
  Hoặc chạy trực tiếp bằng lệnh:
  ```powershell
  newman run books-api.postman_collection.json `
    -e postman/local.postman_environment.json `
    -r "cli,junit" `
    --reporter-junit-export reports/junit.xml
  ```
- **Kết quả thực tế:**
  - `7/7` requests pass, `14/14` assertions pass, `0` failed, tổng thời gian chạy **657 ms** (`< 10s`).
  - File báo cáo JUnit được xuất tại `lab08-starter/reports/junit.xml`.

---

### Lab 4 — Load Test Books API với Locust

- **File chính:** `performance/locustfile.py`, `performance/analysis.md`
- **Nội dung đã làm:**
  - Bổ sung task `search_by_year` (`GET /books?year={year}`) với 1% client-side failure injection (`response.failure(...)`) và phân biệt rõ với lỗi HTTP 500 từ server.
  - Chạy đủ 3 kịch bản từ Terminal 2 (khi Flask server đang chạy ở Terminal 1):
    ```powershell
    cd lab08-starter

    # Kịch bản A — Baseline (10 users, spawn rate 2/s, 30s)
    python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 10 -r 2 -t 30s --html reports/A.html --csv reports/A

    # Kịch bản B — Load test (50 users, spawn rate 5/s, 60s)
    python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 50 -r 5 -t 60s --html reports/B.html --csv reports/B

    # Kịch bản C — Spike test (200 users, spawn rate 50/s, 30s)
    python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 200 -r 50 -t 30s --html reports/C.html --csv reports/C
    ```
- **Kết quả thực tế:**

  | Kịch bản | Users | Spawn rate | Duration | Tổng reqs | p95 (ms) | Failure rate | RPS | Báo cáo |
  |---|---:|---:|---:|---:|---:|---:|---:|---|
  | A (Baseline) | 10 | 2/s | 30s | 125 | 24 | 0.00% | 4.78 | `reports/A.html` |
  | B (Load test) | 50 | 5/s | 60s | 1396 | 27 | 0.36% | 23.54 | `reports/B.html` |
  | C (Spike test) | 200 | 50/s | 30s | 2851 | 130 | 0.35% | 96.63 | `reports/C.html` |

- **Phân tích chi tiết:** Xem toàn bộ phần trả lời 4 câu hỏi (bao gồm câu bonus về connection pool) tại [`lab08-starter/performance/analysis.md`](./lab08-starter/performance/analysis.md).
