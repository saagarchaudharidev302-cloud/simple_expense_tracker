# Implementation Plan

| Field | Value |
|-------|-------|
| Workflow ID | `WF-EPMCDMETST-71369-20261116` |
| Jira issue key | `EPMCDMETST-71369` |
| Author role | Planning Agent |
| Date | 2026-11-16 |
| Status | Draft (revision 2) |

## 0. User clarifications applied (2026-11-16, verbatim choices)

- **Host port (Q-1 resolved):** "Request's server port (Recommended)". Accept `127.0.0.1` or `localhost` with whatever port the server is actually listening on; no fixed port constant; tests work with the Flask test client. This is a user clarification of architecture section 8 (Host check); the architecture is not edited.
- **Filter date bounds:** "Allow future (Recommended)". Filters need only valid `YYYY-MM-DD` calendar dates; a future range simply matches nothing. (Create/update still reject future dates.)
- **Package:** "Yes (Recommended)". `src/expense_tracker/`, run with `python -m expense_tracker`.
- **Installs:** "Approve Flask, pytest, pip-audit". TASK-001 may pin exact versions and install all three; audit results for Flask and pytest are reported before app dependencies are installed.

## 1. Approach

Greenfield (no `src/` or `tests/` exist). Stack per ADR 0001-0004: Python 3, Flask + Jinja (server-rendered), stdlib `sqlite3`, pytest, Flask test client. Order: dependency approval and scaffolding, then the pure service rules (validation, filters), then the repository, then the web layer in vertical slices (list/filter, create, update, delete), then launcher and docs. Each implementation task is followed by its test task so feedback is early. Layers are web -> service -> repository (ADR 0003); `today` is injected.

Layout (package name confirmed by user): `src/expense_tracker/` with `service.py`, `validation.py`, `repository.py`, `app.py` (factory, config, handlers, request checks), `web.py` (routes), `__main__.py` (launcher), `templates/`. Tests in `tests/unit/`, `tests/integration/`, shared fixtures in `tests/conftest.py`.

Acceptance criteria are AC-001..AC-016 in the order of section 5 of `docs/user-story.md`, as used in `docs/requirements.md` section 8.

Review findings folded in: FND-012 (full-string regex match, trailing-newline tests: TASK-003, 004, 005, 006), FND-013 (HTTP errors keep their status; startup failures logged under policy: TASK-011, 013), FND-014 (Host port: TASK-012, resolved by user clarification, no fixed port), FND-015 Info (no action).

## 2. Tasks

