# Code Review

| Field | Value |
|-------|-------|
| Workflow ID | `WF-EPMCDMETST-71369-20261116` |
| Jira issue key | `EPMCDMETST-71369` |
| Author role | Code Review Agent |
| Date | 2026-11-17 |
| Status | Draft |
| Round | 4 |
| Verdict | Approve with changes |

## Scope
Commits 2086f5d..5249f30 (HEAD 5249f30), branch `development`. Files reviewed in full: `src/expense_tracker/{app,web,service,repository,validation,__main__}.py`, all five templates, `tests/conftest.py`, `tests/integration/test_errors_and_security.py`, test names of all other test files, `requirements*.txt`, `.gitignore`, README excerpts. Compared against `docs/requirements.md`, `docs/architecture.md` (rev 2) and the ADR set. Tests were not run (the Verification Agent does that). The change list matches git: 27 non-doc files, 2223 insertions. `git status` shows uncommitted changes only in docs, `.mcp.json` and untracked ADRs; none are implementation files.

## Carried design-review findings
| ID | Result | Evidence |
|----|--------|----------|
| FND-012 | Confirmed | `validation.py:22-24, 88, 100` use `fullmatch`. Tests cover `2026-01-05\n`, `5\n5` and `Food\n` (`test_validation.py:76,108,155`, `test_filters.py:112`). `5\n` is accepted as 5 because amount is trimmed first, which matches architecture section 5. |
| FND-013 | Confirmed | `app.py:73-80` registers an `HTTPException` handler before the `Exception` catch-all. Tests cover 404, a raised 403 and 405, none logged (`test_errors_and_security.py:63-81`). Startup failures are logged as class name only and re-raised `from None` (`app.py:98-108`, test at line 92). See FND-016 for a residual issue. |
| FND-014 | Confirmed | `app.py:40-45` compares the Host port to `SERVER_PORT`, defaulting to 80 when absent. Tests cover ports 80, 5000 and 8123, a mismatched port, and rebinding-style hostnames. |

## Findings
No Blocker or Major findings.

| ID | Severity | Location | Description | Recommendation |
|----|----------|----------|-------------|----------------|
| FND-016 | Minor | `app.py:22-27, 35-36, 73-75` | The `HTTPException` handler renders the status's own code, but `_GENERIC_MESSAGES` has only 400/403/404/500. Any other code (for example 405) falls back to the 500 heading and text, "Something went wrong. Please try again.", under a 405 status. That text is misleading for a client error, and the `Allow` header is dropped. A redirect-type `HTTPException` (3xx) would also be rendered as an error page without a `Location`. No current route triggers the redirect case, because none is defined with a trailing slash. | Add a generic fallback for other 4xx codes, or return `error.get_response()` for non-error codes. Add a test asserting the 405 body text. |
| FND-017 | Minor | `tests/integration/test_errors_and_security.py:21-38, 47-60` | The "forced exception yields generic 500 and policy log" test uses a synthetic `/boom` route. No test forces a repository failure through a real route (create/update/delete) and asserts both the 500 page and that stored data is unchanged. REQ-020 and REQ-NFR-002 are covered only at repository level (`test_repository.py:81-96`). | Add one integration test that monkeypatches the repository to raise during create and update, then asserts a 500, no stored change and the policy log. |
| FND-018 | Minor | `repository.py:129` | The method name `list` shadows the builtin inside the class namespace. It works, but it is fragile if later annotations use `list[...]` in the class body. | Rename to `list_expenses` or `find`. Low priority. |
| FND-019 | Info | `error.html:12` | The back link is hard-coded to `/` rather than `url_for`. This is harmless today. | Use `url_for('web.list_page')` for consistency. |
| FND-020 | Info | working tree | ADRs 0001-0004 and the updated docs are untracked or modified. `.mcp.json` is modified, and it is not part of this workflow. | The Orchestrator should commit the docs before G3 so the tree is clean. Do not stage `.mcp.json` unless the user intends it. |
| FND-021 | Info | `app.py:48-57` | The Origin/Referer check compares `netloc` to `request.host` as exact strings, so case or explicit default-port differences would be rejected (fail-closed). Browsers send normalized values, so there is no functional issue. | None needed. Optionally note it in the README. |

