from flask import Flask, request, jsonify, make_response

app = Flask('__name__')

POST = [
    {
        'id': 1,
        'title': 'Post 1',
        'content': 'Content 1',
        'author': 'Loi'
    },
    {
        'id': 2,
        'title': 'Post 2',
        'content': 'Content 2',
        'author': 'LoiD'
    },
    {
        'id': 3,
        'title': 'Post 3',
        'content': 'Content 3',
        'author': 'LoiDD'
    }
]
_next_postt_id = 4

@app.get('/api/v1/posts')
def list_posts():
    try:
        page = max(int(request.args.get('page',1)),1)
        size = max(min(int(request.args.get('size',10)),36),1)
    except ValueError:
        return jsonify('error': 'page and size must be integers'), 400
    
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
    items = filtered[start: end]
    total_pages = (total + size - 1) // size if total > 0 else 1

    def build_url(p):
        return f"/api/v1/posts?page={p}&size={size}"
    
    links ={
        'self': {'href': build_url(page)},
        'first': {'href': build_url(1)},
        'last': {'href': build_url(total_pages)}
    }

    if page > 1:
        links['prev'] = {'href': build_url(page-1)}
    if page < total_pages:
        links['next'] = {'href': build_url(page+1)}

    return jsonify({
        'items': items,
        'pagination':{
            'page': page,
            'size': size,
            'total': total,
            'total_pages': total_pages
        },
        '_links': links
    }), 200