| ID | Task | Depends on | Requirement(s) | AC | Size |
|----|------|------------|----------------|----|------|
| TASK-001 | Dependency approval, version pinning, vulnerability check (needs user approval to install) | - | REQ-NFR-004 | DoD | S |
| TASK-002 | Project scaffolding, pytest config, fixtures, `.gitignore` entry for `data/` | TASK-001 | REQ-NFR-004 | DoD | S |
| TASK-003 | Validation module: `CATEGORIES`, amount/date/description/category rules, result types | TASK-002 | REQ-002, 003, 004, 018, 019, 021, 022, 023, NFR-003 | AC-002, 003, 004, 016 | M |
| TASK-004 | Unit tests for validation rules | TASK-003 | same as TASK-003 | AC-002, 003, 004, 016 | M |
| TASK-005 | Filter validation (category, start, end, inverted range, independent handling) | TASK-003 | REQ-012, 013, 014, 024 | AC-012 | S |
| TASK-006 | Unit tests for filter validation | TASK-005 | REQ-012, 013, 014, 024 | AC-012 | S |
| TASK-007 | Repository: schema (CHECK from `CATEGORIES`), per-request connection, CRUD, filtered ordered list, transactions, affected-row counts | TASK-003 | REQ-016, 020, 008, NFR-002 | AC-008, 014, 016 | M |
| TASK-008 | Repository tests against temporary SQLite | TASK-007 | REQ-008, 016, 020, NFR-002 | AC-008, 014, 015, 016 | M |
| TASK-009 | Expense service: create/update/delete/get/list orchestration, existence checks, 0-row -> not found, amount display formatting, empty-state decision, injectable `today` | TASK-005, TASK-007 | REQ-001, 006, 007, 009, 010, 011, 017, 025 | AC-001, 006, 007, 009, 010, 011, 015 | M |
| TASK-010 | Service unit tests (fake `today`, temporary SQLite or fake repository) | TASK-009 | as TASK-009 | as TASK-009 | M |
| TASK-011 | App factory/config (`EXPENSE_DB_PATH`, default `data/expenses.db`), startup schema creation, generic 404/400/403/500 handlers, catch-all that preserves HTTP error status, logging per ADR 0004 (operation + class only, incl. `startup`) | TASK-007, TASK-009 | REQ-NFR-001, 019, 020 | AC-015, 016 | M |
| TASK-012 | Request checks `before_request`: Host allowlist (any port the server is listening on) and POST Origin/Referer rule | TASK-011 | REQ-NFR-001, NFR-002 | AC-016 | S |
| TASK-013 | Integration tests: error handling, logging policy, request checks | TASK-011, TASK-012 | REQ-NFR-001, NFR-002, 020 | AC-015, 016 | M |
| TASK-014 | List page + filter form + Clear filters + `msg` whitelist + two empty states + base template | TASK-011, TASK-009 | REQ-005, 006, 007, 008, 009, 012-015, 018, 024, 025, 026 | AC-005, 006, 007, 008, 009, 012, 013 | M |
| TASK-015 | Create form, POST `/expenses`, per-field errors with entered values, 400 on invalid, PRG redirect | TASK-014 | REQ-001-005, 021-023 | AC-001-005, 016 | M |
| TASK-016 | Edit form and POST update (404 if missing, same validation, success message) | TASK-015 | REQ-010, 017, 026 | AC-010, 015 | M |
| TASK-017 | Delete confirmation page, POST delete, Cancel link, 404 if missing | TASK-014 | REQ-011, 017, 026 | AC-011, 015 | S |
| TASK-018 | Integration tests: list, filter, clear, ordering, empty states, msg whitelist, no visible id | TASK-014 | REQ-006-009, 012-016, 024, 025 | AC-006-009, 012, 013, 014 | M |
| TASK-019 | Integration tests: create and update workflows incl. validation failures and unchanged data | TASK-015, TASK-016 | REQ-001-005, 010, 019-023, 026 | AC-001-005, 010, 016 | M |
| TASK-020 | Integration tests: delete confirm/cancel, not-found update/delete | TASK-017, TASK-016 | REQ-011, 017, 026 | AC-011, 015 | S |
| TASK-021 | Launcher `python -m expense_tracker`: host fixed 127.0.0.1, debug off, not environment-configurable | TASK-012 | REQ-NFR-001 | AC-016 | S |
| TASK-022 | README: setup, run, test commands, env var, category list, known limitations | TASK-021 | DoD (documentation) | DoD | S |
| TASK-023 | Full test run, AC-to-test cross-check, lint/format with stack-native tooling already approved (none added) | all | REQ-NFR-004 | DoD | S |

No dependency cycles. TASK-001 can start immediately.

### Task details

#### TASK-001 (install approved by user 2026-11-16: "Approve Flask, pytest, pip-audit")
- **Description:** Choose exact versions of Flask, pytest and pip-audit. Run pip-audit on the pinned Flask and pytest sets and report the results before installing app dependencies; stop and report if a vulnerability is found. Create pinned `requirements.txt` (Flask) and `requirements-dev.txt` (pytest, pip-audit). Install all three. Nothing beyond these three (and their transitive dependencies) is installed.
- **Files:** `requirements.txt`, `requirements-dev.txt`
- **Done when:** versions pinned exactly; audit results reported before app install; installs succeed.

#### TASK-002
- **Description:** Create package skeleton, `tests/unit`, `tests/integration`, `tests/conftest.py` (temp DB path fixture, fixed-`today` fixture, app/test client fixture setting a valid Host per FND-014), `pytest.ini` or equivalent, add `data/` to `.gitignore`.
- **Files:** `src/expense_tracker/__init__.py`, `tests/conftest.py`, `pytest.ini`, `.gitignore`
- **Done when:** `pytest` runs and collects zero failures on an empty suite; `data/` is ignored.

