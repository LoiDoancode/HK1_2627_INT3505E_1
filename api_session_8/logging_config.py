import json
import logging
import sys
import time
from flask import has_request_context, request

class JsonFormatter(logging.Formatter):
    """Log một dòng JSON theo chuẩn (Slide 32-33)"""
    def format(self, record):
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        if has_request_context():
            payload["rid"] = request.headers.get("X-Request-Id", "-")
            payload["path"] = request.path
            payload["method"] = request.method
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging(app):
    """Cấu hình structured logging và latency tracking cho Flask app"""
    # Xóa các handler mặc định của app.logger
    app.logger.handlers.clear()
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(JsonFormatter())
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    @app.before_request
    def _record_start_time():
        request._t0 = time.perf_counter()

    @app.after_request
    def _record_request_completion(response):
        if hasattr(request, "_t0"):
            ms = int((time.perf_counter() - request._t0) * 1000)
            # Log theo dõi request latency
            app.logger.info(
                f"{request.method} {request.path} {response.status_code} in {ms}ms"
            )
        return response

