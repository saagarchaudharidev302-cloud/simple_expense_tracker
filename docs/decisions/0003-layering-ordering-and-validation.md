# 0003 Layering, validation placement and deterministic ordering

- Status: Accepted (G2 re-approved 2026-11-16, revision 2)
- Date: 2026-11-16
- Workflow: WF-EPMCDMETST-71369-20261116

## Context
REQ-NFR-004 requires unit tests of core logic and integration tests of workflows. Assumption 4 requires deterministic ordering for same-date expenses; the tie-break rule is left to Architecture. Assumption 5 leaves "today" undefined.

## Options considered
- Layering: (a) logic inside route handlers; (b) three small layers: web routes, domain service (validation and rules), repository (SQL). Chosen (b): validation is unit-testable without HTTP or a database, and SQL stays in one place. No further abstractions (no interfaces, no ORM, no service container).
- Tie-break: (a) none (non-deterministic); (b) `expense_date DESC, id DESC` where `id` is an auto-increment integer, so the most recently created expense appears first among equal dates. Chosen (b).
- "Today": (a) hard-coded call to system time in validation; (b) an injectable `today` provider defaulting to the server's local date. Chosen (b), so future-date tests are not flaky.

## Decision
Layers: web, service, repository. Validation lives only in the service. The list query always uses `ORDER BY expense_date DESC, id DESC`. The service receives a `today` callable. Local server date is used for the future-date check. Amount and date inputs are validated against strict grammars (ASCII-digit regex first, then `Decimal` / `date.fromisoformat`), defined in architecture section 5 (FND-003, FND-004).

## Consequences
- Edited expenses keep their position among same-date ties (id is stable).
- Users near midnight in a different time zone from the server may see unexpected acceptance or rejection (Assumption 5, accepted).
