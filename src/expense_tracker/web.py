"""HTTP routes: list page, create, edit and delete flows."""

from flask import Blueprint, redirect, render_template, request, url_for

from expense_tracker.app import get_service
from expense_tracker.service import EMPTY_NO_MATCH
from expense_tracker.validation import CATEGORIES

bp = Blueprint("web", __name__)

# Whitelist only: the msg query value is looked up here, never echoed.
_FLASH_MESSAGES = {
    "created": "Expense added.",
    "updated": "Expense updated.",
    "deleted": "Expense deleted.",
}
_FILTER_KEYS = ("category", "start", "end")
_FORM_FIELDS = ("amount", "category", "description", "expense_date")


@bp.get("/")
def list_page():
    raw_filters = {key: request.args.get(key, "") for key in _FILTER_KEYS}
    result = get_service().list_expenses(raw_filters)
    return render_template(
        "list.html",
        result=result,
        filters=raw_filters,
        categories=CATEGORIES,
        flash_message=_FLASH_MESSAGES.get(request.args.get("msg", "")),
        no_match=result.empty_state == EMPTY_NO_MATCH,
    )


def _render_form(
    values: dict, errors: dict, status: int = 200, *, heading="Add expense", action=None
):
    return (
        render_template(
            "form.html",
            heading=heading,
            action=action or url_for("web.create"),
            values=values,
            errors=errors,
            categories=CATEGORIES,
        ),
        status,
    )


@bp.get("/expenses/new")
def new_form():
    return _render_form({}, {})


@bp.post("/expenses")
def create():
    values = {name: request.form.get(name, "") for name in _FORM_FIELDS}
    result = get_service().create(values)
    if not result.is_valid:
        return _render_form(values, result.errors, 400)
    return redirect(url_for("web.list_page", msg="created"), code=303)


def _edit_form(expense_id: int, values: dict, errors: dict, status: int = 200):
    return _render_form(
        values,
        errors,
        status,
        heading="Edit expense",
        action=url_for("web.update", expense_id=expense_id),
    )


@bp.get("/expenses/<int:expense_id>/edit")
def edit_form(expense_id: int):
    expense = get_service().get(expense_id)
    values = {
        "amount": expense.amount_display,
        "category": expense.category,
        "description": expense.description,
        "expense_date": expense.expense_date.isoformat(),
    }
    return _edit_form(expense_id, values, {})


@bp.post("/expenses/<int:expense_id>")
def update(expense_id: int):
    values = {name: request.form.get(name, "") for name in _FORM_FIELDS}
    result = get_service().update(expense_id, values)
    if not result.is_valid:
        return _edit_form(expense_id, values, result.errors, 400)
    return redirect(url_for("web.list_page", msg="updated"), code=303)


@bp.get("/expenses/<int:expense_id>/delete")
def delete_confirm(expense_id: int):
    expense = get_service().get(expense_id)
    return render_template(
        "confirm_delete.html",
        expense=expense,
        action=url_for("web.delete", expense_id=expense_id),
    )


@bp.post("/expenses/<int:expense_id>/delete")
def delete(expense_id: int):
    get_service().delete(expense_id)
    return redirect(url_for("web.list_page", msg="deleted"), code=303)
