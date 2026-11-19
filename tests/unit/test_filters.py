from datetime import date

import pytest

from expense_tracker import validation as v


def test_no_filters():
    result = v.validate_filters({})
    assert not result.applied
    assert result.messages == {}


def test_empty_strings_are_no_filters():
    result = v.validate_filters({"category": "", "start": "", "end": ""})
    assert not result.applied
    assert result.messages == {}


def test_category_only():
    result = v.validate_filters({"category": "Food"})
    assert result.category == "Food"
    assert result.applied


def test_start_only():
    result = v.validate_filters({"start": "2026-01-05"})
    assert (result.start, result.end) == (date(2026, 1, 5), None)
    assert result.applied


def test_end_only():
    result = v.validate_filters({"end": "2026-01-05"})
    assert (result.start, result.end) == (None, date(2026, 1, 5))
    assert result.applied


def test_both_bounds():
    result = v.validate_filters({"start": "2026-01-01", "end": "2026-01-31"})
    assert (result.start, result.end) == (date(2026, 1, 1), date(2026, 1, 31))
    assert result.messages == {}


def test_category_and_range():
    result = v.validate_filters(
        {"category": "Health", "start": "2026-01-01", "end": "2026-01-31"}
    )
    assert result.category == "Health"
    assert result.start == date(2026, 1, 1)
    assert result.end == date(2026, 1, 31)


def test_equal_start_and_end_accepted():
    result = v.validate_filters({"start": "2026-01-05", "end": "2026-01-05"})
    assert result.start == result.end == date(2026, 1, 5)
    assert result.messages == {}


def test_malformed_start_not_applied():
    result = v.validate_filters({"start": "2026-1-5"})
    assert result.start is None
    assert result.messages == {"start": v.MSG_FILTER_START}
    assert not result.applied


def test_malformed_end_not_applied():
    result = v.validate_filters({"end": "nope"})
    assert result.end is None
    assert result.messages == {"end": v.MSG_FILTER_END}


def test_unknown_category_not_applied():
    result = v.validate_filters({"category": "Travel"})
    assert result.category is None
    assert result.messages == {"category": v.MSG_FILTER_CATEGORY}
    assert not result.applied


def test_inverted_range_applies_neither_bound():
    result = v.validate_filters({"start": "2026-02-01", "end": "2026-01-01"})
    assert result.start is None and result.end is None
    assert result.messages == {"range": v.MSG_FILTER_RANGE}
    assert not result.applied


def test_inverted_range_still_applies_category():
    result = v.validate_filters(
        {"category": "Food", "start": "2026-02-01", "end": "2026-01-01"}
    )
    assert result.category == "Food"
    assert result.start is None and result.end is None
    assert result.messages == {"range": v.MSG_FILTER_RANGE}
    assert result.applied


def test_one_invalid_one_valid_filter():
    result = v.validate_filters({"category": "Travel", "start": "2026-01-01"})
    assert result.category is None
    assert result.start == date(2026, 1, 1)
    assert result.messages == {"category": v.MSG_FILTER_CATEGORY}
    assert result.applied


def test_invalid_start_with_valid_end_keeps_end():
    result = v.validate_filters({"start": "bad", "end": "2026-01-31"})
    assert result.start is None
    assert result.end == date(2026, 1, 31)
    assert "range" not in result.messages


@pytest.mark.parametrize("key", ["start", "end"])
def test_trailing_newline_date_rejected(key):
    result = v.validate_filters({key: "2026-01-05\n"})
    assert getattr(result, key) is None
    assert key in result.messages


@pytest.mark.parametrize("key", ["start", "end"])
def test_impossible_calendar_date_rejected(key):
    result = v.validate_filters({key: "2026-02-30"})
    assert getattr(result, key) is None
    assert key in result.messages


def test_future_dates_are_allowed(today):
    future_start = date(today.year + 1, 1, 1)
    future_end = date(today.year + 1, 12, 31)
    result = v.validate_filters(
        {"start": future_start.isoformat(), "end": future_end.isoformat()}
    )
    assert (result.start, result.end) == (future_start, future_end)
    assert result.messages == {}
    assert result.applied


def test_non_string_values_ignored():
    result = v.validate_filters({"category": None, "start": 5, "end": []})
    assert not result.applied
    assert result.messages == {}
