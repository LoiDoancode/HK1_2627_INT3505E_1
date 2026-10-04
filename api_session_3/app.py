import base64, json
from flask import Flask, request, jsonify
from error import ApiProblem, register_error_handlers

app = Flask(__name__)
#BAI1
# POST = [
#     {'id': 1, 'title': 'Post 1', 'content': 'Content 1', 'author': 'Loi', 'tag': ['tech', 'flask']},
#     {'id': 2, 'title': 'Post 2', 'content': 'Content 2', 'author': 'LoiD', 'tag': ['python']},
#     {'id': 3, 'title': 'Post 3', 'content': 'Content 3', 'author': 'LoiDD', 'tag': ['web']}
# ]
# _next_post_id = 4

# COMMENTS = [
#     {'id': 1, 'post_id': 1, 'author': 'Loi', 'content': 'Bài viết rất hay!'},
#     {'id': 2, 'post_id': 1, 'author': 'LoiD', 'content': 'Cảm ơn đã chia sẻ.'}
# ]
# _next_comment_id = 3

# USERS = [
#     {'username': 'Loi', 'name': 'Loi Doan', 'bio': 'Flask Developer'},
#     {'username': 'oli', 'name': 'oli Doan', 'bio': 'Tech Enthusiast'},
#     {'username': 'iol', 'name': 'iol Doan', 'bio': 'Reader'}
# ]

# FOLLOWS = {
#     'oli': ['Loi'],
#     'iol': ['Loi', 'oli']
# }

# @app.get('/api/v1/posts')
# def list_posts():
#     try:
#         page = max(int(request.args.get('page', 1)), 1)
#         size = max(min(int(request.args.get('size', 10)), 36), 1)
#     except ValueError:
#         return jsonify({'error': 'page and size must be integers'}), 400
    
#     tag = request.args.get('tag', '')
#     q = request.args.get('q', '')
#     filtered = POST
    
#     if tag:
#         filtered = [p for p in filtered if tag.lower() in [t.lower() for t in p.get('tag', [])]]
#     if q:
#         filtered = [p for p in filtered if q.lower() in p['title'].lower() or q.lower() in p['content'].lower() or q.lower() in p['author'].lower()]
    
#     total = len(filtered)
#     start = (page - 1) * size
#     end = start + size
#     items = filtered[start:end]
#     total_pages = (total + size - 1) // size if total > 0 else 1

#     def build_url(p):
#         return f"/api/v1/posts?page={p}&size={size}"
    
#     links = {
#         'self': {'href': build_url(page)},
#         'first': {'href': build_url(1)},
#         'last': {'href': build_url(total_pages)}
#     }
#     if page > 1:
#         links['prev'] = {'href': build_url(page - 1)}
#     if page < total_pages:
#         links['next'] = {'href': build_url(page + 1)}

#     return jsonify({
#         'items': items,
#         'pagination': {
#             'page': page,
#             'size': size,
#             'total': total,
#             'total_pages': total_pages
#         },
#         '_links': links
#     }), 200

# @app.post('/api/v1/posts')
# def create_post():
#     global _next_post_id
#     data = request.get_json()
#     if not data or 'title' not in data or 'content' not in data or 'author' not in data:
#         return jsonify({'error': 'title, content, and author are required'}), 400
#     new_post = {
#         'id': _next_post_id,
#         'title': data['title'],
#         'content': data['content'],
#         'author': data['author'],
#         'tag': data.get('tag', [])
#     }
#     POST.append(new_post)
#     _next_post_id += 1
#     return jsonify(new_post), 201

# @app.get('/api/v1/posts/<int:post_id>')
# def get_post(post_id):
#     post = next((p for p in POST if p['id'] == post_id), None)
#     if not post:
#         return jsonify({'error': 'post not found'}), 404
#     return jsonify(post), 200

# @app.put('/api/v1/posts/<int:post_id>')
# def update_post(post_id):
#     post = next((p for p in POST if p['id'] == post_id), None)
#     if not post:
#         return jsonify({'error': 'post not found'}), 404
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'Invalid data'}), 400
#     post['title'] = data.get('title', post['title'])
#     post['author'] = data.get('author', post['author'])
#     post['content'] = data.get('content', post['content'])
#     post['tag'] = data.get('tag', post['tag'])
#     return jsonify(post), 200

# @app.delete('/api/v1/posts/<int:post_id>')
# def delete_post(post_id):
#     post = next((p for p in POST if p['id'] == post_id), None)
#     if not post:
#         return jsonify({'error': 'post not found'}), 404
#     POST.remove(post)
#     return '', 204

# @app.get('/api/v1/posts/<int:post_id>/comments')
# def get_comments(post_id):
#     post = next((p for p in POST if p['id'] == post_id), None)
#     if not post:
#         return jsonify({'error': 'post not found'}), 404
    
