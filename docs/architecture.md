# Architecture

| Field | Value |
|-------|-------|
| Workflow ID | `WF-EPMCDMETST-71369-20261116` |
| Jira issue key | `EPMCDMETST-71369` |
| Author role | Architecture Agent |
| Date | 2026-11-16 |
| Status | Approved (revision 2) |

## 1. Overview and Goals

A single-user Personal Expense Tracker: create, list (newest expense date first), update, delete (with confirmation) and filter expenses by category and date range. Drivers: field-level validation and graceful errors (REQ-003, 004, 019, 021-024); data integrity on failure (REQ-020, REQ-NFR-002); no leakage of internals (REQ-NFR-001); persistence between uses (Assumption 1); unit and integration testability (REQ-NFR-004). No volume, performance or availability targets, so the simplest design is chosen.

## 2. Context

One local user operates the app through a browser. No external systems, no authentication (out of scope), one data set. The app listens on 127.0.0.1 only. Boundary: HTTP form input from the browser is untrusted; the SQLite file is the only stored state.

## 3. Technology Choices

| Area | Choice | Rationale | ADR |
|------|--------|-----------|-----|
| Language / runtime | Python 3 | Stdlib covers decimals, dates and SQLite; assumed team skill (no constraint given) | 0001 |
| Web | Flask + Jinja, server-rendered, no JavaScript | Forms, lists, confirmation page map directly to requirements; no SPA/build tooling | 0001 |
| Storage | SQLite (stdlib `sqlite3`), amounts as integer minor units | Atomic transactions satisfy REQ-020; no server; exact money | 0002 |
| Testing | pytest; Flask test client for integration | Meets REQ-NFR-004 | 0001 |
| Structure | Web / service / repository layers, injectable `today` | Unit-testable rules; deterministic tests | 0003 |

New dependencies (Flask, pytest) require user approval before installation. Versions are pinned exactly in a requirements file created by the plan/implementation; before the user is asked to approve installation, the pinned versions are checked against a vulnerability source (for example `pip-audit`) and the result is reported (security rules; FND-010).

## 4. Components

| Component | Responsibility | Depends on |
|-----------|----------------|------------|
| Web layer (routes, templates) | Parse form/query input, call service, render list/forms/confirmation page, show messages, map errors to generic pages, Origin check on POSTs | Service |
| Expense service | All business rules: validation (REQ-003/004/021/022/023/024), category list, filter semantics, existence checks, result/error types | Repository, `today` provider |
| Repository | SQL access only: insert, update, delete, get by id, list with optional filters and fixed ordering; one transaction per write; schema creation | SQLite |
| Config / app factory | Create the app, read DB path from environment, wire components, register error handlers and the Host/Origin check | all |
| Launcher (module entry point, e.g. `python -m <package>`) | Start the server with host fixed to `127.0.0.1` and debug off, hard-coded (not configurable by environment) | App factory |

Connection lifecycle: one SQLite connection per request, opened lazily and closed at request teardown; no connection is shared between threads (the Flask dev server is threaded). Schema creation runs once at startup. Default DB path is `data/expenses.db` under the project root (git-ignored), overridable by the `EXPENSE_DB_PATH` environment variable (FND-008).

## 5. Data Model

Table `expenses`:

| Column | Type | Rules |
|--------|------|-------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique (REQ-016); never rendered as text; used only in URLs/hidden form fields |
| amount_minor | INTEGER NOT NULL | CHECK 1..99999999 (0.01 to 999,999.99) |
| category | TEXT NOT NULL | One of Food, Transport, Housing, Utilities, Entertainment, Health, Shopping, Other. Single source: one `CATEGORIES` constant; the service validates against it and the schema CHECK is generated from the same constant (a test asserts the created schema accepts exactly those values) (FND-010) |
| description | TEXT NOT NULL | 1..200 characters after trimming (whitespace-only is missing, Assumption 6) |
| expense_date | TEXT NOT NULL | Exact `YYYY-MM-DD`, valid calendar date, not after today |

Index on `expense_date`. Categories are a constant in code, not a table (not user-editable, REQ-018).

Ordering (all lists): `ORDER BY expense_date DESC, id DESC` (ADR 0003). Filter: `category = ?`, `expense_date >= ?`, `expense_date <= ?`, each applied only when supplied (inclusive, optional bounds); all via bound parameters.

Amount parsing (FND-003): trim surrounding whitespace, then require the grammar `^[0-9]+(\.[0-9]+)?$` (ASCII digits, optional single decimal point with at least one digit after it; max 20 characters before parsing). Anything else (signs, exponent, underscores, commas, NaN/Infinity, empty, `.5`, `5.`) is rejected with the "amount must be a number greater than zero" message. A matching value is parsed with `Decimal` and then rejected if <= 0, if it has more than 2 decimal places (trailing zeros count: `1.500` is rejected, `1.50` accepted), or if > 999999.99. Display as `0.00` format with no currency symbol (REQ-007).

