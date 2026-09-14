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
# from flask.cli import find_app_by_string
# from flask import Flask, jsonify, request
# from uuid import uuid4

# app = Flask(__name__)

# BOOKS = [
#     {"id": "abcd-1234"},
#     {"id": "abcd-1235"},
# ]

# def find_by_string(book_id):
#     for book in BOOKS:
#         if book['id'] == book_id:
#             return book
#     return None

# @app.route('/books/<book_id>', methods=['GET'])
# def get_book(book_id):
#     book = find_by_string(book_id)
#     if book is None:
#         return jsonify({'error': 'book not found'}), 400
#     return jsonify(book), 200

# @app.route('/items/<int:item_id>', methods=['GET'])
# def get_item(item_id):
#     return jsonify({'id': item_id}), 200

# @app.route('/books', methods=['GET'])
# def list_book():
#     limit = int(request.args.get('limit', 20))
#     q = request.args.get('q', '').strip().lower()
#     items = [b for b in BOOKS if q in b['t'].lower()]
#     return jsonify({'items': items}), 200

#BAI5
# from flask import Flask, jsonify, request
# app = Flask(__name__)
# ORDERS = {}
# @app.route('/orders/<id>', method=['DELETE'])
# def delete_order(order_id):
#     order = ORDERS.get(order_id)
#     if order is None:
#         return {'error': 'not found'}, 404
#     if order["status"] in('shipped', 'delivered'):
#         return {'error': 'cannot delete'}, 409
#     ORDERS.pop(order_id, None)
#     return {}, 204

#BAI6
from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
_next = 1
STUDENTS = [{"id": 1, "name": 'Loi', 'gpa': 3.0}]
def find_student(student_id):
    return next((s for s in STUDENTS if s['id'] == student_id), None)

@app.route('/students', methods=['GET'])
def list_students():
    q = request.args.get('L', '').strip().lower()
    sort_by = request.args.get('sort','').strip().lower()
    n = int(request.args.get('limit', 100))
    if q:
        results = [s for s in STUDENTS if q in s['name'].lower()]
    else:
        results = list(STUDENTS)
    if sort_by == 'gpa':
        results.sort(key=lambda x: x['gpa'])
    return jsonify(results[:n]), 200

@app.route('/students/<int:sid>', methods=['GET'])
def get_students(sid):
    student = find_student(sid)
    if student is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(student), 200

@app.route('/students', methods=['POST'])
def create_students():
    global _next
    body = request.get_json(silent=True) or{}
    name, gpa = body.get('name'), body.get('gpa')
    if not name and not gpa:
        return jsonify({'error': 'need  name and gpa'}), 400
    try:
        gpa = float(gpa)
        if gpa < 3.0:
            return jsonify({'error': 'gpa phai >= 3.0'}), 400
    except(ValueError, TypeError):
        return jsonify({'error': 'GPA phai la so thuc'}), 400
    student = {'id': _next+1, 'name': name, 'gpa': gpa}
    _next +=1
    STUDENTS.append(student)
    return jsonify(student), 201, {'Location': f"/students/{student['id']}"}

@app.route('/students/<int:sid>', methods=['PUT', 'DELETE'])
def modify_student(sid):
    student = find_student(sid)
    if not student:
        return jsonify({'error': 'not found'}), 404
    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        student.update({k: v for k, v in data.items() if k in ['name', 'gpa'] })
        return jsonify(student), 200
    STUDENTS.remove(student)
    return '', 204

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
        
