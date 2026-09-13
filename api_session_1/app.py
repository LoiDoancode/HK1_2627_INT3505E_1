# BAI1
# from flask import Flask, jsonify, request

# app = Flask('__name__')

# @app.route("/")
# def index():
#     return {"message": "Hello API"}
# if __name__ == '__main__':
#     app.run(host="127.0.0.1", port=5000, debug=True)

# BAI2
# from flask import Flask, jsonify, request

# app = Flask(__name__)

# @app.route('/health', methods=['GET'])
# def health():
#     return jsonify({'status': 'OK'}), 200
# @app.route('/echo', methods=['POST'])
# def echo():
#     data =request.get_json(silent=True) or {}
#     return jsonify({'you_sent': data}), 200
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000, debug=True)

#BAI3
# from flask.cli import find_app_by_string
# from flask import Flask, jsonify, request
# from uuid import uuid4
# app = Flask(__name__)
# STUDENTS = []
# @app.route('/students', methods=['POST'])
# def create_students():
#     body = request.get_json(silent=True) or {}
#     name = body.get('name')
#     if not name:
#         return jsonify({'error': 'name la bat buoc'}), 400
#     student = {
#         'id': str(uuid4()),
#         'name': name,
#         'gpa': body.get('gpa', 0.0),
#     }
#     STUDENTS.append(student)
#     return jsonify(student), 201
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000, debug=True)

#BAI4
from flask.cli import find_app_by_string
from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

BOOKS = [
    {"id": "abcd-1234"},
    {"id": "abcd-1235",}
]

def find_by_string(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            return book
    return None

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = find_by_string(book_id)
    if book is None:
        return jsonify({'error': 'book not found'}), 400
    return jsonify(book), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return jsonify({'id': item_id}), 200

@app.route('/books', methods=['GET'])
def list_book():
    limit = int(request.args.get('limit', 20))
    q = request.args.get('q', '').strip().lower()
    items = [b for b in BOOKS if q in b['t'].lower()]
    return jsonify({'items': items}), 200