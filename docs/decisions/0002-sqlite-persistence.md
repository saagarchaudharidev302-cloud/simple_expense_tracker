# 0002 Persistence with SQLite and integer minor-unit amounts

- Status: Accepted (G2 re-approved 2026-11-16, revision 2)
- Date: 2026-11-16
- Workflow: WF-EPMCDMETST-71369-20261116

## Context
Assumption 1: expenses persist between uses. REQ-020 and REQ-NFR-002 require that failed operations leave no inconsistent or corrupted records. REQ-021 requires exact 2-decimal amounts. Single user, small data.

## Options considered
1. **JSON file.** No engine, but whole-file rewrites risk corruption on crash and need custom atomic-write logic; filtering and ordering done by hand.
2. **SQLite via Python stdlib `sqlite3`.** Transactional and atomic, no extra dependency or server, SQL for filtering and ordering, parameterized queries.
3. **Client/server database (e.g. PostgreSQL).** Operational overhead with no requirement for it.

## Decision
Option 2. Amounts are stored as INTEGER minor units (amount x 100) to avoid binary floating-point error; the domain layer parses with `decimal.Decimal` and formats to 2 decimals. Dates are stored as TEXT `YYYY-MM-DD` (sorts and compares correctly as text). Database file path comes from configuration (`EXPENSE_DB_PATH` environment variable, default `data/expenses.db` under the project root); the file is git-ignored.

## Consequences
- Each write runs in a single transaction; on exception it rolls back (REQ-NFR-002). Update and delete return the affected-row count so a missing record is never reported as success (FND-007).
- One connection per request, closed at teardown; none shared across threads (FND-008).
- The category CHECK is generated from the single `CATEGORIES` constant (FND-010).
- No ORM and no migrations tool; schema is created idempotently at startup (`CREATE TABLE IF NOT EXISTS`).
- Tests use an in-memory or temporary database.
