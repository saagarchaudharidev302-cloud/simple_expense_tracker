from datetime import date
from urllib.parse import quote

import pytest

from expense_tracker.repository import ExpenseRepository
from expense_tracker.validation import CATEGORIES, ValidExpense


@pytest.fixture
def seed(db_path):
    def _seed(*rows):
        repo = ExpenseRepository(db_path)
        try:
            for amount_minor, category, description, day in rows:
                repo.insert(ValidExpense(amount_minor, category, description, day))
        finally:
            repo.close()

    return _seed


def body(client, url="/"):
    response = client.get(url)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_empty_list_shows_none_recorded(client):
    text = body(client)
    assert "No expenses recorded." in text
    assert "No expenses match the filters." not in text


def test_fields_shown(client, seed):
    seed((1250, "Food", "Lunch", date(2026, 6, 1)))
    text = body(client)
    for expected in ("12.50", "Food", "Lunch", "2026-06-01"):
        assert expected in text


def test_newest_first_with_tie_break(client, seed):
    seed(
        (100, "Food", "stale-row", date(2026, 6, 1)),
        (100, "Food", "tie-first-inserted", date(2026, 6, 5)),
        (100, "Food", "tie-last-inserted", date(2026, 6, 5)),
    )
    text = body(client)
    order = [text.index(n) for n in ("tie-last-inserted", "tie-first-inserted", "stale-row")]
    assert order == sorted(order)


@pytest.fixture
def mixed(seed):
    seed(
        (100, "Food", "food-early", date(2026, 5, 1)),
        (200, "Food", "food-mid", date(2026, 5, 15)),
        (300, "Transport", "transport-mid", date(2026, 5, 15)),
        (400, "Food", "food-late", date(2026, 5, 31)),
    )


ALL_NAMES = ("food-early", "food-mid", "transport-mid", "food-late")


def test_category_filter(client, mixed):
    text = body(client, "/?category=Transport")
    assert "transport-mid" in text
    assert "food-mid" not in text


def test_date_range_inclusive_bounds(client, mixed):
    text = body(client, "/?start=2026-05-15&end=2026-05-31")
    assert "food-early" not in text
    for name in ("food-mid", "transport-mid", "food-late"):
        assert name in text


def test_start_only_and_end_only(client, mixed):
    assert "food-early" not in body(client, "/?start=2026-05-02")
    assert "food-late" not in body(client, "/?end=2026-05-30")


def test_combined_filters(client, mixed):
    text = body(client, "/?category=Food&start=2026-05-10&end=2026-05-20")
    assert "food-mid" in text
    for name in ("food-early", "transport-mid", "food-late"):
        assert name not in text


def test_future_filter_dates_allowed(client, mixed):
    text = body(client, "/?start=2030-01-01")
    assert "No expenses match the filters." in text
    assert "must not be in the future" not in text


def test_inverted_range_message_and_no_bounds_applied(client, mixed):
    text = body(client, "/?start=2026-05-31&end=2026-05-01")
    assert "the date range was not applied" in text
    for name in ALL_NAMES:
        assert name in text


def test_invalid_filters_show_messages_and_are_ignored(client, mixed):
    text = body(client, "/?category=Bogus&start=nope&end=2026-13-45")
    assert "Category filter must be one of the listed categories." in text
    assert "Start date must be a valid date" in text
    assert "End date must be a valid date" in text
    for name in ALL_NAMES:
        assert name in text


def test_no_match_message_distinct_from_empty(client, mixed):
    text = body(client, "/?start=2026-01-01&end=2026-01-02")
    assert "No expenses match the filters." in text
    assert "No expenses recorded." not in text


def test_filter_form_redisplays_submitted_values(client, mixed):
    text = body(client, "/?category=Food&start=2026-05-01&end=2026-05-31")
    assert 'value="Food" selected' in text
    assert 'name="start" value="2026-05-01"' in text
    assert 'name="end" value="2026-05-31"' in text


def test_clear_filters_link_returns_all(client, mixed):
    text = body(client, "/?category=Transport")
    assert 'href="/">Clear filters</a>' in text
    cleared = body(client, "/")
    for name in ALL_NAMES:
        assert name in cleared


@pytest.mark.parametrize(
    "msg,expected",
    [("created", "Expense added."), ("updated", "Expense updated."), ("deleted", "Expense deleted.")],
)
def test_known_msg_values_show_message(client, msg, expected):
    assert expected in body(client, f"/?msg={msg}")


@pytest.mark.parametrize("msg", ["other", "CREATED", "<script>alert(1)</script>", "created x"])
def test_unknown_or_hostile_msg_ignored_and_not_reflected(client, msg):
    text = body(client, f"/?msg={quote(msg)}")
    for known in ("Expense added.", "Expense updated.", "Expense deleted."):
        assert known not in text
    assert msg not in text
    assert "alert(1)" not in text


def test_category_dropdown_lists_all_categories(client):
    text = body(client)
    for category in CATEGORIES:
        assert f'<option value="{category}"' in text


def test_record_id_not_visible_text(client, seed):
    seed(*[(100 + i, "Food", f"item-{i}", date(2026, 6, 1)) for i in range(3)])
    text = body(client)
    for record_id in (1, 2, 3):
        assert f">{record_id}<" not in text
    assert "ID" not in text


def test_description_is_escaped(client, seed):
    seed((100, "Food", "<b>x</b>", date(2026, 6, 1)))
    text = body(client)
    assert "<b>x</b>" not in text
    assert "&lt;b&gt;x&lt;/b&gt;" in text
