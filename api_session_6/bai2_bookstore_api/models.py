# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)

    books = db.relationship("Book", back_populates="category", cascade="all, delete-orphan")
    def __init__(self, name: str, slug: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.slug = slug


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    price_vnd = db.Column(db.Float, default=0.0, index=True)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    category = db.relationship("Category", back_populates="books")

    def __init__(
        self,
        title: str,
        isbn: str,
        price_vnd: float = 0.0,
        stock: int = 0,
        category_id: int | None = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.isbn = isbn
        self.price_vnd = price_vnd
        self.stock = stock
        self.category_id = category_id

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "raw_id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price": {
                "amount": self.price_vnd,
                "currency": "VND"
            },
            "stock": self.stock,
            "category": {
                "id": self.category.id,
                "name": self.category.name,
                "slug": self.category.slug
            } if self.category else None,
            "created_at": self.created_at.isoformat() + "Z"
        }