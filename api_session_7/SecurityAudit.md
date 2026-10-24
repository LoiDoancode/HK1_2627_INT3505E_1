# BÁO CÁO ĐÁNH GIÁ AN TOÀN API (SECURITY AUDIT)
**Dự án:** Social Network API — Authentication & Posts Service  
**Phiên bản tài liệu:** 1.0.0  
**Đối tượng đánh giá:** `POST /auth/login`, `POST /auth/refresh`, `GET /posts/{id}`  
**Tiêu chuẩn đối chiếu:** OWASP API Security Top 10 (2023), CWE/SANS Top 25

---

## TỔNG QUAN ĐÁNH GIÁ (EXECUTIVE SUMMARY)

Báo cáo này phân tích các rủi ro bảo mật tiềm ẩn và nguy cơ rò rỉ thông tin (Information Disclosure / Data Leakage) có thể phát sinh trong quá trình thiết kế, đặc tả và triển khai 3 endpoint cốt lõi của mạng xã hội.

Báo cáo xác định **6 điểm có nguy cơ lộ lọt dữ liệu và lỗ hổng an toàn**, kèm theo phân tích chi tiết nguyên nhân, kịch bản tấn công và giải pháp khắc phục triệt để.

---

## CHI TIẾT CÁC ĐIỂM CÓ THỂ LỘ & LỖ HỔNG BẢO MẬT

### 1. Thu thập danh sách người dùng qua phản hồi lỗi (User Enumeration)
- **Mã phân loại:** [CWE-204](https://cwe.mitre.org/data/definitions/204.html) | OWASP API3:2023 (Broken Object Property Level Authorization / Info Disclosure)
- **Mức độ rủi ro:** **High (Cao)**
- **Endpoint ảnh hưởng:** `POST /auth/login`
- **Nguyên nhân gốc rễ:**
  - Backend xử lý logic trả về thông báo lỗi chi tiết khác biệt giữa trường hợp email không tồn tại trong hệ thống và trường hợp mật khẩu sai.
  - Ví dụ phản hồi dễ bị khai thác:
    - Nếu email không có trong DB: `404 Not Found` hoặc `401 Unauthorized` kèm message: *"Email không tồn tại trên hệ thống"*.
    - Nếu email đúng nhưng mật khẩu sai: `401 Unauthorized` kèm message: *"Mật khẩu bạn nhập không đúng"*.
- **Hậu quả & Dữ liệu bị lộ:**
  - Kẻ tấn công sử dụng công cụ tự động quét hàng triệu email thu thập từ các vụ rò rỉ dữ liệu trước đây (Credential Stuffing / Rainbow tables).
  - Phân loại được chính xác email nào đang đăng ký tài khoản trên mạng xã hội này.
  - Từ đó phục vụ các chiến dịch tấn công giả mạo (Targeted Phishing), đe dọa tống tiền hoặc dò vét mật khẩu (Brute-force).
- **Biện pháp khắc phục (Mitigation):**
  - **Chuẩn hóa thông điệp lỗi:** Dù sai email hay sai mật khẩu, luôn trả về cùng mã HTTP `401 Unauthorized` với nội dung chung:
    ```json
    {
      "code": 401,
      "error": "UNAUTHORIZED",
      "message": "Tài khoản hoặc mật khẩu không chính xác"
    }
    ```
  - **Kết hợp Rate Limiting:** Giới hạn tối đa 5 lần thử sai trong vòng 15 phút theo IP và theo định danh tài khoản.

---

### 2. Phân quyền cấp đối tượng bị phá vỡ (BOLA / IDOR) & Đoán ID bài viết riêng tư
- **Mã phân loại:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html) | OWASP API1:2023 (Broken Object Level Authorization - BOLA)
- **Mức độ rủi ro:** **Critical (Nghiêm trọng)**
- **Endpoint ảnh hưởng:** `GET /posts/{id}`
- **Nguyên nhân gốc rễ:**
  - Sử dụng ID dạng số nguyên tự tăng tuần tự (`/posts/1`, `/posts/2`, `/posts/3`,...).
  - Controller chỉ truy vấn `Post.query.get(id)` mà không đối chiếu quyền hạn giữa `current_user` với cờ bảo mật của bài viết (`privacy: PUBLIC / FRIENDS / PRIVATE`).
  - Hoặc khi truy cập bài viết riêng tư mà không có quyền, API trả về `403 Forbidden`. Điều này vô tình xác nhận cho kẻ tấn công biết: **ID bài viết này có thật và tồn tại**.