#### TASK-003
- **Description:** `CATEGORIES` single constant. Amount: trim, full-string match of `[0-9]+(\.[0-9]+)?` (use full-match semantics, not `$`, to reject trailing newline, FND-012), max 20 chars, `Decimal`, reject <=0, >2 decimals (trailing zeros count), >999999.99; convert to minor units. Date: full-match `YYYY-MM-DD`, real calendar date, not after `today`. Description: trim, 1..200 chars. Category in `CATEGORIES`. Collect all field errors with field-specific messages. Signatures only, e.g. `validate_expense(raw: dict, today: date) -> ValidationResult`.
- **Files:** `src/expense_tracker/validation.py`
- **Done when:** TASK-004 passes.

#### TASK-004
- **Description:** Tests: amount 0.01, 999999.99 accepted; 1000000.00, 0, 0.00, -1, `1.500`, 3 decimals, `1e2`, `1_0`, `.5`, `5.`, empty, NaN, Infinity, ` 5 ` (accepted after trim), `5\n` inner/trailing handling per rule; dates today ok, tomorrow rejected, `2026-1-5`, `20260105`, `2026-02-30`, `2026-01-05\n` rejected; description 200 ok/201 rejected/whitespace-only missing; unknown category; all four fields missing yields four messages; each message names the field; `CATEGORIES` has exactly the eight required values.
- **Files:** `tests/unit/test_validation.py`
- **Done when:** tests pass; each listed boundary is a distinct test case.

#### TASK-005
- **Description:** Validate `category`, `start`, `end` independently with the strict date parser's format and calendar check only. Future dates are allowed for filters (user clarification); do not apply the "not after today" rule. Inverted range: apply neither bound, produce message. Return applied filters, per-filter messages, and "valid filter applied" flag.
- **Files:** `src/expense_tracker/validation.py` (or `filters.py`)
- **Done when:** TASK-006 passes.

#### TASK-006
- **Description:** Tests: category only, start only, end only, both inclusive, category + range, malformed start, unknown category, inverted range (neither applied, category still applied), one invalid plus one valid, `2026-01-05\n` rejected, equal start and end accepted, future start/end (relative to injected `today`) accepted and applied, `2026-02-30` rejected.
- **Files:** `tests/unit/test_filters.py`
- **Done when:** tests pass.

#### TASK-007
- **Description:** `init_schema` (CHECK for amount range, category generated from `CATEGORIES`, index on `expense_date`), connection opened lazily per request and closed at teardown, `insert`, `update`, `delete` (return affected rows), `get`, `list(filters)` with `ORDER BY expense_date DESC, id DESC`, bound parameters only, one transaction per write with rollback on any exception.
- **Files:** `src/expense_tracker/repository.py`
- **Done when:** TASK-008 passes.

#### TASK-008
- **Description:** Tests on temporary SQLite: ordering and tie-break by id desc; filter combos with inclusive bounds; rollback leaves data unchanged on forced failure; 0 affected rows for missing id on update and delete; ids unique and not reused after delete (AUTOINCREMENT); schema accepts exactly `CATEGORIES`, rejects amount 0 and 100000000.
- **Files:** `tests/unit/test_repository.py`
- **Done when:** tests pass.

#### TASK-009
- **Description:** Service methods composing validation and repository; get/update/delete return not-found when missing or when affected rows is 0 (race, FND-007); list returns rows, applied-filter flag, filter messages; format amount as `0.00` with no currency symbol.
- **Files:** `src/expense_tracker/service.py`
- **Done when:** TASK-010 passes.

#### TASK-010
- **Description:** Tests: create stores values; invalid create/update changes nothing; update existing/missing; delete existing/missing; vanishing record between check and write maps to not found; amount display `1.50`, `1000.00`; empty-state decision for no filter vs valid filter matching nothing vs inverted range only.
- **Files:** `tests/unit/test_service.py`
- **Done when:** tests pass.

#### TASK-011
- **Description:** App factory reading `EXPENSE_DB_PATH`; schema creation at startup wrapped so failure is logged as `startup` with class name only and no traceback or message (FND-013); handlers for 400/403/404/500; catch-all `Exception` handler must return HTTP exceptions with their own status and generic page (do not convert to 500, and do not log them as failures); failure logs: operation and class only, no `exc_info`.
- **Files:** `src/expense_tracker/app.py`, `src/expense_tracker/templates/error.html`
- **Done when:** TASK-013 error and logging tests pass.

