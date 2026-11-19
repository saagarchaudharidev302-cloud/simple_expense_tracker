# Design Review

| Field | Value |
|-------|-------|
| Workflow ID | `WF-EPMCDMETST-71369-20261116` |
| Jira issue key | `EPMCDMETST-71369` |
| Author role | Design Review Agent |
| Date | 2026-11-16 |
| Status | Draft |
| Review round | 2 |

## Verdict: Approve

No Blockers and no Majors. All round 1 findings are resolved. Three new Minor findings are clarifications that can be deferred to planning or implementation. The design remains proportionate (Flask, SQLite, three layers) and is justified by ADRs 0001-0004.

## Round 1 resolution check

| Finding | Round 1 severity | Status | Evidence in architecture rev 2 |
|---------|------------------|--------|-------------------------------|
| FND-001 | Major | Resolved | Section 8 logging: only operation type and exception class; no `exc_info`, paths, message text or request values; catch-all handler; caplog test; ADR 0004 records the user's choice. Consistent with REQ-NFR-001. |
| FND-002 | Minor | Resolved | Section 6 defines per-filter independent validation, inverted range drops both bounds, remaining filters apply, and the empty-state rule. |
| FND-003 | Minor | Resolved | Section 5 amount grammar, trailing zeros counted, boundary tests listed. (See FND-012 for a regex detail.) |
| FND-004 | Minor | Resolved | Section 5 strict date pattern; malformed forms tested. (See FND-012.) |
| FND-005 | Minor | Resolved | Section 8 Host allowlist; Origin, then Referer, then reject if both absent. |
| FND-006 | Minor | Resolved | Section 6: unknown `msg` ignored. |
| FND-007 | Minor | Resolved | Sections 6 and 7, ADR 0002: affected-row count; 0 maps to 404. |
| FND-008 | Minor | Resolved | Section 4: per-request connection, default path, launcher fixes host and debug. |
| FND-009 | Minor | Resolved | Section 8 adds REQ-016, `msg` and CSRF tests. |
| FND-010 | Minor | Resolved | Single `CATEGORIES` source with schema test; pinning and pip-audit before approval. |
| FND-011 | Info | Acknowledged | Risk 4 unchanged. |

## Requirement coverage check

| Requirement | Component | Test approach | Result |
|-------------|-----------|---------------|--------|
| REQ-001, 002 | Web, Service, Repo | Integration create | Covered |
| REQ-003, 004, 019, 021-023, NFR-003 | Service, Web | Unit boundary list (section 8) | Covered |
| REQ-005, 026 | Web `msg` whitelist | Integration, hostile `msg` | Covered |
| REQ-006, 007 | Web, Repo, Service format | Integration | Covered |
| REQ-008 | Repo ordering (ADR 0003) | Tie-break unit and repo tests | Covered |
| REQ-009, 025 | Web template | Integration, filter combinations | Covered |
| REQ-010, 011 | Web, Service, Repo | Integration (confirm and cancel) | Covered |
| REQ-012-015, 024 | Service, Repo, Web | Unit and integration | Covered |
| REQ-016 | Repo autoincrement, Web | Uniqueness/no-reuse and no-visible-id tests | Covered |
| REQ-017 | Service, 404 handler, affected rows | Integration not-found, repo count 0 | Covered |
| REQ-018 | `CATEGORIES` constant | Unit, schema-match test | Covered |
| REQ-020, NFR-002 | Repo transactions | Rollback tests | Covered |
| REQ-NFR-001 | Error handlers, logging policy | Forced exception plus caplog | Covered |
| REQ-NFR-004 | Section 8 | n/a | Covered |

## Findings

### FND-012 - Minor - Input handling (regex anchoring)
Evidence: Section 5: "require the grammar `^[0-9]+(\.[0-9]+)?$`" and "must match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` exactly (no trimming of inner content...)". In Python, `$` also matches before a trailing newline, so `2026-01-05\n` would pass the date pattern, contradicting "exactly".
Recommendation: State that the patterns are applied as full-string matches (no trailing-newline tolerance) and add a trailing-newline case to the date and filter tests.

### FND-013 - Minor - Error handling (handler precedence)
Evidence: Section 8: "A catch-all `Exception` handler is registered so the framework does not log tracebacks itself", alongside 404, 400 and 403 responses.
In Flask a catch-all `Exception` handler also receives HTTP errors, so a 404, 400 or 403 could be turned into a 500 and logged as a failure. Failures outside request handling (for example opening the database at startup, logged as `startup`) are also not covered by the handler.
Recommendation: State that HTTP errors keep their status codes and generic pages, and that startup failures are caught and logged under the same policy (operation and class only). Add a test for a 404 not producing a failure log.

### FND-014 - Minor - Testability (Host check)
Evidence: Section 8: Host "must be one of `127.0.0.1:<port>` or `localhost:<port>`".
Flask's test client sends a Host without a port by default, and the port is not defined in the architecture (launcher fixes host only). Integration tests could fail or the check could be bypassed in tests.
Recommendation: Specify how the allowed port is determined, and that integration tests set a valid Host so the same check runs in tests.

### FND-015 - Info
Section 10 risk rows are numbered out of order (6 before 5). Cosmetic. ADR 0004 is `Proposed` pending G2, as expected. Reopening G2 is required because architecture rev 2 and ADRs changed.

## Open Questions (for the Orchestrator)
None. Requirements are unchanged and unambiguous for this review.

## Counts
Blocker 0, Major 0, Minor 3, Info 1.
