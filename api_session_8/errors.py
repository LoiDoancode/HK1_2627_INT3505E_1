from flask import jsonify
from werkzeug.exceptions import HTTPException

class ApiError(Exception):
    """Base class - mọi ngoại lệ nghiệp vụ kế thừa từ class này"""
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "", code: str = None, status: int = None, detail: str = None):
        super().__init__(message)
        if code is not None:
            self.code = code
        if status is not None:
            self.status_code = status
        self.message = message
        self.detail = detail if detail is not None else message

class NotFound(ApiError):
    status_code = 404
    code = "not_found"

class Conflict(ApiError):
    status_code = 409
    code = "conflict"

class OutOfStock(ApiError):
    status_code = 409
    code = "out_of_stock"

class ValidationError(ApiError):
    status_code = 422
    code = "validation_error"

def register_error_handlers(app):
    """Đăng ký global error handlers cho Flask Application"""
    @app.errorhandler(ApiError)
    def _handle_api_error(err):
        return jsonify({
            "error": err.code,
            "code": err.code,
            "message": err.message,
            "detail": err.detail,
        }), err.status_code

    @app.errorhandler(HTTPException)
    def _handle_http_exception(err):
        code_str = err.name.lower().replace(" ", "_")
        return jsonify({
            "error": code_str,
            "code": code_str,
            "message": err.description,
            "detail": err.description,
        }), err.code

    @app.errorhandler(Exception)
    def _handle_generic_exception(err):
        app.logger.exception(f"Unhandled exception: {str(err)}")
        return jsonify({
            "error": "internal_error",
            "code": "internal_error",
            "message": "Đã xảy ra lỗi máy chủ nội bộ.",
            "detail": str(err),
        }), 500

