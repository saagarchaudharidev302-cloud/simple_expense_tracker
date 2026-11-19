import sqlite3
from datetime import date

import pytest

from expense_tracker.repository import ExpenseRepository
from expense_tracker.validation import CATEGORIES, FilterResult, ValidExpense


def make(amount=150, category="Food", description="Lunch", d=date(2026, 1, 5)):
    return ValidExpense(amount, category, description, d)


@pytest.fixture
def repo(db_path):
    repository = ExpenseRepository(db_path)
    repository.init_schema()
    yield repository
    repository.close()


def test_insert_and_get_roundtrip(repo):
    new_id = repo.insert(make())
    got = repo.get(new_id)
    assert (got.id, got.amount_minor, got.category, got.description, got.expense_date) == (
        new_id, 150, "Food", "Lunch", date(2026, 1, 5),
    )


def test_get_missing_returns_none(repo):
    assert repo.get(999) is None


def test_list_ordered_by_date_desc_then_id_desc(repo):
    a = repo.insert(make(d=date(2026, 1, 5)))
    b = repo.insert(make(d=date(2026, 1, 7)))
    c = repo.insert(make(d=date(2026, 1, 5)))
    assert [e.id for e in repo.list_expenses()] == [b, c, a]


def test_list_filters_inclusive_and_combined(repo):
    repo.insert(make(category="Food", d=date(2026, 1, 1)))
    inside = repo.insert(make(category="Food", d=date(2026, 1, 5)))
    edge = repo.insert(make(category="Food", d=date(2026, 1, 10)))
    repo.insert(make(category="Health", d=date(2026, 1, 7)))
    repo.insert(make(category="Food", d=date(2026, 1, 11)))

    both = FilterResult(start=date(2026, 1, 5), end=date(2026, 1, 10))
    assert len(repo.list_expenses(both)) == 3
    combined = FilterResult(category="Food", start=date(2026, 1, 5), end=date(2026, 1, 10))
    assert [e.id for e in repo.list_expenses(combined)] == [edge, inside]
    assert len(repo.list_expenses(FilterResult(category="Health"))) == 1
    assert len(repo.list_expenses(FilterResult(start=date(2026, 1, 10)))) == 2
    assert len(repo.list_expenses(FilterResult(end=date(2026, 1, 1)))) == 1


def test_update_changes_row_and_returns_one(repo):
    row_id = repo.insert(make())
    assert repo.update(row_id, make(amount=999, category="Other", description="X")) == 1
    assert repo.get(row_id).amount_minor == 999


def test_update_and_delete_missing_return_zero(repo):
    assert repo.update(42, make()) == 0
    assert repo.delete(42) == 0


def test_delete_removes_row(repo):
    row_id = repo.insert(make())
    assert repo.delete(row_id) == 1
    assert repo.get(row_id) is None


def test_ids_not_reused_after_delete(repo):
    first = repo.insert(make())
    repo.delete(first)
    second = repo.insert(make())
    assert second > first


def test_rollback_on_failure_leaves_data_unchanged(repo):
    keep = repo.insert(make())
    with pytest.raises(RuntimeError):
        with repo._transaction() as conn:
            conn.execute("DELETE FROM expenses")
            raise RuntimeError("forced")
    assert repo.get(keep) is not None


def test_failed_insert_does_not_persist(repo):
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert(make(category="Bogus"))
    assert repo.list_expenses() == []


@pytest.mark.parametrize("category", CATEGORIES)
def test_schema_accepts_each_category(repo, category):
    assert repo.insert(make(category=category))


def test_schema_rejects_unknown_category(repo):
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert(make(category="food"))


@pytest.mark.parametrize("amount", [0, 100_000_000, -1])
def test_schema_rejects_out_of_range_amount(repo, amount):
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert(make(amount=amount))


@pytest.mark.parametrize("amount", [1, 99_999_999])
def test_schema_accepts_amount_bounds(repo, amount):
    assert repo.insert(make(amount=amount))


def test_sql_metacharacters_stored_literally(repo):
    text = "x'); DROP TABLE expenses;--"
    row_id = repo.insert(make(description=text))
    assert repo.get(row_id).description == text


def test_init_schema_is_idempotent(repo):
    repo.insert(make())
    repo.init_schema()
    assert len(repo.list_expenses()) == 1


def test_data_persists_across_connections(db_path):
    first = ExpenseRepository(db_path)
    first.init_schema()
    row_id = first.insert(make())
    first.close()
    second = ExpenseRepository(db_path)
    try:
        assert second.get(row_id) is not None
    finally:
        second.close()
