"""Pure validation rules for expenses and list filters (no I/O)."""
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

CATEGORIES = (
    "Food",
    "Transport",
    "Housing",
    "Utilities",
    "Entertainment",
    "Health",
    "Shopping",
    "Other",
)

MAX_AMOUNT_MINOR = 99_999_999
MAX_AMOUNT_CHARS = 20
MAX_DESCRIPTION_CHARS = 200

# fullmatch() is used everywhere so a trailing newline is never tolerated.
_AMOUNT_RE = re.compile(r"[0-9]+(\.[0-9]+)?")
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

MSG_AMOUNT_REQUIRED = "Amount is required."
MSG_AMOUNT_INVALID = "Amount must be a number greater than zero."
MSG_AMOUNT_ZERO = "Amount must be greater than zero."
MSG_AMOUNT_DECIMALS = "Amount must have at most 2 decimal places."
MSG_AMOUNT_MAX = "Amount must not exceed 999,999.99."
MSG_CATEGORY_REQUIRED = "Category is required."
MSG_CATEGORY_INVALID = "Category must be one of the listed categories."
MSG_DESCRIPTION_REQUIRED = "Description is required."
MSG_DESCRIPTION_LONG = "Description must be at most 200 characters."
MSG_DATE_REQUIRED = "Expense date is required."
MSG_DATE_INVALID = "Expense date must be a valid date in YYYY-MM-DD format."
MSG_DATE_FUTURE = "Expense date must not be in the future."
MSG_FILTER_CATEGORY = "Category filter must be one of the listed categories."
MSG_FILTER_START = "Start date must be a valid date in YYYY-MM-DD format."
MSG_FILTER_END = "End date must be a valid date in YYYY-MM-DD format."
MSG_FILTER_RANGE = "Start date must not be after end date; the date range was not applied."


@dataclass(frozen=True)
class ValidExpense:
    amount_minor: int
    category: str
    description: str
    expense_date: date


@dataclass(frozen=True)
class ValidationResult:
    """`expense` is set only when `errors` (field name -> message) is empty."""

    expense: ValidExpense | None
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class FilterResult:
    """Applied filters plus a message per rejected filter.

    Message keys: `category`, `start`, `end`, `range`.
    """

    category: str | None = None
    start: date | None = None
    end: date | None = None
    messages: dict[str, str] = field(default_factory=dict)

    @property
    def applied(self) -> bool:
        return any(v is not None for v in (self.category, self.start, self.end))


def _text(raw: dict, key: str) -> str:
    value = raw.get(key)
    return value if isinstance(value, str) else ""


def parse_strict_date(text: str) -> date | None:
    """Return the date for an exact YYYY-MM-DD string, else None."""
    if not _DATE_RE.fullmatch(text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _parse_amount(text: str) -> tuple[int | None, str | None]:
    text = text.strip()
    if not text:
        return None, MSG_AMOUNT_REQUIRED
    if len(text) > MAX_AMOUNT_CHARS or not _AMOUNT_RE.fullmatch(text):
        return None, MSG_AMOUNT_INVALID
    value = Decimal(text)
    if value <= 0:
        return None, MSG_AMOUNT_ZERO
    if value.as_tuple().exponent < -2:
        return None, MSG_AMOUNT_DECIMALS
    minor = int(value * 100)
    if minor > MAX_AMOUNT_MINOR:
        return None, MSG_AMOUNT_MAX
    return minor, None


def _parse_expense_date(text: str, today: date) -> tuple[date | None, str | None]:
    if not text:
        return None, MSG_DATE_REQUIRED
    parsed = parse_strict_date(text)
    if parsed is None:
        return None, MSG_DATE_INVALID
    if parsed > today:
        return None, MSG_DATE_FUTURE
    return parsed, None


def _parse_description(text: str) -> tuple[str | None, str | None]:
    text = text.strip()
    if not text:
        return None, MSG_DESCRIPTION_REQUIRED
    if len(text) > MAX_DESCRIPTION_CHARS:
        return None, MSG_DESCRIPTION_LONG
    return text, None


def _parse_category(text: str) -> tuple[str | None, str | None]:
    if not text:
        return None, MSG_CATEGORY_REQUIRED
    if text not in CATEGORIES:
        return None, MSG_CATEGORY_INVALID
    return text, None


def validate_expense(raw: dict, today: date) -> ValidationResult:
    """Validate all four fields, collecting one message per invalid field."""
    amount, amount_err = _parse_amount(_text(raw, "amount"))
    category, category_err = _parse_category(_text(raw, "category"))
    description, description_err = _parse_description(_text(raw, "description"))
    expense_date, date_err = _parse_expense_date(_text(raw, "expense_date"), today)

    errors = {
        name: err
        for name, err in (
            ("amount", amount_err),
            ("category", category_err),
            ("description", description_err),
            ("expense_date", date_err),
        )
        if err
    }
    if errors:
        return ValidationResult(expense=None, errors=errors)
    return ValidationResult(
        expense=ValidExpense(amount, category, description, expense_date)
    )


def _parse_filter_date(text: str, message: str, key: str, messages: dict) -> date | None:
    if not text:
        return None
    parsed = parse_strict_date(text)
    if parsed is None:
        messages[key] = message
    return parsed


def validate_filters(raw: dict) -> FilterResult:
    """Validate category/start/end independently.

    Future dates are allowed for filters. If both dates are valid but
    inverted, neither bound is applied.
    """
    messages: dict[str, str] = {}

    category = _text(raw, "category")
    if category and category not in CATEGORIES:
        messages["category"] = MSG_FILTER_CATEGORY
        category = ""

    start = _parse_filter_date(_text(raw, "start"), MSG_FILTER_START, "start", messages)
    end = _parse_filter_date(_text(raw, "end"), MSG_FILTER_END, "end", messages)

    if start is not None and end is not None and start > end:
        messages["range"] = MSG_FILTER_RANGE
        start = end = None

    return FilterResult(
        category=category or None, start=start, end=end, messages=messages
    )
