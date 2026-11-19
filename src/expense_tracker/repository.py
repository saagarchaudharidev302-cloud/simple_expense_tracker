"""SQLite access only: schema, CRUD and the filtered, ordered list."""
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

from expense_tracker.validation import (
    CATEGORIES,
    MAX_AMOUNT_MINOR,
    FilterResult,
    ValidExpense,
)

# Category values come from the CATEGORIES constant, never from user input.
_CATEGORY_SQL = ", ".join(f"'{c}'" for c in CATEGORIES)

_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_minor INTEGER NOT NULL
        CHECK (amount_minor BETWEEN 1 AND {MAX_AMOUNT_MINOR}),
    category TEXT NOT NULL CHECK (category IN ({_CATEGORY_SQL})),
    description TEXT NOT NULL,
    expense_date TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_expense_date ON expenses (expense_date);
"""

_COLUMNS = "id, amount_minor, category, description, expense_date"


@dataclass(frozen=True)
class Expense:
    id: int
    amount_minor: int
    category: str
    description: str
    expense_date: date


def _to_expense(row: sqlite3.Row) -> Expense:
    return Expense(
        id=row["id"],
        amount_minor=row["amount_minor"],
        category=row["category"],
        description=row["description"],
        expense_date=date.fromisoformat(row["expense_date"]),
    )


class ExpenseRepository:
    """One instance per request: the connection is opened lazily and must be
    closed by the caller at request teardown. It is never shared across threads.
    """

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def _connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @contextmanager
    def _transaction(self):
        conn = self._connection()
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise

    def init_schema(self) -> None:
        with self._transaction() as conn:
            conn.executescript(_SCHEMA)

    def insert(self, expense: ValidExpense) -> int:
        with self._transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO expenses (amount_minor, category, description, expense_date)"
                " VALUES (?, ?, ?, ?)",
                (
                    expense.amount_minor,
                    expense.category,
                    expense.description,
                    expense.expense_date.isoformat(),
                ),
            )
            return cursor.lastrowid

    def update(self, expense_id: int, expense: ValidExpense) -> int:
        """Return the number of rows changed (0 when the id does not exist)."""
        with self._transaction() as conn:
            cursor = conn.execute(
                "UPDATE expenses SET amount_minor = ?, category = ?, description = ?,"
                " expense_date = ? WHERE id = ?",
                (
                    expense.amount_minor,
                    expense.category,
                    expense.description,
                    expense.expense_date.isoformat(),
                    expense_id,
                ),
            )
            return cursor.rowcount

    def delete(self, expense_id: int) -> int:
        """Return the number of rows deleted (0 when the id does not exist)."""
        with self._transaction() as conn:
            cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            return cursor.rowcount

    def get(self, expense_id: int) -> Expense | None:
        row = (
            self._connection()
            .execute(f"SELECT {_COLUMNS} FROM expenses WHERE id = ?", (expense_id,))
            .fetchone()
        )
        return _to_expense(row) if row else None

    def list_expenses(self, filters: FilterResult | None = None) -> list[Expense]:
        clauses: list[str] = []
        params: list[str] = []
        if filters is not None:
            if filters.category is not None:
                clauses.append("category = ?")
                params.append(filters.category)
            if filters.start is not None:
                clauses.append("expense_date >= ?")
                params.append(filters.start.isoformat())
            if filters.end is not None:
                clauses.append("expense_date <= ?")
                params.append(filters.end.isoformat())
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = (
            self._connection()
            .execute(
                f"SELECT {_COLUMNS} FROM expenses{where}"
                " ORDER BY expense_date DESC, id DESC",
                params,
            )
            .fetchall()
        )
        return [_to_expense(r) for r in rows]