## Checks with no findings
- **SQL safety.** All values are bound parameters (`repository.py:87-141`). The only interpolated SQL is the `CATEGORIES` constant in the schema and the fixed clause fragments in `list`.
- **Output encoding.** Jinja autoescaping is on. The `msg` value is looked up in a whitelist and never echoed (`web.py:12-16, 30`). Tests cover hostile `msg` values and HTML escaping.
- **Input validation.** Amount grammar, ASCII-only digits, a 20-character cap, Decimal parsing, 2-decimal and maximum checks, strict date regex plus calendar validation, the future-date rule and the description limit all match architecture section 5. Category is exact-match against the constant.
- **Data integrity.** Writes use a transaction with rollback on `BaseException`. The service maps a 0-row update or delete to `NotFoundError`. The schema has CHECK constraints for amount and category.
- **Log policy (ADR 0004 / REQ-NFR-001).** `_log_failure` logs operation and class name only, with no `exc_info`. The test asserts exact message text, no `exc_info`, and no secret text or "Traceback".
- **Launcher.** The host is the constant `127.0.0.1`, debug is off, and only the port is configurable and range-checked. Tests confirm host and debug cannot be set.
- **Dependencies.** Only Flask, pytest and pip-audit, all pinned exactly. This matches the approved architecture.
- **Scope creep.** None found. The per-request connection lifecycle matches the architecture.

## AC-to-test coverage
| AC | Tests |
|----|-------|
| AC-001, 002, 005 | `test_create_update.py` (create success, message, fields) |
| AC-003, 004, 016 | `test_validation.py`, `test_create_update.py` (missing fields, amount, date, description, category boundaries, multiple errors, value preservation, unchanged list) |
| AC-006, 007, 008, 009 | `test_list_filter.py` (empty, fields, ordering with tie-break), `test_repository.py` |
| AC-010 | `test_create_update.py` (edit prefill, update success, invalid update not saved) |
| AC-011 | `test_delete_not_found.py` (confirmation page, GET does not delete, confirm, cancel) |
| AC-012, 013 | `test_list_filter.py`, `test_filters.py` (category, inclusive range, open bounds, combined, inverted range, no-match message, clear filters) |
| AC-014 | `test_repository.py` (ids not reused), `test_list_filter.py` (id not visible as text) |
| AC-015 | `test_delete_not_found.py` (404 and no change), `test_errors_and_security.py` |

All ACs have tests. The residual gap is the web-level failure-path test (FND-017). A test run is still required from the Verification Agent.

## Open Questions
None.

## Round 2 re-review (commit 0503174, HEAD)
Scope: `git show 0503174` (app.py, repository.py, service.py, three test files). `pytest -q` run read-only: 244 passed. `grep` finds no remaining `.list(` callers.

| ID | Result | Evidence |
|----|--------|----------|
| FND-016 | Resolved | `app.py:26,36-37,77-85`: 405 has its own message, other 4xx fall back to the 400 text, and 3xx return `error.get_response()`. The handler copies `error.get_headers()` (Allow, Retry-After and similar) except Content-Type and Content-Length. These headers are fixed by Werkzeug and contain no request data or internals. Test at `test_errors_and_security.py:78-85` asserts 405, `Allow`, the new body text, absence of the 500 text, and no log record. |
| FND-017 | Resolved | `test_errors_and_security.py:204-259`: create and update through real routes with the repository forced to fail. They assert a 500, the secret text absent from the body and logs, the exact policy log message on create, and unchanged data afterwards. |
| FND-018 | Resolved | Renamed to `list_expenses` in `repository.py:129`, `service.py:84` and unit tests. |

