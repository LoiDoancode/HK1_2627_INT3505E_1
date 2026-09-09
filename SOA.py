import requests

# 1. Gửi yêu cầu GET (Ví dụ lấy thông tin từ một API có sẵn)
response_get = requests.get('https://jsonplaceholder.typicode.com/posts/1')

if response_get.status_code == 200:
    print("Dữ liệu GET nhận được:")
    print(response_get.json()) # In ra dữ liệu dạng JSON
else:
    print(f"Lỗi GET: {response_get.status_code}")


# 2. Gửi yêu cầu POST (Ví dụ gửi dữ liệu tạo mới lên server)
data_to_send = {
    "title": "foo",
    "body": "bar",
    "userId": 1
}
response_post = requests.post('https://jsonplaceholder.typicode.com/posts', json=data_to_send)

if response_post.status_code == 201: # 201 thường là mã thành công khi tạo mới
    print("\nDữ liệu POST thành công, server trả về:")
    print(response_post.json())
else:
    print(f"Lỗi POST: {response_post.status_code}")
