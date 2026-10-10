# Thiết Kế Kiến Trúc RESTful API Cho Nền Tảng Blog

## 1. Bài Toán (Domain Requirements)
Thiết kế hệ thống API cho nền tảng Blog đơn giản hỗ trợ các tính năng:
- Quản lý tài khoản người dùng, hồ sơ cá nhân và tính năng **Follow / Unfollow** tác giả khác.
- Quản lý **Bài viết (Posts)** bao gồm tạo, đọc, sửa, xóa bài viết.
- Quản lý **Bình luận (Comments)** trên từng bài viết.
- Gắn và quản lý **Thẻ (Tags)** phân loại cho bài viết.

---

## 2. Xác Định Resources & Phân Loại
Hệ thống xác định 5 tài nguyên (resources) chính:
- `users`: Tài khoản người dùng trong hệ thống.
- `profiles`: Hồ sơ cá nhân của người dùng.
- `posts`: Bài viết đăng trên blog.
- `comments`: Các bình luận thuộc bài viết.
- `tags`: Thẻ phân loại bài viết.

### Phân loại Cấu trúc Resource:
- **Collection**: `/users`, `/posts`, `/tags`
- **Item**: `/users/{user_id}`, `/posts/{post_id}`, `/tags/{tag_id}`
- **Sub-resource**:
  - Hồ sơ user: `/users/{user_id}/profile`
  - Người theo dõi: `/users/{user_id}/followers`
  - Đang theo dõi: `/users/{user_id}/following`
  - Bình luận bài viết: `/posts/{post_id}/comments`
  - Thẻ của bài viết: `/posts/{post_id}/tags`

---

## 3. Versioning & Cấu Trúc Endpoint

Hệ thống sử dụng Prefix Versioning: `/api/v1`

```text
/api/v1
├── /users
│   ├── GET                          : Lấy danh sách người dùng (có phân trang)
│   ├── POST                         : Đăng ký tài khoản mới
│   └── /{user_id}
│       ├── GET                      : Lấy thông tin chi tiết người dùng
│       ├── PUT / PATCH              : Cập nhật thông tin người dùng
│       ├── DELETE                   : Xóa tài khoản
│       ├── /profile
│       │   ├── GET                  : Xem hồ sơ cá nhân
│       │   └── PUT / PATCH          : Cập nhật hồ sơ cá nhân
│       ├── /followers
│       │   └── GET                  : Lấy danh sách người theo dõi (followers)
│       └── /following
│           ├── GET                  : Lấy danh sách những người đang theo dõi
│           ├── POST                 : Bắt đầu theo dõi một tác giả khác
│           └── /{target_user_id}
│               └── DELETE           : Hủy theo dõi (Unfollow)
│
├── /posts
│   ├── GET                          : Lấy danh sách bài viết (phân trang, lọc theo tag, tìm kiếm q)
│   ├── POST                         : Đăng bài viết mới
│   └── /{post_id}
│       ├── GET                      : Xem chi tiết bài viết
│       ├── PUT / PATCH              : Cập nhật nội dung bài viết
│       ├── DELETE                   : Xóa bài viết
│       ├── /comments
│       │   ├── GET                  : Lấy danh sách bình luận của bài viết
│       │   ├── POST                 : Thêm bình luận vào bài viết
│       │   └── /{comment_id}
│       │       ├── PUT / PATCH      : Cập nhật bình luận
│       │       └── DELETE           : Xóa bình luận
│       └── /tags
│           ├── GET                  : Lấy danh sách thẻ của bài viết
│           ├── POST                 : Gắn thẻ cho bài viết
│           └── /{tag_id}
│               └── DELETE           : Gỡ thẻ khỏi bài viết
│
└── /tags
    ├── GET                          : Lấy danh sách tất cả các thẻ
    ├── POST                         : Tạo thẻ mới
    └── /{tag_id}
        ├── GET                      : Lấy thông tin chi tiết của thẻ
        ├── PUT / PATCH              : Cập nhật tên/thông tin thẻ
        └── DELETE                   : Xóa thẻ