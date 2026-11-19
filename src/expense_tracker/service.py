"""Business orchestration: validation, existence checks and display shaping."""
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from expense_tracker.repository import Expense, ExpenseRepository
from expense_tracker.validation import (
    ValidationResult,
    validate_expense,
    validate_filters,
)

EMPTY_NONE_RECORDED = "none_recorded"
EMPTY_NO_MATCH = "no_match"


class NotFoundError(Exception):
    """The requested expense does not exist (including vanishing mid-request)."""


@dataclass(frozen=True)
class ExpenseView:
    id: int
    amount_display: str
    category: str
    description: str
    expense_date: date


@dataclass(frozen=True)
class ListResult:
    expenses: list[ExpenseView]
    filters_applied: bool
    messages: dict[str, str] = field(default_factory=dict)
    # None when there are rows; otherwise which empty-state text to show.
    empty_state: str | None = None


def format_amount(amount_minor: int) -> str:
    return f"{amount_minor // 100}.{amount_minor % 100:02d}"


def _to_view(expense: Expense) -> ExpenseView:
    return ExpenseView(
        id=expense.id,
        amount_display=format_amount(expense.amount_minor),
        category=expense.category,
        description=expense.description,
        expense_date=expense.expense_date,
    )


class ExpenseService:
    def __init__(self, repository: ExpenseRepository, today: Callable[[], date]):
        self._repo = repository
        self._today = today

    def create(self, raw: dict) -> ValidationResult:
        result = validate_expense(raw, self._today())
        if result.is_valid:
            self._repo.insert(result.expense)
        return result

    def get(self, expense_id: int) -> ExpenseView:
        expense = self._repo.get(expense_id)
        if expense is None:
            raise NotFoundError
        return _to_view(expense)

    def update(self, expense_id: int, raw: dict) -> ValidationResult:
        self.get(expense_id)
        result = validate_expense(raw, self._today())
        if result.is_valid and self._repo.update(expense_id, result.expense) == 0:
            raise NotFoundError
        return result

    def delete(self, expense_id: int) -> None:
        self.get(expense_id)
        if self._repo.delete(expense_id) == 0:
            raise NotFoundError

    def list_expenses(self, raw_filters: dict) -> ListResult:
        filters = validate_filters(raw_filters)
        views = [_to_view(e) for e in self._repo.list_expenses(filters)]
        empty_state = None
        if not views:
            empty_state = EMPTY_NO_MATCH if filters.applied else EMPTY_NONE_RECORDED
        return ListResult(views, filters.applied, filters.messages, empty_state)
