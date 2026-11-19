# 0004 Log content policy

- Status: Accepted (G2 re-approved 2026-11-16, revision 2)
- Date: 2026-11-16
- Workflow: WF-EPMCDMETST-71369-20261116

## Context
Design review FND-001: the first architecture logged error class and stack, which conflicts with REQ-NFR-001 ("Error messages and logs shall not expose ... stack traces, file paths and other internal details"). `sqlite3` error text can contain the database path.

## Options considered
1. Keep stack traces in logs and request a requirements exception. Better diagnosability, but changes approved requirements.
2. Apply REQ-NFR-001 literally: log only operation type and exception class name.

## Decision
Option 2, chosen by the user on 2026-11-16 ("Apply NFR literally"). Failure log entries hold only the operation type and exception class name. No `exc_info`, no exception message text, no paths, no request values. A catch-all exception handler is registered so the framework does not emit its own traceback log. Requirements are unchanged.

## Consequences
- Less detail for debugging; developers reproduce locally.
- Testable: a test forces a repository exception and asserts the captured log has no traceback, path or message text.