#     post_comments = [c for c in COMMENTS if c['post_id'] == post_id]
#     return jsonify({'items': post_comments, 'total': len(post_comments)}), 200

# @app.post('/api/v1/posts/<int:post_id>/comments')
# def create_comment(post_id):
#     global _next_comment_id
#     post = next((p for p in POST if p['id'] == post_id), None)
#     if not post:
#         return jsonify({'error': 'post not found'}), 404
    
#     data = request.get_json()
#     if not data or 'content' not in data or 'author' not in data:
#         return jsonify({'error': 'author and content are required'}), 400
    
#     new_comment = {
#         'id': _next_comment_id,
#         'post_id': post_id,
#         'author': data['author'],
#         'content': data['content']
#     }
#     COMMENTS.append(new_comment)
#     _next_comment_id += 1
#     return jsonify(new_comment), 201

# @app.delete('/api/v1/posts/<int:post_id>/comments/<int:comment_id>')
# def delete_comment(post_id, comment_id):
#     """Xóa bình luận"""
#     comment = next((c for c in COMMENTS if c['id'] == comment_id and c['post_id'] == post_id), None)
#     if not comment:
#         return jsonify({'error': 'comment not found'}), 404
#     COMMENTS.remove(comment)
#     return '', 204
#BAI2
# register_error_handlers(app)
# class User:
#     @staticmethod
#     def query_get(user_id):
#         if user_id == 42:
#             return User(42, "Loi")
#     def __init__(self, id, name):
#         self.id = id
#         self.name = name
#     def to_dict(self):
#         return {"id": self.id, "name": self.name}
# @app.get("/users/<int:id>")
# def get_user(id):
#     user = User.query_get(id)
#     if not user:
#         raise ApiProblem(
#             status = 404,
#             title = "user not found",
#             type_path = "user-not-found",
#             resource_id = id
#         )
#     return jsonify(user.to_dict()), 200

#BAI3
DATA = [
    {
        "id": 1,
        "customer_id": "A",
        "status": "paid",
        "total": 150.0
    },
    {
        "id": 2,
        "customer_id": "B",
        "status": "pending",
        "total": 250.0
    },
    {
        "id": 3,
        "customer_id": "A",
        "status": "cancelled",
        "total": 350.0
    }
]

def encode_cursor(last_id):
    cursor_str = json.dumps({'last_id': last_id})
    return base64.b64encode(cursor_str.encode('utf-8')).decode('utf-8')

def decode_cursor(cursor_param):
    try:
        decoded_bytes = base64.b64decode(cursor_param.encode('utf-8'))
        data = json.loads(decoded_bytes.decode('utf-8'))
        if 'last_id' not in data:
            raise ValueError('Missing last_id')
        return data['last_id']
    except Exception:
        return None

@app.route('/orders', methods=['GET'])
def get_orders():
    cursor_param = request.args.get('cursor')
    limit = request.args.get('limit', default=10, type=int)
    status_filter = request.args.get('status')
    customer_filter = request.args.get('customer_id')
    sort_param = request.args.get('sort', default='id')
    fields_param = request.args.get('fields')
    results = DATA.copy()
    last_id = None
    if cursor_param:
        last_id = decode_cursor(cursor_param)
        if last_id is None:
            return (
                jsonify(
                    {
                        'error': 'Bad Request',
                        'message': 'cursor khong hop le hoac bi loi'
                    }
                ), 400
            )
    if status_filter:
        results = [item for item in results if item['status'] == status_filter]
    if customer_filter:
        results = [item for item in results if item['customer_id'] == customer_filter]
    reverse = False
    sort_field = sort_param
    if sort_param.startswith('-'):
        reverse = True
        sort_field = sort_param[1:]
    if results and sort_field in results[0]:
        results.sort(key=lambda x: x[sort_field], reverse=reverse)
    if last_id is not None:
        start_index = 0
        for i, item in enumerate(results):
            if item['id'] == last_id:
                start_index = i + 1
                break
        results = results[start_index:]
    paginated_results = results[:limit]
    next_cursor = None
    if len(results) > limit:
        last_item_id = paginated_results[-1]['id']
        next_cursor = encode_cursor(last_item_id)
    if fields_param:
        requested_fields = [f.strip() for f in fields_param.split(',')]
        final_results = []
        for item in paginated_results:
            filtered_item = {
                k: v for k,v in item.items() if k in requested_fields
            }
            final_results.append(filtered_item)
    else:
        final_results = paginated_results
    return jsonify(
        {
            'data': final_results,
            'pagination': {'limit': limit, 'next_cursor': next_cursor}
        }
    )
        

if __name__ == '__main__':
    app.run(debug=True, port=5000)