Date parsing (FND-004): the text must match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` exactly (no trimming of inner content, no compact or non-padded forms such as `2026-1-5` or `20260105`), then be a real calendar date (`date.fromisoformat` on the matched text), and not after `today`. The same strict parser is used for the filter `start` and `end` values.

## 6. Interfaces

Server-rendered HTML; no public JSON API (Not applicable: no integration need).

| Method and path | Purpose |
|-----------------|---------|
| GET `/` | Expense list; query params `category`, `start`, `end`; "Clear filters" links to `/` |
| GET `/expenses/new`, POST `/expenses` | Create form; submit |
| GET `/expenses/<id>/edit`, POST `/expenses/<id>` | Update form; submit |
| GET `/expenses/<id>/delete` | Confirmation page (Confirm submits POST; Cancel links to `/`) |
| POST `/expenses/<id>/delete` | Delete after confirmation |

Behaviour: invalid input re-renders the form (HTTP 400) with a per-field message and the user's entered values; no record changes. Success redirects (Post/Redirect/Get) to `/?msg=<code>` where `code` is one of a fixed whitelist (`created`, `updated`, `deleted`) mapped to fixed texts, so no user input is reflected. Any other `msg` value is ignored: no message is shown and the page renders normally (FND-006). Unknown id on edit/update/delete returns a 404 page with a generic message "Expense not found" and changes nothing (REQ-017); this includes a record that vanishes between the existence check and the write (FND-007).

Invalid filter handling (FND-002, REQ-024): each filter is validated independently and the list always renders (HTTP 200) with a validation message per invalid filter. Invalid or unknown `category` is not applied. A malformed `start` or `end` is not applied. If both dates are individually valid but start is after end, neither date bound is applied. Any remaining valid filters are still applied (for example a valid category with an inverted range lists that category across all dates). The filter form re-displays the user's submitted values. The empty-state text "No expenses match the filters" is shown only when at least one valid filter was applied and nothing matched; "No expenses recorded" is shown when no valid filter was applied and the table is empty. If no valid filter was applied and expenses exist, the full list is shown.

Unexpected exceptions return a generic 500 page ("Something went wrong"); see section 8 for what is logged.

## 7. Key Flows

- **Create:** form POST -> web trims/passes strings -> service validates all fields, collecting all errors -> if errors, re-render with messages; else repository INSERT in one transaction -> redirect `/?msg=created`.
- **Update:** same validation; service first checks the expense exists; repository UPDATE in a transaction. The repository returns the affected-row count; 0 rows is mapped by the service to "not found" (404), never to success (FND-007).
- **Delete:** GET confirmation page (404 if missing) -> POST deletes (repository returns affected-row count; 0 maps to 404) -> redirect `/?msg=deleted`; Cancel navigates away with no write.
- **List/filter:** service validates filters, repository queries with fixed ordering; empty result shows "No expenses recorded" when no filter is applied, or "No expenses match the filters" when a valid filter is applied (REQ-009 vs REQ-025).

## 8. Cross-Cutting Concerns

- **Security:** localhost bind only; no auth (out of scope). Server-side validation of every field at the boundary; parameterized SQL only; Jinja autoescaping on; no secrets exist; DB path from environment, DB file git-ignored. Request checks (FND-005), applied to every request in a `before_request` hook: (1) the `Host` header must be one of `127.0.0.1:<port>` or `localhost:<port>` (DNS-rebinding defence), otherwise a generic 400; (2) for POST, if an `Origin` header is present its host:port must equal the `Host` header; if `Origin` is absent, the `Referer` host:port must equal `Host`; if both are absent, or a present one mismatches, the POST is rejected with a generic 403 and nothing is changed. The 403/400 pages do not echo header values.
- **Error handling:** service returns structured field errors for expected failures; repository wraps writes in a transaction with rollback on any exception; global handlers for 404/500 return generic pages (REQ-NFR-001). A catch-all `Exception` handler is registered so the framework does not log tracebacks itself. Debug mode is off, fixed by the launcher.
- **Logging / observability (FND-001, REQ-NFR-001 applied literally to logs):** standard `logging`. Each failure log entry contains only the operation type (for example `create`, `update`, `delete`, `list`, `startup`) and the exception class name (for example `OperationalError`). Logs never contain stack traces (`exc_info` is not used), file paths, exception message text (including raw `sqlite3` messages, which may carry the DB path), request values, descriptions or amounts. The web server's access log (method, request path and query, status) is permitted; it contains no internals. No metrics (no requirement). Trade-off: diagnosing a fault relies on operation and class only; deeper debugging requires a developer to reproduce locally (ADR 0004).
- **Testability:** unit tests on the service (every validation rule and boundary: 0.01, 999999.99, 1000000.00, 3 decimals, `1.500`, `1e2`, `1_0`, ` 5 `, `-1`, `.5`, `5.`, today/future date, `2026-1-5`, `20260105`, `2026-02-30`, 200/201 chars, whitespace description, inverted range, filter combinations including one invalid plus one valid, tie-break order) with a fake `today`; repository tests against temporary SQLite (rollback on failure leaves data unchanged, ordering, affected-row count 0 for missing id, ids unique and not reused across inserts for REQ-016, schema CHECK matches `CATEGORIES`); integration tests via Flask test client for create/list/update/delete-confirm/cancel/filter/clear/not-found/error-page workflows, plus: unknown and hostile `msg` values show no message and reflect nothing, POST with mismatching Origin, with no Origin/Referer, and with a bad Host is rejected and changes nothing, rendered pages do not contain the record id as visible text (REQ-016), and a forced repository exception yields the generic 500 page and a log record that contains no traceback, path or exception text (captured with `caplog`). Maps to REQ-NFR-004.

## 9. Requirement Coverage

| Requirement | Addressed by |
|-------------|--------------|
| REQ-001, 002 | Web (create form), Service, Repository |
| REQ-003, 004, 019, REQ-NFR-003 | Service validation; Web renders per-field messages |
| REQ-005, 026 | Web (`msg` whitelist) |
| REQ-006, 007 | Web list template, Repository list; amount formatted by Service |
| REQ-008 | Repository fixed ordering (ADR 0003) |
| REQ-009, 025 | Web list template (two distinct empty states) |
| REQ-010 | Web edit form, Service, Repository update |
| REQ-011 | Web confirmation page and POST delete |
| REQ-012, 013, 014 | Service filter validation, Repository filter query |
| REQ-015 | Web "Clear filters" link to `/` |
| REQ-016 | Repository (`id` autoincrement), Web (never rendered) |
| REQ-017 | Service existence check, Web 404 handler |
| REQ-018 | Service category constant, Web select/filter dropdown |
| REQ-020, REQ-NFR-002 | Repository transactions with rollback; validation before write |
| REQ-021, 022, 023 | Service validation (Decimal, date parser with injectable today, length) |
| REQ-024 | Service filter validation |
| REQ-NFR-001 | Web global error handlers, logging policy (operation and error class only; ADR 0004) |
| REQ-NFR-004 | Test strategy (section 8) |

## 10. Risks and Trade-offs

| # | Risk / Trade-off | Mitigation |
|---|------------------|------------|
| 1 | Flask/pytest installation needs approval; language is an assumption | Ask at G2; fallback is a stdlib-only CLI (ADR 0001) |
| 2 | Time zone ambiguity near midnight for the future-date check (Assumption 5) | Documented; injectable clock in tests |
| 3 | CSRF / DNS rebinding on a local unauthenticated app | Localhost bind, Host allowlist, strict Origin/Referer check (missing both rejected) |
| 4 | Integer `id` in URLs is guessable and visible in the address bar (FND-011, Info) | Acceptable: single-user, no authz boundary; REQ-016 only requires that the id is not shown in the page content |
| 6 | Minimal logs limit diagnosability (FND-001) | Accepted by user choice to apply REQ-NFR-001 literally; operation and error class remain |
| 5 | Concurrent writers to SQLite | Single-user; SQLite locking plus transactions is sufficient |

## 11. Decision Records

- `docs/decisions/0001-platform-and-stack.md`
- `docs/decisions/0002-sqlite-persistence.md`
- `docs/decisions/0003-layering-ordering-and-validation.md`
- `docs/decisions/0004-log-content-policy.md`
- `docs/decisions/0005-ui-styling-and-date-input.md` (amendment A1, Accepted)

## Amendment A1 (2026-11-17, Accepted by user choice "Short amendment, no gate reopen (Recommended)"): UI styling and native date input

Covers user change requests CR-001 and CR-002, already implemented; no approved decision above is altered (ADR 0005).

- **Styling (CR-001):** one hand-written stylesheet, `src/expense_tracker/static/style.css`, served by Flask's default static route and linked from `base.html` and the standalone `error.html`. No CDN, JavaScript or new dependencies. Static requests fall under the existing Host check (section 8) and are not logged by the application (ADR 0004). Teal accent; goal of WCAG AA contrast for text and the focus ring.
- **Date input (CR-002):** the `expense_date` field and the `start`/`end` filters use `type="date"` for a browser calendar. Server-side `YYYY-MM-DD` fullmatch validation (section 5) is unchanged and authoritative.
- **Known limitation (FND-023, accepted):** a hand-edited non-ISO value is dropped by the browser on re-render, so the field shows empty while the server still reports the error.

## Open Questions / Assumptions

- Assumption A1: Python 3 + Flask is acceptable (no language/hosting constraint supplied). Impact: stack change affects ADR 0001 and everything downstream.
- Assumption A2: A local browser-based interface is acceptable as the platform (Q11 left open). Impact: a CLI alternative is available.
- Assumption A3: server local date is "today" (Assumption 5 of requirements).
- No blocking open questions.
