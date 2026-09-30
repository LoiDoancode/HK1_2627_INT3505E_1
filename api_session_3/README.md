# Thiết kế resource cho Blog API

## BÀI TOÁN
**Nền tảng blog đơn giản**
Một blog cho phép người dùng đăng **bài viết (posts)**, mỗi bài có **bình luận (comments)** và gắn **thẻ (tags)**. Mỗi user có **hồ sơ** và đăng ký **theo dõi (follow)** tác giả khác. Hãy thiết kế cấu trúc endpoint đầy đủ.

## THIẾT KẾ

### 1. Xác định **resources** trong miền
Dựa trên bài toán, ta có thể xác định các đối tượng (resources) chính:
- `users`: Thông tin tài khoản người dùng.
- `profiles`: Hồ sơ cá nhân của người dùng.
- `posts`: Bài viết trên blog.
- `comments`: Các bình luận trên bài viết.
- `tags`: Thẻ phân loại bài viết.

### 2. Phân loại collection / item / sub-resource
- **Collection**: Tập hợp nhiều đối tượng cùng loại. Ví dụ: `/users`, `/posts`, `/tags`.
- **Item**: Một đối tượng cụ thể trong Collection (xác định bằng ID). Ví dụ: `/users/{user_id}`, `/posts/{post_id}`.
- **Sub-resource**: Đối tượng phụ thuộc vào một Item. Ví dụ:
  - Hồ sơ của user: `/users/{user_id}/profile`
  - Những người user đang theo dõi: `/users/{user_id}/following`
  - Những người theo dõi user: `/users/{user_id}/followers`
  - Các bình luận của bài viết: `/posts/{post_id}/comments`
  - Các thẻ của bài viết: `/posts/{post_id}/tags`

### 3. Vẽ sơ đồ cây endpoint và quyết định version segment
Chúng ta sẽ sử dụng prefix version: `/api/v1`

**Sơ đồ Endpoint:**
```text
/api/v1
├── /users
│   ├── POST: Tạo user mới
│   ├── GET: Lấy danh sách users
│   └── /{user_id}
│       ├── GET: Lấy thông tin user
│       ├── PUT/PATCH: Cập nhật thông tin user
│       ├── DELETE: Xóa user
│       ├── /profile
│       │   ├── GET: Lấy hồ sơ user
│       │   └── PUT: Cập nhật hồ sơ user
│       ├── /followers
│       │   └── GET: Lấy danh sách người theo dõi user này
│       └── /following
│           ├── GET: Lấy danh sách những người user này đang theo dõi
│           ├── POST: Bắt đầu theo dõi một user khác (truyền ID qua body)
│           └── DELETE: Hủy theo dõi một user khác
├── /posts
│   ├── POST: Đăng bài viết mới
│   ├── GET: Lấy danh sách bài viết
│   └── /{post_id}
│       ├── GET: Lấy chi tiết bài viết
│       ├── PUT/PATCH: Cập nhật bài viết
│       ├── DELETE: Xóa bài viết
│       ├── /comments
│       │   ├── POST: Thêm bình luận vào bài viết
│       │   └── GET: Lấy danh sách bình luận của bài viết
│       └── /tags
│           ├── POST: Gắn thẻ cho bài viết
│           ├── GET: Lấy danh sách thẻ của bài viết
│           └── DELETE /{tag_id}: Gỡ thẻ khỏi bài viết
└── /tags
    ├── POST: Tạo thẻ mới
    ├── GET: Lấy danh sách các thẻ
    └── /{tag_id}
        └── GET: Xem chi tiết thẻ
```