#### TASK-012
- **Description:** `before_request` Host check: hostname must be `127.0.0.1` or `localhost`, with whatever port the server is actually listening on (taken from the request/WSGI environment, no fixed port constant); otherwise generic 400. POST Origin/Referer rule (Origin host:port equals Host; else Referer; both absent or mismatched gives generic 403, header values not echoed). Must work with the Flask test client without configuring a port.
- **Files:** `src/expense_tracker/app.py`
- **Done when:** TASK-013 request-check tests pass.

#### TASK-013
- **Description:** Tests: forced repository exception gives generic 500 page and a `caplog` record with only operation and class name (no traceback, path, message text); 404 returns 404 and produces no failure log (FND-013); startup failure logged with policy; bad Host rejected with 400; POST with mismatching Origin, no Origin/Referer rejected with 403 and data unchanged; matching Origin accepted; error pages do not echo headers. Test client uses a valid Host so the real check runs (FND-014); also `localhost` and `127.0.0.1` accepted with an arbitrary port, other hostnames rejected.
- **Files:** `tests/integration/test_errors_and_security.py`
- **Done when:** tests pass.

#### TASK-014
- **Description:** `GET /` with `category`, `start`, `end`; table showing amount, category, description, date (no id text); category dropdown from `CATEGORIES`; filter form re-displays submitted values; Clear filters link to `/`; per-filter messages; `msg` whitelist (`created`, `updated`, `deleted`), unknown values ignored and never reflected; "No expenses recorded" vs "No expenses match the filters".
- **Files:** `src/expense_tracker/web.py`, `templates/base.html`, `templates/list.html`
- **Done when:** TASK-018 passes.

#### TASK-015
- **Description:** `GET /expenses/new`, `POST /expenses`; invalid gives HTTP 400 re-render with per-field messages and entered values; success redirects to `/?msg=created`. Ids appear only in URLs/hidden fields.
- **Files:** `web.py`, `templates/form.html`
- **Done when:** TASK-019 create tests pass.

#### TASK-016
- **Description:** `GET /expenses/<id>/edit`, `POST /expenses/<id>`; 404 for missing; invalid gives 400 with values kept; success redirects to `/?msg=updated`.
- **Files:** `web.py`, `templates/form.html`
- **Done when:** TASK-019 update tests and TASK-020 pass.

#### TASK-017
- **Description:** `GET /expenses/<id>/delete` confirmation (404 if missing), `POST` delete redirecting `/?msg=deleted`, Cancel link to `/`.
- **Files:** `web.py`, `templates/confirm_delete.html`
- **Done when:** TASK-020 passes.

#### TASK-018
- **Description:** Tests: list newest first with tie-break; fields shown; no-expenses message; each filter type, combined, inclusive bounds; inverted range message with neither bound applied; no-match message distinct from empty; Clear filters link returns all; unknown/hostile `msg` shows nothing and reflects nothing; page text does not contain record id as visible text; AC-014 (distinct ids via repository tests cross-referenced).
- **Files:** `tests/integration/test_list_filter.py`
- **Done when:** tests pass.

#### TASK-019
- **Description:** Tests: create success and message; each missing field message; invalid amount messages; future/incorrect date; 201-char description; invalid create leaves list unchanged; update success reflected in list with message; invalid update not saved, values preserved.
- **Files:** `tests/integration/test_create_update.py`
- **Done when:** tests pass.

#### TASK-020
- **Description:** Tests: confirmation page shown (no deletion on GET); confirm deletes and shows message; cancel link leaves record; edit/update/delete of unknown id return 404 with "Expense not found" and change nothing.
- **Files:** `tests/integration/test_delete_not_found.py`
- **Done when:** tests pass.

#### TASK-021
- **Description:** `__main__` starting the app on `127.0.0.1` with debug off, hard-coded. Port is the normal server default or a launcher argument; no port constant is shared with the Host check. Small test asserting the launcher settings (without starting a long-running server).
- **Files:** `src/expense_tracker/__main__.py`, `tests/unit/test_launcher.py`
- **Done when:** test passes; manual start observed in verification.

#### TASK-022
- **Description:** README with install, run, test, env var, categories, privacy/logging policy note, known limitations (time zone, minimal logs).
- **Files:** `README.md`
- **Done when:** commands in README were run as written.

#### TASK-023
- **Description:** Run the full suite, report exact commands and counts, confirm every AC row in section 4 has a passing test.
- **Done when:** all tests pass; report states counts.

## 3. Test Plan

