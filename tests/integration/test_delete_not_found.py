ORIGIN = {"Origin": "http://localhost"}
VALID = {
    "amount": "12.50",
    "category": "Food",
    "description": "Lunch",
    "expense_date": "2026-06-01",
}


def create_one(client):
    client.post("/expenses", data=VALID, headers=ORIGIN)


def list_text(client):
    return client.get("/").get_data(as_text=True)


def test_list_has_edit_and_delete_links_without_visible_id(client):
    create_one(client)
    text = list_text(client)
    assert 'href="/expenses/1/edit"' in text
    assert 'href="/expenses/1/delete"' in text
    assert ">1<" not in text


def test_delete_confirmation_shown_and_get_does_not_delete(client):
    create_one(client)
    response = client.get("/expenses/1/delete")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Delete this expense?" in text
    assert "Lunch" in text
    assert 'method="post"' in text
    assert "Lunch" in list_text(client)


def test_confirm_deletes_and_shows_message(client):
    create_one(client)
    response = client.post("/expenses/1/delete", headers=ORIGIN)
    assert response.status_code == 303
    assert response.headers["Location"] == "/?msg=deleted"
    text = client.get(response.headers["Location"]).get_data(as_text=True)
    assert "Expense deleted." in text
    assert "Lunch" not in text
    assert "No expenses recorded." in text


def test_cancel_link_returns_to_list_and_keeps_record(client):
    create_one(client)
    text = client.get("/expenses/1/delete").get_data(as_text=True)
    assert '<a href="/">Cancel</a>' in text
    assert "Lunch" in list_text(client)


def test_unknown_id_get_edit_and_delete_return_404(client):
    for url in ("/expenses/99/edit", "/expenses/99/delete"):
        response = client.get(url)
        assert response.status_code == 404
        assert "Expense not found" in response.get_data(as_text=True)


def test_unknown_id_update_returns_404_and_changes_nothing(client):
    create_one(client)
    response = client.post("/expenses/99", data={**VALID, "description": "Zzchanged"}, headers=ORIGIN)
    assert response.status_code == 404
    assert "Expense not found" in response.get_data(as_text=True)
    text = list_text(client)
    assert "Lunch" in text
    assert "Zzchanged" not in text


def test_unknown_id_delete_returns_404_and_changes_nothing(client):
    create_one(client)
    response = client.post("/expenses/99/delete", headers=ORIGIN)
    assert response.status_code == 404
    assert "Expense not found" in response.get_data(as_text=True)
    assert "Lunch" in list_text(client)


def test_deleted_id_then_edit_is_404(client):
    create_one(client)
    client.post("/expenses/1/delete", headers=ORIGIN)
    assert client.get("/expenses/1/edit").status_code == 404
