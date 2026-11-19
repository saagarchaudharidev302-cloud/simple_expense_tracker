from datetime import date

import pytest

from expense_tracker import service as svc
from expense_tracker.repository import ExpenseRepository
from expense_tracker.service import ExpenseService, NotFoundError

VALID = {
    "amount": "1.50",
    "category": "Food",
    "description": "Lunch",
    "expense_date": "2026-06-01",
}


@pytest.fixture
def repo(db_path):
    repository = ExpenseRepository(db_path)
    repository.init_schema()
    yield repository
    repository.close()


@pytest.fixture
def service(repo, today):
    return ExpenseService(repo, lambda: today)


def test_create_stores_values(service, repo):
    result = service.create(VALID)
    assert result.is_valid
    (stored,) = repo.list_expenses()
    assert (stored.amount_minor, stored.category, stored.description, stored.expense_date) == (
        150, "Food", "Lunch", date(2026, 6, 1),
    )


def test_create_invalid_changes_nothing(service, repo):
    result = service.create({**VALID, "amount": "0", "category": ""})
    assert set(result.errors) == {"amount", "category"}
    assert repo.list_expenses() == []


def test_create_future_date_uses_injected_today(service, repo):
    assert not service.create({**VALID, "expense_date": "2026-06-16"}).is_valid
    assert service.create({**VALID, "expense_date": "2026-06-15"}).is_valid


def test_update_existing(service, repo):
    service.create(VALID)
    row_id = repo.list_expenses()[0].id
    result = service.update(row_id, {**VALID, "amount": "20.00", "description": "Dinner"})
    assert result.is_valid
    updated = service.get(row_id)
    assert (updated.amount_display, updated.description) == ("20.00", "Dinner")


def test_update_invalid_changes_nothing(service, repo):
    service.create(VALID)
    row_id = repo.list_expenses()[0].id
    result = service.update(row_id, {**VALID, "description": "  "})
    assert "description" in result.errors
    assert service.get(row_id).description == "Lunch"


def test_update_missing_raises_not_found(service):
    with pytest.raises(NotFoundError):
        service.update(99, VALID)


def test_delete_existing(service, repo):
    service.create(VALID)
    row_id = repo.list_expenses()[0].id
    service.delete(row_id)
    assert repo.list_expenses() == []


def test_delete_missing_raises_not_found(service):
    with pytest.raises(NotFoundError):
        service.delete(99)


def test_get_missing_raises_not_found(service):
    with pytest.raises(NotFoundError):
        service.get(99)


class _VanishingRepo:
    """Row exists at the check but is gone by the write (FND-007)."""

    def __init__(self, inner):
        self._inner = inner

    def get(self, expense_id):
        return self._inner.get(expense_id)

    def update(self, expense_id, expense):
        self._inner.delete(expense_id)
        return self._inner.update(expense_id, expense)

    def delete(self, expense_id):
        self._inner.delete(expense_id)
        return self._inner.delete(expense_id)


def test_update_vanishing_record_maps_to_not_found(repo, today):
    ExpenseService(repo, lambda: today).create(VALID)
    row_id = repo.list_expenses()[0].id
    racing = ExpenseService(_VanishingRepo(repo), lambda: today)
    with pytest.raises(NotFoundError):
        racing.update(row_id, VALID)


def test_delete_vanishing_record_maps_to_not_found(repo, today):
    ExpenseService(repo, lambda: today).create(VALID)
    row_id = repo.list_expenses()[0].id
    racing = ExpenseService(_VanishingRepo(repo), lambda: today)
    with pytest.raises(NotFoundError):
        racing.delete(row_id)


@pytest.mark.parametrize(
    "minor, text", [(150, "1.50"), (100_000, "1000.00"), (1, "0.01"), (99_999_999, "999999.99")]
)
def test_amount_display(minor, text):
    assert svc.format_amount(minor) == text


def test_list_displays_formatted_amounts_newest_first(service):
    service.create({**VALID, "amount": "1000", "expense_date": "2026-05-01"})
    service.create(VALID)
    result = service.list_expenses({})
    assert [e.amount_display for e in result.expenses] == ["1.50", "1000.00"]
    assert result.empty_state is None
    assert not result.filters_applied


def test_empty_state_none_recorded_without_filters(service):
    result = service.list_expenses({})
    assert result.empty_state == svc.EMPTY_NONE_RECORDED


def test_empty_state_no_match_with_valid_filter(service):
    service.create(VALID)
    result = service.list_expenses({"category": "Health"})
    assert result.filters_applied
    assert result.empty_state == svc.EMPTY_NO_MATCH


def test_inverted_range_only_is_not_an_applied_filter(service):
    result = service.list_expenses({"start": "2026-02-01", "end": "2026-01-01"})
    assert not result.filters_applied
    assert "range" in result.messages
    assert result.empty_state == svc.EMPTY_NONE_RECORDED


def test_inverted_range_still_lists_everything(service):
    service.create(VALID)
    result = service.list_expenses({"start": "2026-12-01", "end": "2026-01-01"})
    assert len(result.expenses) == 1
    assert "range" in result.messages


def test_invalid_filter_message_with_valid_filter_applied(service):
    service.create(VALID)
    result = service.list_expenses({"category": "Food", "start": "bad"})
    assert result.filters_applied
    assert "start" in result.messages
    assert len(result.expenses) == 1
