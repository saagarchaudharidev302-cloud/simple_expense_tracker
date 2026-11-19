import logging
import sqlite3

import pytest
from werkzeug.exceptions import Forbidden

from expense_tracker.app import create_app, get_service

SECRET_TEXT = "secret-internal-detail"


@pytest.fixture
def writes():
    return []


@pytest.fixture
def app(db_path, today, writes):
    app = create_app(db_path=db_path, today=lambda: today)

    @app.route("/boom")
    def boom():
        raise sqlite3.OperationalError(f"unable to open {SECRET_TEXT}")

    @app.route("/forbidden-raised")
    def forbidden_raised():
        raise Forbidden()

    @app.route("/missing-expense")
    def missing_expense():
        get_service().get(999)

    @app.route("/write", methods=["GET", "POST"])
    def write():
        writes.append(1)
        return "ok"

    return app


def failure_records(caplog):
    return [r for r in caplog.records if r.name == "expense_tracker"]


# --- error pages and logging (AC-015, AC-016) ---

def test_unexpected_exception_gives_generic_500_and_policy_log(client, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.get("/boom")
    assert response.status_code == 500
    body = response.get_data(as_text=True)
    assert "Something went wrong" in body
    assert SECRET_TEXT not in body
    records = failure_records(caplog)
    assert len(records) == 1
    record = records[0]
    assert record.getMessage() == "operation=request error=OperationalError"
    assert record.exc_info is None
    assert SECRET_TEXT not in caplog.text
    assert "Traceback" not in caplog.text


def test_unknown_url_returns_404_without_failure_log(client, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert failure_records(caplog) == []


def test_raised_http_error_keeps_its_status_and_is_not_logged(client, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.get("/forbidden-raised")
    assert response.status_code == 403
    assert failure_records(caplog) == []


def test_method_not_allowed_is_not_converted_to_500(client, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.delete("/write")
    assert response.status_code == 405
    assert "Allow" in response.headers
    body = response.get_data(as_text=True)
    assert "Method not allowed" in body
    assert "Something went wrong" not in body
    assert failure_records(caplog) == []


def test_missing_expense_returns_404_page_without_failure_log(client, caplog):
    caplog.set_level(logging.DEBUG)
    response = client.get("/missing-expense")
    assert response.status_code == 404
    assert "Expense not found" in response.get_data(as_text=True)
    assert failure_records(caplog) == []


def test_startup_failure_logged_with_class_name_only(tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    blocker = tmp_path / "file"
    blocker.write_text("x")
    bad_path = str(blocker / "sub" / "expenses.db")
    with pytest.raises(RuntimeError):
        create_app(db_path=bad_path)
    records = failure_records(caplog)
    assert len(records) == 1
    assert records[0].getMessage().startswith("operation=startup error=")
    assert records[0].exc_info is None
    assert str(tmp_path) not in caplog.text
    assert "Traceback" not in caplog.text


def test_db_path_read_from_environment(tmp_path, monkeypatch):
    target = tmp_path / "env.db"
    monkeypatch.setenv("EXPENSE_DB_PATH", str(target))
    create_app()
    assert target.exists()


# --- Host check ---

@pytest.mark.parametrize("host", ["localhost", "127.0.0.1"])
@pytest.mark.parametrize("port", [80, 5000, 8123])
def test_allowed_hostnames_accepted_on_any_listening_port(app, host, port):
    base = f"http://{host}" if port == 80 else f"http://{host}:{port}"
    response = app.test_client().get("/write", base_url=base)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "host", ["evil.example", "evil.example:5000", "localhost.evil.example", "127.0.0.1.evil.example", "0.0.0.0"]
)
def test_other_hostnames_rejected_with_400(app, writes, host):
    response = app.test_client().get("/write", headers={"Host": host})
    assert response.status_code == 400
    assert writes == []
    assert host not in response.get_data(as_text=True)


def test_host_port_differing_from_listening_port_rejected(app):
    response = app.test_client().get(
        "/write", base_url="http://localhost:5000", headers={"Host": "localhost:6000"}
    )
    assert response.status_code == 400


# --- Origin / Referer check ---

def test_post_without_origin_or_referer_rejected_and_not_executed(client, writes):
    response = client.post("/write")
    assert response.status_code == 403
    assert writes == []


def test_post_with_mismatching_origin_rejected(client, writes):
    response = client.post("/write", headers={"Origin": "http://evil.example"})
    assert response.status_code == 403
    assert writes == []
    assert "evil.example" not in response.get_data(as_text=True)


def test_post_with_null_origin_rejected(client, writes):
    assert client.post("/write", headers={"Origin": "null"}).status_code == 403
    assert writes == []


def test_post_with_matching_origin_accepted(client, writes):
    response = client.post("/write", headers={"Origin": "http://localhost"})
    assert response.status_code == 200
    assert writes == [1]


def test_origin_with_matching_host_but_other_port_rejected(app, writes):
    response = app.test_client().post(
        "/write", base_url="http://localhost:5000", headers={"Origin": "http://localhost:6000"}
    )
    assert response.status_code == 403
    assert writes == []


def test_post_without_origin_uses_matching_referer(client, writes):
    response = client.post("/write", headers={"Referer": "http://localhost/expenses/new"})
    assert response.status_code == 200
    assert writes == [1]


def test_post_with_mismatching_referer_rejected(client, writes):
    response = client.post("/write", headers={"Referer": "http://evil.example/x"})
    assert response.status_code == 403
    assert writes == []


def test_mismatching_origin_not_rescued_by_matching_referer(client, writes):
    response = client.post(
        "/write",
        headers={"Origin": "http://evil.example", "Referer": "http://localhost/x"},
    )
    assert response.status_code == 403
    assert writes == []


def test_get_does_not_require_origin(client):
    assert client.get("/write").status_code == 200


# --- repository failure through real routes (REQ-020, REQ-NFR-002) ---

FORM = {
    "amount": "12.50",
    "category": "Food",
    "description": "Lunch",
    "expense_date": "2026-06-01",
}
ORIGIN = {"Origin": "http://localhost"}


def test_repository_failure_on_create_gives_500_and_stores_nothing(client, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    def fail(self, expense):
        raise sqlite3.OperationalError(f"disk {SECRET_TEXT}")

    monkeypatch.setattr("expense_tracker.repository.ExpenseRepository.insert", fail)
    response = client.post("/expenses", data=FORM, headers=ORIGIN)
    assert response.status_code == 500
    assert SECRET_TEXT not in response.get_data(as_text=True)
    assert SECRET_TEXT not in caplog.text
    assert [r.getMessage() for r in failure_records(caplog)] == [
        "operation=request error=OperationalError"
    ]
    monkeypatch.undo()
    assert "Lunch" not in client.get("/").get_data(as_text=True)


def test_repository_failure_on_update_gives_500_and_keeps_data(client, monkeypatch, caplog):
    created = client.post("/expenses", data=FORM, headers=ORIGIN)
    assert created.status_code == 303
    expense_id = get_id_from_list(client)
    caplog.set_level(logging.DEBUG)

    def fail(self, expense_id, expense):
        raise sqlite3.OperationalError(f"disk {SECRET_TEXT}")

    monkeypatch.setattr("expense_tracker.repository.ExpenseRepository.update", fail)
    response = client.post(
        f"/expenses/{expense_id}", data={**FORM, "description": "Changed"}, headers=ORIGIN
    )
    assert response.status_code == 500
    assert SECRET_TEXT not in response.get_data(as_text=True)
    assert len(failure_records(caplog)) == 1
    monkeypatch.undo()
    text = client.get("/").get_data(as_text=True)
    assert "Lunch" in text
    assert "Changed" not in text


def get_id_from_list(client):
    import re

    match = re.search(r"/expenses/(\d+)/edit", client.get("/").get_data(as_text=True))
    assert match
    return int(match.group(1))
