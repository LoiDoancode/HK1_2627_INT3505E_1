from flask import Flask, jsonify, request, make_response
from uuid import uuid4
app = Flask('__name__')
BOOKS = []
next_id = 1
@app.get('/books')
def list_books():
    return jsonify({
        'data': BOOKS,
        'total': len(BOOKS)
    }), 200

@app.get('/books/<int:book_id>')
def get_books(book_id):
    book = next((b for b in BOOKS if b['id'] == book_id), None)
    if not book:
        return jsonify({'error': 'book not found'}),     404
    return jsonify(book), 200

@app.post('/books')
def create_book():
    global next_id
    if not request.is_json:
        return jsonify({'error': 'request body must be JSON'}),     415
    p = request.get_json(silent=True) or {}
    t = p.get('title', '').strip()
    a = p.get('author', '').strip()
    if not a or not t:
        return jsonify({'error': 'title and author are required'}), 422
    book = {
        'id': next_id,
        'title': t,
        'author': a
    }
    next_id += 1
    BOOKS.append(book)
    resp = make_response(jsonify(book), 201)
    resp.headers['Location'] = f"books/{book['id']}"
    return resp

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

    

