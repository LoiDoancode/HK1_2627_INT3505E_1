from flask import Flask, request, jsonify

app = Flask(__name__)

POST = [
    {'id': 1, 'title': 'Post 1', 'content': 'Content 1', 'author': 'Loi', 'tag': ['tech', 'flask']},
    {'id': 2, 'title': 'Post 2', 'content': 'Content 2', 'author': 'LoiD', 'tag': ['python']},
    {'id': 3, 'title': 'Post 3', 'content': 'Content 3', 'author': 'LoiDD', 'tag': ['web']}
]
_next_post_id = 4

COMMENTS = [
    {'id': 1, 'post_id': 1, 'author': 'Loi', 'content': 'Bài viết rất hay!'},
    {'id': 2, 'post_id': 1, 'author': 'LoiD', 'content': 'Cảm ơn đã chia sẻ.'}
]
_next_comment_id = 3

USERS = [
    {'username': 'Loi', 'name': 'Loi Doan', 'bio': 'Flask Developer'},
    {'username': 'oli', 'name': 'oli Doan', 'bio': 'Tech Enthusiast'},
    {'username': 'iol', 'name': 'iol Doan', 'bio': 'Reader'}
]

FOLLOWS = {
    'oli': ['Loi'],
    'iol': ['Loi', 'oli']
}

@app.get('/api/v1/posts')
def list_posts():
    try:
        page = max(int(request.args.get('page', 1)), 1)
        size = max(min(int(request.args.get('size', 10)), 36), 1)
    except ValueError:
        return jsonify({'error': 'page and size must be integers'}), 400
    
    tag = request.args.get('tag', '')
    q = request.args.get('q', '')
    filtered = POST
    
    if tag:
        filtered = [p for p in filtered if tag.lower() in [t.lower() for t in p.get('tag', [])]]
    if q:
        filtered = [p for p in filtered if q.lower() in p['title'].lower() or q.lower() in p['content'].lower() or q.lower() in p['author'].lower()]
    
    total = len(filtered)
    start = (page - 1) * size
    end = start + size
    items = filtered[start:end]
    total_pages = (total + size - 1) // size if total > 0 else 1

    def build_url(p):
        return f"/api/v1/posts?page={p}&size={size}"
    
    links = {
        'self': {'href': build_url(page)},
        'first': {'href': build_url(1)},
        'last': {'href': build_url(total_pages)}
    }
    if page > 1:
        links['prev'] = {'href': build_url(page - 1)}
    if page < total_pages:
        links['next'] = {'href': build_url(page + 1)}

    return jsonify({
        'items': items,
        'pagination': {
            'page': page,
            'size': size,
            'total': total,
            'total_pages': total_pages
        },
        '_links': links
    }), 200

@app.post('/api/v1/posts')
def create_post():
    global _next_post_id
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'author' not in data:
        return jsonify({'error': 'title, content, and author are required'}), 400
    new_post = {
        'id': _next_post_id,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'tag': data.get('tag', [])
    }
    POST.append(new_post)
    _next_post_id += 1
    return jsonify(new_post), 201

@app.get('/api/v1/posts/<int:post_id>')
def get_post(post_id):
    post = next((p for p in POST if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404
    return jsonify(post), 200

@app.put('/api/v1/posts/<int:post_id>')
def update_post(post_id):
    post = next((p for p in POST if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    post['title'] = data.get('title', post['title'])
    post['author'] = data.get('author', post['author'])
    post['content'] = data.get('content', post['content'])
    post['tag'] = data.get('tag', post['tag'])
    return jsonify(post), 200

@app.delete('/api/v1/posts/<int:post_id>')
def delete_post(post_id):
    post = next((p for p in POST if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404
    POST.remove(post)
    return '', 204

@app.get('/api/v1/posts/<int:post_id>/comments')
def get_comments(post_id):
    post = next((p for p in POST if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404
    
    post_comments = [c for c in COMMENTS if c['post_id'] == post_id]
    return jsonify({'items': post_comments, 'total': len(post_comments)}), 200

@app.post('/api/v1/posts/<int:post_id>/comments')
def create_comment(post_id):
    global _next_comment_id
    post = next((p for p in POST if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404
    
    data = request.get_json()
    if not data or 'content' not in data or 'author' not in data:
        return jsonify({'error': 'author and content are required'}), 400
    
    new_comment = {
        'id': _next_comment_id,
        'post_id': post_id,
        'author': data['author'],
        'content': data['content']
    }
    COMMENTS.append(new_comment)
    _next_comment_id += 1
    return jsonify(new_comment), 201

@app.delete('/api/v1/posts/<int:post_id>/comments/<int:comment_id>')
def delete_comment(post_id, comment_id):
    """Xóa bình luận"""
    comment = next((c for c in COMMENTS if c['id'] == comment_id and c['post_id'] == post_id), None)
    if not comment:
        return jsonify({'error': 'comment not found'}), 404
    COMMENTS.remove(comment)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)