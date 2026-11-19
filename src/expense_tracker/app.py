"""App factory: configuration, error handling, logging and request checks."""

import logging
import os
from datetime import date
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

from flask import Flask, current_app, g, make_response, render_template, request
from werkzeug.exceptions import HTTPException

from expense_tracker.repository import ExpenseRepository
from expense_tracker.service import ExpenseService, NotFoundError

DEFAULT_DB_PATH = "data/expenses.db"
ALLOWED_HOSTNAMES = frozenset({"127.0.0.1", "localhost"})
DEFAULT_HTTP_PORT = "80"

logger = logging.getLogger("expense_tracker")

_GENERIC_MESSAGES = {
    400: ("Bad request", "The request could not be processed."),
    403: ("Forbidden", "The request was not allowed."),
    404: ("Not found", "The page was not found."),
    405: ("Method not allowed", "That action is not allowed on this page."),
    500: ("Something went wrong", "Something went wrong. Please try again."),
}


def _log_failure(operation: str, error: BaseException) -> None:
    # ADR 0004: operation and class name only; no exc_info, message or paths.
    logger.error("operation=%s error=%s", operation, type(error).__name__)


def _error_page(status: int, message: str | None = None):
    fallback = _GENERIC_MESSAGES[400] if 400 <= status < 500 else _GENERIC_MESSAGES[500]
    heading, default_message = _GENERIC_MESSAGES.get(status, fallback)
    return render_template("error.html", heading=heading, message=message or default_message), status


def _host_is_allowed() -> bool:
    hostname, sep, port = request.host.rpartition(":")
    if not sep:
        hostname, port = request.host, DEFAULT_HTTP_PORT
    listening_port = request.environ.get("SERVER_PORT", DEFAULT_HTTP_PORT)
    return hostname in ALLOWED_HOSTNAMES and port == str(listening_port)


def _origin_matches_host() -> bool:
    source = request.headers.get("Origin")
    if source is None:
        source = request.headers.get("Referer")
    if not source:
        return False
    try:
        return urlsplit(source).netloc == request.host
    except ValueError:
        return False


def _check_request():
    if not _host_is_allowed():
        return _error_page(400)
    if request.method == "POST" and not _origin_matches_host():
        return _error_page(403)
    return None


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(NotFoundError)
    def handle_not_found(_error):
        return _error_page(404, "Expense not found")

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if error.code is not None and error.code < 400:
            return error.get_response()
        body, status = _error_page(error.code or 500)
        response = make_response(body, status)
        # Keep protocol headers such as Allow on 405.
        for name, value in error.get_headers():
            if name.lower() not in ("content-type", "content-length"):
                response.headers[name] = value
        return response

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        _log_failure("request", error)
        return _error_page(500)


def get_service() -> ExpenseService:
    """Service bound to a per-request repository, closed at teardown."""
    if "service" not in g:
        g.repository = ExpenseRepository(current_app.config["DB_PATH"])
        g.service = ExpenseService(g.repository, current_app.config["TODAY"])
    return g.service


def _close_repository(_exc) -> None:
    repository = g.pop("repository", None)
    g.pop("service", None)
    if repository is not None:
        repository.close()


def _init_database(db_path: str) -> None:
    try:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        repository = ExpenseRepository(db_path)
        try:
            repository.init_schema()
        finally:
            repository.close()
    except Exception as error:
        _log_failure("startup", error)
        raise RuntimeError("startup failed") from None


def create_app(db_path: str | None = None, today: Callable[[], date] = date.today) -> Flask:
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("EXPENSE_DB_PATH") or DEFAULT_DB_PATH
    app.config["TODAY"] = today
    _init_database(app.config["DB_PATH"])
    app.before_request(_check_request)
    app.teardown_appcontext(_close_repository)
    _register_error_handlers(app)
    from expense_tracker.web import bp  # deferred: web imports get_service from this module

    app.register_blueprint(bp)
    return app
