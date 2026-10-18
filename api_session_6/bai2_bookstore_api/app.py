import os
from flask import Flask
from sqlalchemy import select, func
from models import db, Book, Category
from routes.books import bp as books_bp

def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(books_bp)

    with app.app_context():
        db.create_all()
        category_count = db.session.scalar(select(func.count(Category.id))) or 0

        if not test_config and category_count == 0:
            c_tech = Category(name="Technology", slug="tech")
            c_lit = Category(name="Literature", slug="literature")
            c_biz = Category(name="Business", slug="business")
            db.session.add_all([c_tech, c_lit, c_biz])
            db.session.commit()

            sample_books = []
            for i in range(1, 101):
                cat = c_tech if i % 3 == 0 else (c_lit if i % 3 == 1 else c_biz)
                sample_books.append(Book(
                    title=f"Lập trình hướng dịch vụ - Tập {i:03d}",
                    isbn=f"978{i:010d}",
                    price_vnd=float(100000 + (i % 8) * 35000),
                    stock=i*3,
                    category_id=cat.id
                ))
            db.session.add_all(sample_books)
            db.session.commit()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)