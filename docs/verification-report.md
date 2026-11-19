# Verification Report

- Workflow ID: WF-EPMCDMETST-71369-20261116
- Jira key: EPMCDMETST-71369
- Author role: verification-agent (round 2, after change requests REQ-CR-001/002)
- Date: 2026-11-17
- Status: Draft
- Result: **Pass**

## Environment
- Branch: `development`; commit verified: `57a744c`
- Working tree: tracked source/test files clean. Unrelated untracked/modified items only: ` M .mcp.json`, `?? .claude/worktrees/`, `?? docs/codemie/`.
- `git diff --stat 93f9a42 HEAD -- src tests requirements*.txt pytest.ini README.md` printed nothing, so code, tests and dependencies are unchanged since the commit that implemented the CRs; later commits are docs-only.
- Python 3.14.8, Windows 11. Test command taken from `pytest.ini` (`pythonpath = src`, `testpaths = tests`). No dependencies installed.

## Commands run
| Command | Exit | Key output |
|---|---|---|
| `python -m pytest -v` | 0 | `252 passed in 2.19s` |
| `python -m pytest -q` (second run) | 0 | `252 passed in 2.15s` |
| `python -m pip_audit -r requirements.txt` | 0 (output ended) | `No known vulnerabilities found` (pip_audit builds its own temp venv; a path-casing warning was printed; no project install) |
| Live server: `EXPENSE_DB_PATH=<temp db> python -m expense_tracker --port 8766`, probed with curl | n/a | see Live checks. Server on 8766 stopped afterwards (only that PID); temp DB removed. The user's server on 127.0.0.1:5000 was untouched and still returned 200. |

## Test totals
252 passed / 0 failed / 0 skipped. Suites: unit (test_filters, test_launcher, test_repository, test_service, test_validation) and integration (test_create_update, test_delete_not_found, test_errors_and_security, test_list_filter, test_static_assets). 95 integration tests collected.

## Live checks (port 8766, temp DB)
- `GET /static/style.css`: `HTTP/1.1 200 OK`, `Content-Type: text/css; charset=utf-8`, 3597 bytes.
- Stylesheet link `/static/style.css` present on: list (`/`, 200), create form (`/expenses/new`, 200), edit form (`/expenses/1/edit`, 200), confirm-delete (`/expenses/1/delete`, 200), 404 error page (`/nonexistent`, 404). Unexpected-error (500) page not triggered live; covered by `test_static_assets.py` and `error.html` has the link.
- `type="date"` present on: create form and edit form (`expense_date`, edit retains `value="2026-01-05"`), list filter `start` and `end`.
- `<script` count on list page: 0.
- POST without Origin: 403 (existing guard). POST with Origin and valid data: 303 to `/?msg=created`; list shows 12.50 / lunch.
- Hand-posted create with `2026-13-45` and `05/01/2026`: HTTP 400, "Expense date must be a valid date in YYYY-MM-DD format."; `2099-01-01`: HTTP 400, "Expense date must not be in the future." Only the one valid expense existed afterwards (list showed a single row).
- Hand-posted update with `2099-01-01`: 400 future-date message; with `garbage`: 400 invalid-format message; record still present unchanged (`lunch` count 1).
- Filter `?start=2026-02-01&end=2026-01-01`: "Start date must not be after end date; the date range was not applied." Valid range `2026-01-01`..`2026-02-01` retained in both date inputs.
- Host check: `Host: evil.example:8766` returns 400 for both `/static/style.css` and `/`.
- Viewport meta present in `base.html` and `error.html`; `style.css` has a `@media (max-width: 40rem)` block and `.table-wrap { overflow-x: auto; }`.

