from flask import Flask, jsonify, request, make_response, g
from uuid import uuid4
import sqlite3

app = Flask('__name__')
BOOKS = [{"id": 1, "title": "code book", "author": "LoiDD", "price": 36018}]
next_id = 2
#BAI1
# @app.get('/books')
# def list_books():
#     return jsonify({
#         'data': BOOKS,
#         'total': len(BOOKS)
#     }), 200

# @app.get('/books/<int:book_id>')
# def get_books(book_id):
#     book = next((b for b in BOOKS if b['id'] == book_id), None)
#     if not book:
#         return jsonify({'error': 'book not found'}),     404
#     return jsonify(book), 200

# @app.post('/books')
# def create_book():
#     global next_id
#     if not request.is_json:
#         return jsonify({'error': 'request body must be JSON'}),     415
#     p = request.get_json(silent=True) or {}
#     t = p.get('title', '').strip()
#     a = p.get('author', '').strip()
#     if not a or not t:
#         return jsonify({'error': 'title and author are required'}), 422
#     book = {
#         'id': next_id,
#         'title': t,
#         'author': a
#     }
#     next_id += 1
#     BOOKS.append(book)
#     resp = make_response(jsonify(book), 201)
#     resp.headers['Location'] = f"books/{book['id']}"
#     return resp

#BAI2
# @app.get('/books/<int:bid>')
# def fetch(bid):
#     i = next((k for k, b in enumerate(BOOKS) if b['id'] == bid), None)
#     if i is None:
#         return jsonify(error = "Not Found"), 404
#     resp = make_response(jsonify(BOOKS[i]),200)
#     resp.headers['Cache-Control'] = 'max-age:60'
#     return resp

# @app.put('/books/<int:bid>')
# def put(bid):
#     i = next((k for k, b in enumerate(BOOKS) if b['id'] == bid), None)
#     if i is None:
#         return jsonify(error = "Not Found"), 404
#     p = request.get_json(silent = True) or {}
#     t, a = p.get('title'), p.get('author')
#     if not t or not a:
#         return jsonify(error = 'title and author are required'), 422
#     BOOKS[i] = {
#         'id': bid,
#         'title': t.strip(),
#         'author': a.strip(),
#         'isbn': p.get('isbn'),
#         'price': p. get('price')
#     }
#     return jsonify(BOOKS[i]), 200

# @app.patch('/books/<int:bid>')
# def patch(bid): 
#     i = next((k for k, b in enumerate(BOOKS) if b['id'] == bid), None)
#     if i is None:
#         return jsonify(error = 'Not Found'), 404
#     p = request.get_json(silent = True) or {}
#     if p.get('price', 0)<0:
#         return jsonify(error = 'price must be positive'), 422
#     for k in "title author isbn price".split():
#         if k in p:
#             BOOKS[i][k] = p[k]
#     return jsonify(BOOKS[i]), 200

# @app.delete('/books/<int:bid>')
# def delete(bid):
#     i = next((k for k,b in enumerate(BOOKS) if b['id'] ==bid), None)
#     if i is None:
#         return jsonify(error = "Not Found"), 404
#     BOOKS.pop(i)
#     return '', 204

app = Flask('__name__')
DB_FILE = 'library.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception = None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DB_FILE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            price REAL
        )
    ''')
    db.commit()
    db.close()

def row_to_book(row):
    return {
        'id': row['id'],
        'title': row['title'],
        'author': row['author'],
        'isbn': row['isbn'],
        'price': row['price']
    }

@app.get('/books')
def list_book():
    db = get_db()
    rows = db.execute('SELECT * FROM books').fetchall()
    return jsonify([row_to_book(r) for r in rows]), 200

@app.post('/books')
def create_book():
    p = request.get_json(silent=True) or {}
    t, a = p.get('title'), p.get('author')
    if not t or not a:
        return jsonify(error = 'title and author are required'), 422
    db = get_db()
    cur = db.execute(
        'INSERT INTO books (title, author, isbn, price) VALUES (?,?,?,?)',
        (t.strip(), a.strip(), p.get('isbn'), p.get('price'))
    )
    db.commit()
    new_row = db.execute('SELECT * FROM books WHERE id = ?', (cur.lastrowid,)).fetchone()
    return jsonify(row_to_book(new_row)), 201

@app.get('/books/<int:bid>')
def fetch(bid):
    db = get_db()
    row = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    if row is None:
        return jsonify(error = 'not found'), 404
    resp = make_response(jsonify(row_to_book(row)),200)
    resp.headers['Cache-Control'] = 'max-age=60'
    return resp

@app.put('/books/<int:bid>')
def put(bid):
    db = get_db()
    row = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    if row is None:
        return jsonify(error = 'not found'), 404
    p = request.get_json(silent=True) or {}
    t, a = p.get('title'), p.get('author')
    if not t or not a:
        return jsonify(error = 'title and author are required'), 422
    db.execute(
        'UPDATE books SET title = ?, author = ?, isbn = ?, price = ? WHERE id = ?',
        (t.strip(), a.strip(), p.get('isbn'), p.get('price'), bid)
    )
    db.commit()
    updated = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    return jsonify(row_to_book(updated)), 200

@app.patch('/books/<int:bid>')
def patch(bid):
    db = get_db()
    row = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    if row is None:
        return jsonify(error = 'not found'), 404
    p = request.get_json(silent=True) or {}
    t, a = p.get('title'), p.get('author')
    if not t or not a:
        return jsonify(error = 'title and author are required'), 422
    db.execute(
        'UPDATE books SET title = ?, author = ?, isbn = ?, price = ? WHERE id = ?',
        (t.strip(), a.strip(), p.get('isbn'), p.get('price'), bid)
    )
    db.commit()
    updated = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    return jsonify(row_to_book(updated)), 200

@app.delete('/books/<int:bid>')
def delete(bid):
    db = get_db()
    row = db.execute('SELECT * FROM books WHERE id = ?', (bid,)).fetchone()
    if row is None:
        return jsonify(error = 'Not found'), 404
    db.execute('DELET * FROM books WHERE id = ?', (bid,))
    db.commit()
    return '', 204

@app.get('/orders/<int:oid>')
def fetch_order(oid):
    db = get_db()
    row = db.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    if row is None:
        return jsonify(error = 'not found'), 404
    return jsonify(row_to_book(row)), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

    

