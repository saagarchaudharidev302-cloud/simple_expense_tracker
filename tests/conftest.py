from datetime import date

import pytest

FIXED_TODAY = date(2026, 6, 15)


@pytest.fixture
def today():
    """Fixed 'today' so future-date rules are deterministic."""
    return FIXED_TODAY


@pytest.fixture
def db_path(tmp_path):
    """Path to a throwaway SQLite file, unique per test."""
    return str(tmp_path / "expenses.db")


@pytest.fixture
def app(db_path, today):
    from expense_tracker.app import create_app

    return create_app(db_path=db_path, today=lambda: today)


@pytest.fixture
def client(app):
    """Test client whose Host is a valid listening address, so the real Host
    check runs (FND-014)."""
    return app.test_client()
