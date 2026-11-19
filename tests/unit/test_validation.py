from datetime import date

import pytest

from expense_tracker import validation as v


def make(**overrides):
    raw = {
        "amount": "12.50",
        "category": "Food",
        "description": "Lunch",
        "expense_date": "2026-06-15",
    }
    raw.update(overrides)
    return raw


def validate(today, **overrides):
    return v.validate_expense(make(**overrides), today)


def test_categories_are_exactly_the_eight_required_values():
    assert v.CATEGORIES == (
        "Food", "Transport", "Housing", "Utilities",
        "Entertainment", "Health", "Shopping", "Other",
    )


def test_valid_expense_converts_to_minor_units(today):
    result = validate(today)
    assert result.is_valid
    assert result.expense == v.ValidExpense(
        1250, "Food", "Lunch", date(2026, 6, 15)
    )


@pytest.mark.parametrize(
    "text, minor",
    [
        ("0.01", 1),
        ("999999.99", 99_999_999),
        ("1.50", 150),
        ("1.5", 150),
        ("7", 700),
        (" 5 ", 500),
        ("5\n", 500),
        ("007.10", 710),
    ],
)
def test_amount_accepted(today, text, minor):
    result = validate(today, amount=text)
    assert result.is_valid, result.errors
    assert result.expense.amount_minor == minor


@pytest.mark.parametrize(
    "text, message",
    [
        ("1000000.00", v.MSG_AMOUNT_MAX),
        ("999999.991", v.MSG_AMOUNT_DECIMALS),
        ("0", v.MSG_AMOUNT_ZERO),
        ("0.00", v.MSG_AMOUNT_ZERO),
        ("-1", v.MSG_AMOUNT_INVALID),
        ("+1", v.MSG_AMOUNT_INVALID),
        ("1.500", v.MSG_AMOUNT_DECIMALS),
        ("1.234", v.MSG_AMOUNT_DECIMALS),
        ("1e2", v.MSG_AMOUNT_INVALID),
        ("1_0", v.MSG_AMOUNT_INVALID),
        ("1,000", v.MSG_AMOUNT_INVALID),
        (".5", v.MSG_AMOUNT_INVALID),
        ("5.", v.MSG_AMOUNT_INVALID),
        ("NaN", v.MSG_AMOUNT_INVALID),
        ("Infinity", v.MSG_AMOUNT_INVALID),
        ("abc", v.MSG_AMOUNT_INVALID),
        ("5\n5", v.MSG_AMOUNT_INVALID),
        ("٥", v.MSG_AMOUNT_INVALID),
        ("1" * 21, v.MSG_AMOUNT_INVALID),
        ("", v.MSG_AMOUNT_REQUIRED),
        ("   ", v.MSG_AMOUNT_REQUIRED),
    ],
)
def test_amount_rejected(today, text, message):
    result = validate(today, amount=text)
    assert result.expense is None
    assert result.errors == {"amount": message}


@pytest.mark.parametrize("text", ["2026-06-15", "2026-06-14", "2024-02-29"])
def test_date_accepted(today, text):
    assert validate(today, expense_date=text).is_valid


def test_date_tomorrow_rejected(today):
    result = validate(today, expense_date="2026-06-16")
    assert result.errors == {"expense_date": v.MSG_DATE_FUTURE}


@pytest.mark.parametrize(
    "text",
    [
        "2026-1-5",
        "20260105",
        "2026-02-30",
        "2025-02-29",
        "2026-13-01",
        "0000-01-01",
        "2026-01-05\n",
        " 2026-01-05",
        "05-01-2026",
        "2026/01/05",
        "abcd-ef-gh",
    ],
)
def test_date_malformed_rejected(today, text):
    result = validate(today, expense_date=text)
    assert result.errors == {"expense_date": v.MSG_DATE_INVALID}


def test_date_missing(today):
    assert validate(today, expense_date="").errors == {
        "expense_date": v.MSG_DATE_REQUIRED
    }


def test_description_200_chars_accepted(today):
    assert validate(today, description="a" * 200).is_valid


def test_description_201_chars_rejected(today):
    result = validate(today, description="a" * 201)
    assert result.errors == {"description": v.MSG_DESCRIPTION_LONG}


def test_description_is_trimmed(today):
    assert validate(today, description="  Lunch  ").expense.description == "Lunch"


def test_description_length_counts_after_trim(today):
    assert validate(today, description="  " + "a" * 200 + "  ").is_valid


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_description_blank_is_missing(today, text):
    assert validate(today, description=text).errors == {
        "description": v.MSG_DESCRIPTION_REQUIRED
    }


@pytest.mark.parametrize("category", v.CATEGORIES)
def test_each_category_accepted(today, category):
    assert validate(today, category=category).is_valid


@pytest.mark.parametrize("category", ["Food ", "food", "Travel", "Food\n"])
def test_unknown_category_rejected(today, category):
    assert validate(today, category=category).errors == {
        "category": v.MSG_CATEGORY_INVALID
    }


def test_missing_category(today):
    assert validate(today, category="").errors == {
        "category": v.MSG_CATEGORY_REQUIRED
    }


def test_all_fields_missing_gives_four_messages(today):
    result = v.validate_expense({}, today)
    assert result.expense is None
    assert result.errors == {
        "amount": v.MSG_AMOUNT_REQUIRED,
        "category": v.MSG_CATEGORY_REQUIRED,
        "description": v.MSG_DESCRIPTION_REQUIRED,
        "expense_date": v.MSG_DATE_REQUIRED,
    }


def test_non_string_values_are_treated_as_missing(today):
    result = v.validate_expense(
        {"amount": None, "category": 5, "description": [], "expense_date": {}},
        today,
    )
    assert set(result.errors) == {"amount", "category", "description", "expense_date"}


@pytest.mark.parametrize(
    "message, word",
    [
        (v.MSG_AMOUNT_REQUIRED, "Amount"),
        (v.MSG_AMOUNT_INVALID, "Amount"),
        (v.MSG_AMOUNT_ZERO, "Amount"),
        (v.MSG_AMOUNT_DECIMALS, "Amount"),
        (v.MSG_AMOUNT_MAX, "Amount"),
        (v.MSG_CATEGORY_REQUIRED, "Category"),
        (v.MSG_CATEGORY_INVALID, "Category"),
        (v.MSG_DESCRIPTION_REQUIRED, "Description"),
        (v.MSG_DESCRIPTION_LONG, "Description"),
        (v.MSG_DATE_REQUIRED, "Expense date"),
        (v.MSG_DATE_INVALID, "Expense date"),
        (v.MSG_DATE_FUTURE, "Expense date"),
    ],
)
def test_messages_name_the_field(message, word):
    assert message.startswith(word)


def test_only_invalid_fields_are_reported(today):
    result = validate(today, amount="0", description="")
    assert set(result.errors) == {"amount", "description"}
