# Những Đánh Đổi Trong Thiết Kế OpenAPI Specification

## 1. Cân bằng giữa Tính tái sử dụng (DRY) và Tính minh bạch qua `$ref`

Quyết định khó khăn đầu tiên là xác định mức độ trừu tượng hóa các cấu trúc dữ liệu. OpenAPI cho phép sử dụng từ khóa `$ref` để trỏ tới các object được định nghĩa sẵn trong phần `components/schemas`.

* **Trừu tượng hóa cao (Max DRY):**  
  Mọi trường dữ liệu lặp lại (như `ErrorResponse`, `PaginationMeta`, `UserAddress`) đều được tách ra thành các component riêng. Điều này giúp dễ bảo trì (cập nhật một nơi, áp dụng toàn bộ), nhưng biến file OpenAPI thành một mạng nhện tham chiếu chéo. Các lập trình viên khi đọc spec phải liên tục nhảy qua lại giữa các file hoặc dòng code để hiểu cấu trúc thực tế của một payload.

* **Trình bày phẳng (Flat / Inline):**  
  Định nghĩa trực tiếp schema ngay tại endpoint. Cách này thân thiện với con người khi đọc lướt, nhưng tạo ra sự trùng lặp dữ liệu khổng lồ và nguy cơ bất đồng bộ khi API phát triển.

* **Điểm quyết định:**  
  Đội ngũ thiết kế phải quyết định "điểm dừng" của việc chia nhỏ component. Thông thường, một cấu trúc dữ liệu nếu được sử dụng lại từ 3 endpoint trở lên mới nên đưa vào `components`, nhưng ranh giới này rất mong manh và thường xuyên bị phá vỡ.

---

## 2. Đa hình (Polymorphism) đối đầu với Khả năng sinh mã (Code Generation)

OpenAPI hỗ trợ mô hình hóa dữ liệu phức tạp thông qua các từ khóa cấu trúc đa hình: `oneOf`, `anyOf`, và `allOf`, kết hợp với `discriminator`. Tuy nhiên, quyết định sử dụng chúng hay không lại là một bài toán đánh đổi lớn.

* **Thiết kế chuẩn (Theo đúng chuẩn OpenAPI):**  
  Sử dụng `oneOf` để mô tả một endpoint có thể trả về hoặc nhận vào nhiều loại payload khác nhau (ví dụ: một mảng `Event` chứa cả `UserCreatedEvent` và `OrderShippedEvent`). Xét về mặt đặc tả, đây là cách thiết kế chính xác và thanh lịch nhất.

* **Thực tế sinh mã (Code Generation):**  
  Đa số các công cụ sinh mã tự động (như OpenAPI Generator, Swagger Codegen) cho các ngôn ngữ định kiểu tĩnh (Java, C#, Go) xử lý `oneOf` và `anyOf` rất kém. Chúng thường sinh ra các class lộn xộn, mất type-safety, hoặc dùng kiểu dữ liệu cơ bản (như `Object` hoặc `Map`) khiến mất đi giá trị của việc dùng OpenAPI.

* **Điểm quyết định:**  
  Người thiết kế API phải chọn giữa việc:
  * Viết một bản spec **"hoàn hảo, đúng chuẩn"** (nhưng phá hỏng SDK tự động sinh ra cho client).
  * **HOẶC** thiết kế **"hạ cấp"** bằng cách nhồi nhét tất cả các trường có thể có vào một schema duy nhất và đánh dấu chúng là tùy chọn (`optional`) để đảm bảo client code chạy ổn định. định.