- **Hậu quả & Dữ liệu bị lộ:**
  - Kẻ tấn công viết script chạy vòng lặp tăng dần ID để cào (scrape) toàn bộ bài viết trên hệ thống.
  - Xem lén các bài viết riêng tư (Chỉ mình tôi), bài viết dành riêng cho bạn bè hoặc bài viết trong các hội nhóm kín.
- **Biện pháp khắc phục (Mitigation):**
  - **Đổi sang định danh ngẫu nhiên:** Sử dụng UUID v4 (`9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d`) hoặc ULID để triệt tiêu tính đoán trước của ID.
  - **Kiểm tra quyền đa lớp (Contextual Authorization):**
    ```python
    post = get_post_by_id(id)
    if not post:
        return abort(404)
    if post.privacy == 'PRIVATE' and post.author_id != current_user.id:
        # Cố tình trả về 404 thay vì 403 để không làm lộ sự tồn tại của ID bí mật
        return abort(404, message="Không tìm thấy bài viết")
    if post.privacy == 'FRIENDS' and not are_friends(post.author_id, current_user.id):
        return abort(404, message="Không tìm thấy bài viết")
    ```

---

### 3. Rò rỉ thông tin định danh nhạy cảm của tác giả (Excessive Data Exposure)
- **Mã phân loại:** [CWE-213](https://cwe.mitre.org/data/definitions/213.html) | OWASP API3:2023 (Broken Object Property Level Authorization)
- **Mức độ rủi ro:** **High (Cao)**
- **Endpoint ảnh hưởng:** `GET /posts/{id}`
- **Nguyên nhân gốc rễ:**
  - Lập trình viên serialize trực tiếp toàn bộ thực thể ORM `Author` (User) đính kèm theo bài viết ra JSON (dùng `user.__dict__` hoặc `SELECT *`).
  - Thiếu lớp DTO (Data Transfer Object) hoặc schema filter định rõ các trường được phép public.
- **Hậu quả & Dữ liệu bị lộ:**
  - Response JSON vô tình chứa: `email`, `phone_number`, `password_hash`, `role`, `is_admin`, `ip_address` lúc đăng bài, `totp_secret`.
  - Kẻ tấn công thu thập được toàn bộ thông tin định danh cá nhân (PII - Personally Identifiable Information) của bất kỳ ai đăng bài.
- **Biện pháp khắc phục (Mitigation):**
  - Trong OpenAPI Spec và mã nguồn, bắt buộc định nghĩa schema `AuthorSummary` chỉ chứa thông tin công khai an toàn:
    ```yaml
    AuthorSummary:
      type: object
      properties:
        id: { type: string, format: uuid }
        username: { type: string }
        display_name: { type: string }
        avatar_url: { type: string, format: uri }
      # Tuyệt đối cấm các trường: email, phone, role, password_hash
    ```

---

### 4. Rò rỉ Token & Nguy cơ chiếm đoạt phiên vĩnh viễn (Token Leakage & Replay Attack)
- **Mã phân loại:** [CWE-287](https://cwe.mitre.org/data/definitions/287.html) | OWASP API2:2023 (Broken Authentication)
- **Mức độ rủi ro:** **Critical (Nghiêm trọng)**
- **Endpoint ảnh hưởng:** `POST /auth/refresh`
- **Nguyên nhân gốc rễ:**
  - Client lưu trữ `refresh_token` tại `localStorage` hoặc `sessionStorage` của trình duyệt, rất dễ bị trích xuất nếu website dính lỗ hổng XSS (Cross-Site Scripting).
  - Phía server cấp `refresh_token` có thời hạn quá dài (hoặc vĩnh viễn) và **không áp dụng cơ chế hủy token cũ** khi cấp mới.
  - Refresh token vô tình bị log lại ở access log của Reverse Proxy (Nginx, Kong) hoặc thông báo lỗi console.
- **Hậu quả & Dữ liệu bị lộ:**
  - Nếu token bị kẻ thứ ba đánh cắp, chúng có thể gọi liên tục `POST /auth/refresh` để duy trì phiên đăng nhập mãi mãi dù người dùng đã đổi thiết bị.
- **Biện pháp khắc phục (Mitigation):**
  - **Lưu trữ an toàn:** Gửi Refresh Token qua `HttpOnly`, `Secure`, `SameSite=Strict` Cookie để JavaScript phía client không thể đọc được.
  - **Refresh Token Rotation (RTR):** Mỗi khi endpoint `/auth/refresh` được gọi thành công:
    1. Vô hiệu hóa ngay lập tức `refresh_token` cũ.
    2. Cấp một cặp `access_token` và `refresh_token` hoàn toàn mới.
  - **Phát hiện tái sử dụng Token (Token Reuse Detection):** Nếu hệ thống nhận được một `refresh_token` đã từng bị thu hồi, hệ thống coi đây là dấu hiệu phiên làm việc đã bị xâm phạm $\rightarrow$ Lập tức thu hồi toàn bộ token family (hủy luôn tất cả session hiện hành của user đó) và buộc đăng nhập lại.

---

### 5. Dò quét email qua độ lệch thời gian phản hồi (Timing Attack)
- **Mã phân loại:** [CWE-208](https://cwe.mitre.org/data/definitions/208.html) | Information Exposure Through Timing Discrepancy
- **Mức độ rủi ro:** **Medium (Trung bình)**
- **Endpoint ảnh hưởng:** `POST /auth/login`
- **Nguyên nhân gốc rễ:**
  - Thuật toán băm mật khẩu (Bcrypt, Argon2, PBKDF2) được thiết kế cố tình chạy chậm và tiêu tốn CPU (mất khoảng $100 - 300\text{ms}$) để chống brute-force.
  - Khi người dùng gửi request đăng nhập:
    - Trường hợp 1: Email không có trong DB $\rightarrow$ Trả về lỗi ngay lập tức ($\approx 5 - 10\text{ms}$).
    - Trường hợp 2: Email có trong DB, nhưng mật khẩu sai $\rightarrow$ Chạy hàm `bcrypt.check_password_hash()` $\rightarrow$ Trả về lỗi sau $\approx 200\text{ms}$.
- **Hậu quả & Dữ liệu bị lộ:**
  - Dù thông báo lỗi trả về giống hệt nhau (`401 Unauthorized`), kẻ tấn công chỉ cần đo thời gian phản hồi (Round Trip Time / Server Latency) là có thể xác định 100% email đó đã đăng ký tài khoản hay chưa.
- **Biện pháp khắc phục (Mitigation):**
  - Sử dụng kỹ thuật băm mật khẩu giả định (Dummy Hash Verification) trong trường hợp không tìm thấy email, để thời gian thực thi của cả hai trường hợp luôn xấp xỉ ngang nhau:
    ```python
    DUMMY_HASH = "$2b$12$e8k..."  # Hash bcrypt mẫu
    user = db.find_user(email)
    if not user:
        # Chạy hàm băm giả lập để giữ thời gian phản hồi đồng đều
        bcrypt.check_password_hash(DUMMY_HASH, password)
        return abort(401, "Tài khoản hoặc mật khẩu không chính xác")
    if not bcrypt.check_password_hash(user.password_hash, password):
        return abort(401, "Tài khoản hoặc mật khẩu không chính xác")
    ```

---

### 6. Rò rỉ thông tin kiến trúc nội bộ qua lỗi hệ thống (Verbose Error / Stack Trace)
- **Mã phân loại:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html) | OWASP API8:2023 (Security Misconfiguration)
- **Mức độ rủi ro:** **Medium (Trung bình)**
- **Endpoint ảnh hưởng:** Toàn bộ 3 endpoint khi trả về mã `500 Internal Server Error`
- **Nguyên nhân gốc rễ:**
  - Server bật chế độ `DEBUG = True` trên môi trường production, hoặc không bắt ngoại lệ toàn cục (`try...catch` / `@app.errorhandler(500)`).
  - Khi cơ sở dữ liệu bị ngắt kết nối hoặc gặp lỗi cú pháp SQL/ORM, framework tự động dump toàn bộ traceback HTML/JSON trả về cho client.
- **Hậu quả & Dữ liệu bị lộ:**
  - Lộ phiên bản hệ điều hành, đường dẫn file source code trên máy chủ (ví dụ: `C:/game/HK1_Nam3_2026/.../app.py`), phiên bản Flask/SQLAlchemy, tên bảng và tên cột cơ sở dữ liệu.
  - Kẻ tấn công tận dụng các phiên bản này để tra cứu lỗ hổng 1-day/CVE đã công bố nhằm khai thác sâu hơn vào máy chủ.
- **Biện pháp khắc phục (Mitigation):**
  - Tắt toàn bộ chế độ Debug trên Production.
  - Chuẩn hóa cấu trúc lỗi theo RFC 7807 (Problem Details).
  - Chỉ ghi nhận chi tiết lỗi vào log nội bộ (kèm `trace_id`), client chỉ nhận mã lỗi chung kèm `trace_id` để liên hệ hỗ trợ:
    ```json
    {
      "code": 500,
      "error": "INTERNAL_SERVER_ERROR",
      "message": "Hệ thống đang gặp sự cố nội bộ. Vui lòng thử lại sau.",
      "timestamp": "2026-10-24T08:45:00Z",
      "trace_id": "req-500-d8721c4b"
    }
    ```

---

## BẢNG TỔNG HỢP KIỂM TRA ĐỐI CHIẾU (SECURITY CHECKLIST)

| STT | Điểm rủi ro lộ lọt | Endpoint liên quan | Mức độ | Trạng thái giải pháp trong OpenAPI Spec |
| :---: | :--- | :--- | :---: | :---: |
| 1 | **User Enumeration** | `POST /auth/login` | High | Đã chuẩn hóa mã `401` với thông báo chung đồng nhất |
| 2 | **BOLA / IDOR** | `GET /posts/{id}` | Critical | Sử dụng `UUID v4`, trả về `404` thay vì `403` với bài riêng tư |
| 3 | **Excessive Data Exposure** | `GET /posts/{id}` | High | Tạo schema `AuthorSummary` loại bỏ hoàn toàn email, phone, hash |
| 4 | **Token Leakage & Replay** | `POST /auth/refresh` | Critical | Quy định Refresh Token Rotation (RTR) và xử lý Token Reuse |
| 5 | **Timing Attacks** | `POST /auth/login` | Medium | Đề xuất giải pháp Dummy Hash Verification cân bằng thời gian |
| 6 | **Verbose Stack Trace** | Tất cả endpoint (500) | Medium | Chuẩn hóa schema `ErrorResponse` kèm `trace_id`, ẩn chi tiết nhạy cảm |
| 7 | **Thiếu Rate Limiting** | `/auth/login`, `/posts/{id}` | High | Đặc tả mã `429 Too Many Requests` và header `Retry-After` |

---
*Báo cáo được chuẩn bị phục vụ nộp bài tập môn Kiến trúc hướng dịch vụ (SOA).*
