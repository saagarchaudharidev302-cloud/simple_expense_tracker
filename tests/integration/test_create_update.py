from html.parser import HTMLParser

import pytest

ORIGIN = {"Origin": "http://localhost"}
VALID = {
    "amount": "12.50",
    "category": "Food",
    "description": "Lunch",
    "expense_date": "2026-06-01",
}


def post_create(client, **overrides):
    return client.post("/expenses", data={**VALID, **overrides}, headers=ORIGIN)


def list_text(client):
    return client.get("/").get_data(as_text=True)


def test_new_form_shows_fields_and_categories(client):
    text = client.get("/expenses/new").get_data(as_text=True)
    for name in ("amount", "category", "description", "expense_date"):
        assert f'name="{name}"' in text
    assert '<option value="Transport"' in text


def test_create_success_redirects_and_shows_in_list_with_message(client):
    response = post_create(client)
    assert response.status_code == 303
    assert response.headers["Location"] == "/?msg=created"
    text = client.get(response.headers["Location"]).get_data(as_text=True)
    assert "Expense added." in text
    for expected in ("12.50", "Food", "Lunch", "2026-06-01"):
        assert expected in text


def test_create_trims_description_and_accepts_today(client, today):
    response = post_create(client, description="  Spaced  ", expense_date=today.isoformat())
    assert response.status_code == 303
    assert "Spaced" in list_text(client)


@pytest.mark.parametrize(
    "field,message",
    [
        ("amount", "Amount is required."),
        ("category", "Category is required."),
        ("description", "Description is required."),
        ("expense_date", "Expense date is required."),
    ],
)
def test_missing_field_message(client, field, message):
    response = post_create(client, **{field: ""})
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)
    assert "No expenses recorded." in list_text(client)


def test_whitespace_only_description_rejected(client):
    response = post_create(client, description="   ")
    assert response.status_code == 400
    assert "Description is required." in response.get_data(as_text=True)


@pytest.mark.parametrize(
    "amount,message",
    [
        ("abc", "Amount must be a number greater than zero."),
        ("-5", "Amount must be a number greater than zero."),
        ("0", "Amount must be greater than zero."),
        ("1.234", "Amount must have at most 2 decimal places."),
        ("1000000", "Amount must not exceed 999,999.99."),
    ],
)
def test_invalid_amount_messages(client, amount, message):
    response = post_create(client, amount=amount)
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)
    assert "No expenses recorded." in list_text(client)


def test_max_amount_accepted(client):
    assert post_create(client, amount="999999.99").status_code == 303


@pytest.mark.parametrize(
    "value,message",
    [
        ("2026-06-16", "Expense date must not be in the future."),
        ("2026-02-30", "Expense date must be a valid date in YYYY-MM-DD format."),
        ("06/01/2026", "Expense date must be a valid date in YYYY-MM-DD format."),
    ],
)
def test_invalid_date_messages(client, value, message):
    response = post_create(client, expense_date=value)
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)


def test_invalid_category_rejected(client):
    response = post_create(client, category="Bogus")
    assert response.status_code == 400
    assert "Category must be one of the listed categories." in response.get_data(as_text=True)


def test_description_length_boundary(client):
    assert post_create(client, description="a" * 200).status_code == 303
    response = post_create(client, description="a" * 201)
    assert response.status_code == 400
    assert "Description must be at most 200 characters." in response.get_data(as_text=True)


def test_invalid_create_preserves_entered_values_and_leaves_list_unchanged(client):
    response = post_create(client, amount="oops", description="Keep <me>")
    text = response.get_data(as_text=True)
    assert response.status_code == 400
    assert 'name="amount" value="oops"' in text
    assert 'name="description" value="Keep &lt;me&gt;"' in text
    assert 'value="Food" selected' in text
    assert 'name="expense_date" value="2026-06-01"' in text
    assert "No expenses recorded." in list_text(client)


def test_multiple_errors_reported_together(client):
    text = post_create(client, amount="", description="").get_data(as_text=True)
    assert "Amount is required." in text
    assert "Description is required." in text


def test_create_without_origin_is_forbidden_and_not_saved(client):
    response = client.post("/expenses", data=VALID)
    assert response.status_code == 403
    assert "No expenses recorded." in list_text(client)


def edit_url(expense_id=1):
    return f"/expenses/{expense_id}/edit"


def post_update(client, expense_id=1, **overrides):
    return client.post(
        f"/expenses/{expense_id}", data={**VALID, **overrides}, headers=ORIGIN
    )


def test_edit_form_prefilled_with_current_values(client):
    post_create(client)
    text = client.get(edit_url()).get_data(as_text=True)
    assert "Edit expense" in text
    assert 'value="12.50"' in text
    assert 'value="Lunch"' in text
    assert 'value="2026-06-01"' in text
    assert '<option value="Food" selected' in text
    assert 'action="/expenses/1"' in text


def test_update_success_reflected_in_list_with_message(client):
    post_create(client)
    response = post_update(
        client, amount="7.25", category="Transport", description="Bus", expense_date="2026-06-02"
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/?msg=updated"
    text = client.get(response.headers["Location"]).get_data(as_text=True)
    assert "Expense updated." in text
    for expected in ("7.25", "Transport", "Bus", "2026-06-02"):
        assert expected in text
    assert "Lunch" not in text
    assert text.count("<tr>") == 2  # header row plus the single expense


def test_invalid_update_not_saved_and_values_preserved(client):
    post_create(client)
    response = post_update(client, amount="abc", description="Changed")
    assert response.status_code == 400
    text = response.get_data(as_text=True)
    assert 'value="abc"' in text
    assert 'value="Changed"' in text
    assert 'class="error"' in text
    after = list_text(client)
    assert "12.50" in after
    assert "Lunch" in after
    assert "Changed" not in after


def test_invalid_update_future_date_not_saved(client):
    post_create(client)
    response = post_update(client, expense_date="2026-06-16")
    assert response.status_code == 400
    assert "2026-06-01" in list_text(client)


class _InputCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.inputs.append(dict(attrs))


def inputs_by_name(html):
    collector = _InputCollector()
    collector.feed(html)
    return {i.get("name"): i for i in collector.inputs}


def test_date_fields_render_as_native_date_inputs(client):
    form = inputs_by_name(client.get("/expenses/new").get_data(as_text=True))
    assert form["expense_date"]["type"] == "date"
    listing = inputs_by_name(list_text(client))
    assert listing["start"]["type"] == "date"
    assert listing["end"]["type"] == "date"


def test_edit_form_prefills_valid_date_value(client):
    post_create(client)
    form = inputs_by_name(client.get(edit_url()).get_data(as_text=True))
    assert form["expense_date"]["type"] == "date"
    assert form["expense_date"]["value"] == "2026-06-01"


def test_list_filters_prefill_valid_date_values(client):
    text = client.get("/?start=2026-05-01&end=2026-06-01").get_data(as_text=True)
    listing = inputs_by_name(text)
    assert listing["start"]["value"] == "2026-05-01"
    assert listing["end"]["value"] == "2026-06-01"


def test_hand_edited_date_text_still_fails_server_validation(client):
    response = post_create(client, expense_date="not-a-date")
    assert response.status_code == 400
    assert "Expense date must be a valid date in YYYY-MM-DD format." in response.get_data(as_text=True)