| Test | Level | Covers | Location |
|------|-------|--------|----------|
| Validation rules and boundaries (incl. trailing newline) | Unit | AC-002, 003, 004, 016 | `tests/unit/test_validation.py` |
| Filter validation | Unit | AC-012 | `tests/unit/test_filters.py` |
| Repository ordering, filters, rollback, ids, schema CHECK | Unit | AC-008, 014, 015, 016 | `tests/unit/test_repository.py` |
| Service operations, not-found, empty states | Unit | AC-001, 006, 007, 009, 010, 011, 015 | `tests/unit/test_service.py` |
| Launcher settings | Unit | AC-016 | `tests/unit/test_launcher.py` |
| Errors, logging policy, Host/Origin checks | Integration | AC-015, 016 | `tests/integration/test_errors_and_security.py` |
| List, filter, clear, msg whitelist, no visible id | Integration | AC-006-009, 012, 013, 014 | `tests/integration/test_list_filter.py` |
| Create and update workflows | Integration | AC-001-005, 010, 016 | `tests/integration/test_create_update.py` |
| Delete confirm/cancel, not found | Integration | AC-011, 015 | `tests/integration/test_delete_not_found.py` |

All tests are deterministic: temporary DB per test, fixed `today`, no network. Runner: pytest.

## 4. Acceptance Criteria Mapping

| AC | Tasks | Tests |
|----|-------|-------|
| AC-001 | 009, 015 | test_service, test_create_update |
| AC-002 | 003, 015 | test_validation, test_create_update |
| AC-003 | 003, 015, 016 | test_validation, test_create_update |
| AC-004 | 003, 015, 016 | test_validation, test_create_update |
| AC-005 | 014, 015 | test_create_update |
| AC-006 | 009, 014 | test_service, test_list_filter |
| AC-007 | 009, 014 | test_service, test_list_filter |
| AC-008 | 007, 014 | test_repository, test_list_filter |
| AC-009 | 009, 014 | test_service, test_list_filter |
| AC-010 | 016 | test_service, test_create_update |
| AC-011 | 017 | test_service, test_delete_not_found |
| AC-012 | 005, 007, 014 | test_filters, test_repository, test_list_filter |
| AC-013 | 014 | test_list_filter |
| AC-014 | 007, 014 | test_repository, test_list_filter (no visible id) |
| AC-015 | 009, 011, 016, 017 | test_service, test_repository, test_delete_not_found, test_errors_and_security |
| AC-016 | 003, 007, 011, 012, 021 | test_validation, test_repository, test_errors_and_security, test_launcher |
| DoD (REQ-NFR-004) | 001, 002, 022, 023 | all suites |

Requirement-level coverage: REQ-001..026 and REQ-NFR-001..004 each appear in at least one task row in section 2. Architecture components: Web (014-017), Service (003, 005, 009), Repository (007), Config/factory (011, 012), Launcher (021).

## 5. Risks and Mitigations

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Dependency approval delayed or refused | TASK-001 first; fallback is the stdlib CLI in ADR 0001 (architecture change, reopens G2) |
| 2 | Host check port handling under test client vs real server | Use the request's server port; test both with the test client and the launcher manual check in verification |
| 3 | Regex `$` accepts trailing newline | Full-match semantics plus explicit tests (FND-012) |
| 4 | Catch-all handler masks HTTP errors | Explicit tests that 404/400/403 keep status and are not logged as failures (FND-013) |
| 5 | Time zone near midnight | Injected `today`; documented limitation |
| 6 | Filter future dates | Resolved by user: allowed; tested in TASK-006 |
| 7 | pip-audit finds a vulnerability | TASK-001 stops and reports before installing app dependencies |

## 6. Definition of Done

- All tasks complete and all planned tests pass (exact commands and counts reported).
- Every AC and REQ covered by a task and a passing test.
- Code review has no open Blocker or Major findings.
- Verification report is complete and `Pass` for the current `HEAD`.
- README updated; dependencies pinned and vulnerability-checked; no secrets or `data/` committed.

## 7. Open Questions

None. Q-1 was resolved by the user on 2026-11-16 (see section 0). Suggestion for the Orchestrator: record the clarification in `docs/workflow-state.md`; architecture section 8 wording ("port") may optionally be aligned by the architecture owner, but no plan task depends on it.

## 8. Approval

No separate approval gate applies to this plan. The Orchestrator records its acceptance in `docs/workflow-state.md`.