ADR 0004 still holds. HTTP errors remain unlogged (the `HTTPException` handler does not call `_log_failure`), and unexpected errors log operation and class name only. No new findings.

Minor observation, not a finding: the update failure test checks only the log count, not the message text. The create test already covers the exact text.

## Verdict
Approve. FND-016 to FND-018 are resolved with no regressions. No open Blocker, Major or Minor findings. FND-019 to FND-021 remain Info and were deferred by the user's decision. A Verification Agent run is still required.

## Round 3 review (change requests CR-001 cefc76f, CR-002 848a3f2; HEAD 848a3f2)
Scope: `git diff 047938f..848a3f2 -- src tests` (style.css, base/error/form/list/confirm_delete templates, `test_static_assets.py`, `test_create_update.py`). `pytest -q` run read-only: 250 passed. Python code, routes, validation and field names are untouched. The commits are not in the approved requirements or architecture.

Checked with no problem found: labels and `name` attributes are unchanged; error spans keep their markup; `value="{{ values.* }}"` is still autoescaped; the server-side date regex and calendar validation stay authoritative (`test_hand_edited_date_text_still_fails_server_validation`); the static route goes through the `before_request` Host check (`test_static_respects_host_check`); static GETs are not logged; there is no JS, CDN or new dependency; the viewport meta tag and a `.table-wrap` scroll container are present; text and button contrast is sufficient (white on #0f766e is about 5.5:1, #c62828 on #fdecea is about 5:1).

| ID | Severity | Location | Description | Recommendation |
|----|----------|----------|-------------|----------------|
| FND-022 | Minor | `style.css:53-58` | The focus ring is `#5eead4` on white or `#f1f7f6`, about 1.4:1 contrast. This fails WCAG 2.1 SC 1.4.11 (3:1 for focus indicators), so focus is hard to see on a light background. | Use a darker outline, for example `var(--primary-dark)`. |
| FND-023 | Minor | `form.html:24`, `list.html:15-16` | With `type="date"`, a browser drops a non-ISO `value`. After a server validation error caused by a hand-edited or non-date value (for example `2026-02-30`), the field is shown empty. The user's input is not preserved, which weakens the AC-016 "values preserved" behavior for date fields. Normal browser use cannot produce such a value, and the other fields are preserved. The test `test_hand_edited_date_text_still_fails_server_validation` checks only the error message, not the re-rendered value. | Accept this and record it as a known limitation, or add an assertion that the value attribute is rendered. Optionally state the behavior in the requirements amendment. |
| FND-024 | Minor | `error.html:6` | `{{ '/static/style.css' }}` is a Jinja expression that outputs a constant literal. It is a pointless indirection and a hard-coded path, unlike `base.html`, which uses `url_for('static', ...)`. This extends FND-019. | Write the literal path directly, or pass `url_for('static', filename='style.css')` if the context allows it. The error page deliberately does not extend base.html. |
| FND-025 | Minor | `docs/requirements.md`, `docs/architecture.md` | Neither document mentions styling, a static route, native date inputs or the stylesheet. The date UI changed from a text field with a `YYYY-MM-DD` placeholder to a native date picker. The static route is a new request surface for the Host check and log policy. The approved artifacts and the code have diverged, and the G1/G2 approvals do not cover these changes. | The Orchestrator should record a documented amendment (a CR note or ADR) covering the static assets and the date-picker UI. The user should confirm whether G1/G2 reopen, since the G3 approval covered only 047938f. |
| FND-026 | Info | `test_static_assets.py:8-10` | `test_pages_link_stylesheet` asserts only that the string `/static/style.css` is in the HTML. `test_date_fields_render_as_native_date_inputs` depends on exact attribute order, so it is brittle. No test covers a pre-filled date value on edit or after an error. | Optional: assert the `<link rel="stylesheet">` element and the `value` attribute. |
| FND-027 | Info | `style.css:88-96` | `.filters label` uses `flex: 1 1 10rem`, but the select and the date inputs are `width: 100%`. The `--muted` variable is declared and unused. Native date controls vary across browsers. | Remove the unused variable. No other action. |

No Blocker or Major findings. No scope creep beyond the requested styling and date pickers.

### AC coverage impact
Unchanged. AC-003/004/016 date validation remains covered by the validation and integration tests. The new tests add the native input and server-side rejection coverage, with the gap in FND-023/026.

### Round 3 verdict
Approve with changes. FND-022 to FND-025 are Minor, and FND-025 (a documented amendment) is recommended before the next PR or G3. The Verification Agent must run again for HEAD 848a3f2.

## Round 4 re-review (code commit 93f9a42, HEAD c305115 docs-only)
Scope: `git show 93f9a42` (style.css, error.html, test_static_assets.py, test_create_update.py) and the docs amendments (requirements 8.1, architecture Amendment A1, ADR 0005). `pytest -q` run read-only: 252 passed. `git status` shows only `.mcp.json`, `.claude/worktrees/` and `docs/codemie/` untracked or modified, none of them workflow files.

| ID | Result | Evidence |
|----|--------|----------|
| FND-022 | Resolved | `style.css:53-55` focus outline is now `var(--primary-dark)` (#115e59). The Orchestrator's figures (7.58:1 on white, 7.0:1 on #f1f7f6) exceed the 3:1 required by SC 1.4.11. |
| FND-024 | Resolved | `error.html:6` uses `url_for('static', filename='style.css')`. The test asserts the rendered href. |
| FND-026 | Resolved | Tests now parse HTML: `stylesheet_links(...) == ["/static/style.css"]` on the list and 404 pages. Input type and `value` are asserted for create, edit prefill (`2026-06-01`) and list filters. They no longer depend on attribute order. |
| FND-027 | Resolved | `--muted` removed. No remaining `var(--muted)` use (the full suite passes and the diff removes only the declaration). |
| FND-023 | Accepted (Won't fix) | Recorded in ADR 0005 and Amendment A1. |
| FND-025 | Resolved | Requirements 8.1, Amendment A1 and ADR 0005 cover the stylesheet, the static route, the Host check, the log policy and the date input. They match the code. |

### New findings
| ID | Severity | Location | Description | Recommendation |
|----|----------|----------|-------------|----------------|
| FND-028 | Minor | `docs/requirements.md:147` | The REQ-CR-002 statement "A previously entered date is retained in the field when a form is redisplayed after a validation error, in the same way as other fields" is inaccurate. The server does re-render the submitted text, but the browser drops any value that is not a valid `YYYY-MM-DD` date (for example `2026-02-30` or `abc`) and shows an empty field. Valid dates are retained, including a future date rejected by the future-date rule. The same applies to the filter `start`/`end` fields. The statement also contradicts FND-023 as recorded in ADR 0005 and Amendment A1. The conditional "(if the existing behaviour retains input...)" does not cover this case. | Requirements agent or Orchestrator: reword to "A valid previously entered date is retained on redisplay. A value that is not a valid ISO date is dropped by the browser's date control (known limitation, FND-023, accepted)." |
| FND-029 | Info | `docs/requirements.md:127`, `docs/architecture.md:137,135`, ADR 0005 | The amendment items are still marked Draft or Proposed in the text while the ADR says Accepted. | The Orchestrator should align the status text when it records the amendment, before G3. |

No code regressions or new code issues found. FND-019 to FND-021 remain Info as before.

### AC coverage impact
Unchanged and stronger. Date-input type, prefill of valid values, stylesheet link on normal and error pages, and server-side rejection of hand-edited dates are all covered by deterministic tests. REQ-CR-002's redisplay statement has no test and, as worded, would be untrue for invalid values (FND-028).

### Round 4 verdict
Approve with changes. The code fixes are verified. The only open item is the Minor wording fix FND-028 (documentation) and the Info FND-029. A Verification run is still required for the current HEAD.
