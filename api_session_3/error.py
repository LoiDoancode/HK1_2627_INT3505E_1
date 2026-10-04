import uuid, logging
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)
ERROR_BASE = 'https://api.example.com/probs'
class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__()
        self.status = status
        self.title = title
        self.detail = detail
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about_blank"
        self.extra = extra

def _problem(status, title, detail=None, type_path=None, **extra):
    body = {
        "type": f"{ERROR_BASE}/{type_path}" if type_path else "about:blank",
        "title": title,
        "status": status,
        "trace_id": str(uuid.uuid4())
    }
    if detail:
        body['detail'] = detail
    body.update(extra)
    resp = jsonify(body)
    resp.status_code = status
    resp.headers['Content-Type'] = 'application/problem+json'
    return resp
    
def register_error_handlers(app):
    @app.errorhandler(ApiProblem)
    def handle_api_problem(e):
        return _problem(
            status=e.status,
            title=e.title,
            detail=e.detail,
            type_path=e.type.replace(f"{ERROR_BASE}/","") if e.type.startswith(ERROR_BASE) else None,
            **e.extra
        )
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return _problem(
            status=e.code,
            title=e.name,
            detail=e.description
        )
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.exception("Uncaught exception: %s", e)
        return _problem(
            status=500,
            title="Internal Server Error",
            detail="An unexpected error occurred on the server"
        )