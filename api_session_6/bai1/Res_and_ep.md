# Resource Set & Endpoints

Resource Set trong hệ thống đặt phòng khách sạn gồm có 7 resources chính, được phân loại rõ ràng theo cấp độ truy cập.
## Chi tiết các Resources
### 1. `hotels` (Top-level Resource)
- **URI Design:**
  - **Collection URI:** `/hotels`
  - **Single-item URI:** `/hotels/{hotel_id}`

### 2. `room-types` (Sub-resource của Hotel)
- **URI Design:**
  - **Nested URI:** `/hotels/{hotel_id}/room-types`

### 3. `customers` (Top-level Resource)
- **URI Design:**
  - **Single-item URI:** `/customers/{customer_id}`

### 4. `bookings` (Top-level Resource với Filter)
- **URI Design:**
  - **Collection URI:** `/bookings`
  - **Single-item URI:** `/bookings/{booking_id}`
  - **Query Parameters hỗ trợ:** `?customer_id={customer_id}`, `?hotel_id={hotel_id}`

### 5. `payment` (Sub-resource 1:1 của Booking)
- **URI Design:**
  - **Nested URI:** `/bookings/{booking_id}/payment`

### 6. `rooms` (Sub-resource của Hotel)
- **URI Design:**
  - **Nested URI:** `/hotels/{hotel_id}/rooms`
  - **Single-item URI:** `/hotels/{hotel_id}/rooms/{room_id}`
  - **Query Parameters hỗ trợ:** `?room_type_id={room_type_id}`

### 7. `booking-items` (Sub-resource của Booking)
- **URI Design:**
  - **Nested URI:** `/bookings/{booking_id}/items`
  - **Single-item URI:** `/bookings/{booking_id}/items/{item_id}`

---

## Danh sách URL Endpoints (19 Endpoints)

Dưới đây là danh sách 19 URL endpoints chuẩn RESTful được ánh xạ trực tiếp từ các thực thể và quan hệ trong sơ đồ ERD:

| STT | HTTP Method | Endpoint URI | Mô tả nghiệp vụ |
| :---: | :--- | :--- | :--- |
| **1** | `GET` | `/hotels` | Lấy danh sách tất cả các khách sạn |
| **2** | `POST` | `/hotels` | Tạo/thêm một khách sạn mới |
| **3** | `GET` | `/hotels/{hotel_id}` | Lấy thông tin chi tiết một khách sạn theo `hotel_id` |
| **4** | `PUT` | `/hotels/{hotel_id}` | Cập nhật thông tin khách sạn |
| **5** | `GET` | `/hotels/{hotel_id}/room-types` | Lấy danh sách các hạng phòng thuộc một khách sạn |
| **6** | `POST` | `/hotels/{hotel_id}/room-types` | Thêm hạng phòng mới cho khách sạn |
| **7** | `GET` | `/hotels/{hotel_id}/room-types/{room_type_id}` | Lấy chi tiết thông tin một hạng phòng |
| **8** | `GET` | `/hotels/{hotel_id}/rooms` | Lấy danh sách các phòng vật lý (hỗ trợ filter `?room_type_id=...`) |
| **9** | `POST` | `/hotels/{hotel_id}/rooms` | Thêm mới một phòng vật lý vào khách sạn |
| **10** | `GET` | `/hotels/{hotel_id}/rooms/{room_id}` | Lấy thông tin chi tiết một phòng vật lý theo `room_id` |
| **11** | `POST` | `/customers` | Đăng ký/tạo mới hồ sơ khách hàng (`cus_id`, `name`) |
| **12** | `GET` | `/customers/{customer_id}` | Lấy thông tin chi tiết của một khách hàng |
| **13** | `GET` | `/bookings` | Lấy danh sách đơn đặt phòng (Filter: `?customer_id=...&hotel_id=...`) |
| **14** | `POST` | `/bookings` | Tạo mới một đơn đặt phòng (`booking_id`, `cus_id`, `hotel_id`) |
| **15** | `GET` | `/bookings/{booking_id}` | Lấy thông tin chi tiết một đơn đặt phòng |
| **16** | `GET` | `/bookings/{booking_id}/items` | Lấy danh sách các mục/hạng phòng đặt trong đơn |
| **17** | `POST` | `/bookings/{booking_id}/items` | Thêm mục đặt phòng (`item_id`, `room_type_id`) vào đơn |
| **18** | `GET` | `/bookings/{booking_id}/payment` | Lấy thông tin thanh toán của đơn đặt phòng |
| **19** | `POST` | `/bookings/{booking_id}/payment` | Khởi tạo/ghi nhận thanh toán (`payment_id`, `total_payment`) |