## Acceptance criteria (full suite 252 passed; AC-to-test mapping per `tests/`, behaviour re-confirmed live for AC-001/003/004/010/012/016)
| AC | Result | Evidence |
|---|---|---|
| AC-001 create | Pass | integration create tests; live valid POST 303 |
| AC-002 fields/category | Pass | validation and repository unit tests (all 8 categories); live |
| AC-003 mandatory/validation | Pass | `test_all_fields_missing_gives_four_messages`, integration create/update; live date errors |
| AC-004 amount | Pass | `test_amount_accepted/rejected` parametrised suites |
| AC-005 confirmation | Pass | integration (`msg=created` redirect live) |
| AC-006 view all | Pass | `test_list_filter.py`; live list |
| AC-007 list fields, no currency | Pass | `test_amount_display`, list tests; live `12.50` |
| AC-008 newest first | Pass | `test_list_ordered_by_date_desc_then_id_desc`, service test |
| AC-009 empty message | Pass | `test_empty_state_*` |
| AC-010 update | Pass | `test_create_update.py`; live invalid updates rejected |
| AC-011 delete with confirm | Pass | `test_delete_not_found.py`; live confirm page 200 |
| AC-012 filters | Pass | `test_filters.py`, `test_list_filter.py`; live inverted range message |
| AC-013 clear filters | Pass | `test_list_filter.py` |
| AC-014 unique id not shown | Pass | `test_ids_not_reused_after_delete`; live list shows no id column |
| AC-015 non-existent update/delete | Pass | `test_delete_not_found.py`, service not-found tests |
| AC-016 validation/error handling | Pass | `test_errors_and_security.py`, rollback repository tests |
| NFR-001 no sensitive info | Pass | `test_errors_and_security.py`; live 403/404/400 pages generic |
| NFR-002 data integrity | Pass | `test_rollback_on_failure_leaves_data_unchanged`, `test_failed_insert_does_not_persist`; live invalid posts created nothing |
| NFR-003 meaningful messages | Pass | `test_messages_name_the_field[*]` |
| NFR-004 unit + integration tests | Pass | 157 unit/integration split per files above: both suites present and passing |

(NFR-004 note: 95 integration tests collected; remaining 157 are unit tests.)

## Change requests (requirements section 8.1)
| Statement | Result | Evidence |
|---|---|---|
| CR-001: stylesheet served and linked on every page incl. error pages | Pass | live 200 text/css; link on list/form/edit/confirm-delete/404; `test_static_assets.py` passes |
| CR-001: buttons, list, messages visually distinct; errors vs success | Not verifiable visually; CSS inspection only | `style.css` defines button, table, `.error` (red/danger-bg) and success (green/success-bg) rules. Rendering not viewed in a real browser. |
| CR-001: no horizontal scroll at ~360 px; readable wide | Not verifiable visually | CSS has viewport meta, `@media (max-width: 40rem)`, `.table-wrap{overflow-x:auto}`; no browser/viewport test run |
| CR-001: no new dependency, no JS | Pass | requirements files unchanged since 93f9a42 diff; `<script` count 0 |
| CR-001: existing behaviour unaffected | Pass | 252 tests pass |
| CR-002: date fields are `type="date"` (create, update, filter start/end) | Pass (markup) | live HTML. Native calendar opening not verified in a browser. |
| CR-002: hand-posted invalid/malformed/future date still gives existing error, nothing created/updated | Pass | live create and update results above |
| CR-002: start after end still shows REQ-024 message | Pass | live |
| CR-002: valid date retained on redisplay; non-ISO dropped by browser (FND-023) | Pass for valid date (live); FND-023 browser drop not verifiable server-side | server echoes the posted value (e.g. `value="2026-13-45"`); dropping happens in the browser. Accepted limitation. |
| CR-002: minimal accent colour | Pass (CSS inspection) | `--primary: #0f766e` used for links, primary buttons, focus outline, table header border; palette otherwise neutral. Appearance not viewed. |

## Defects
None found.

## Limitations
- Visual appearance, responsive layout at 360 px, and the native browser calendar picker were not verified in a real browser; only served markup/CSS and HTTP behaviour were checked.
- Unexpected-error (500) page styling verified by the automated test only, not triggered live.
- pip_audit result reflects the packet-stated unchanged dependencies; run via its own temporary venv, not the project environment.
- AC-to-test mapping is by test file/name; tests were not individually annotated with AC IDs.
