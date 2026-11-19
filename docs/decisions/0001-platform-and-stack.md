# 0001 Platform and technology stack

- Status: Accepted (G2 re-approved 2026-11-16, revision 2)
- Date: 2026-11-16
- Workflow: WF-EPMCDMETST-71369-20261116

## Context
Requirements leave the platform/interface to Architecture (Q11). Needs: forms with field-level validation messages (REQ-003, REQ-019), a list with filters and "clear filters" (REQ-012..015), delete confirmation (REQ-011), success/empty-state messages. Single user, no auth, no volume/performance targets (Q9). No user constraints on language or hosting were given.

## Options considered
1. **Command-line app (Python stdlib, argparse).** No dependencies. Filter state, "clear filters" and select-then-update are awkward in one-shot commands; an interactive loop adds custom UI code.
2. **Server-rendered local web app (Python + Flask + Jinja, no JavaScript).** Forms, lists and confirmation pages map directly to the requirements. Two third-party packages (Flask; pytest for tests).
3. **SPA (JS frontend plus API backend).** Two codebases, build tooling, more dependencies. No requirement justifies it.

## Decision
Option 2: Python 3 with Flask and Jinja templates, server-rendered HTML, no client-side JavaScript. Tests with pytest (Flask test client for integration tests). Runs locally, bound to 127.0.0.1.

## Consequences
- Needs user approval to install Flask and pytest (not installed now). Versions are pinned exactly and checked for known vulnerabilities (for example `pip-audit`) before the approval request (FND-010).
- Launched by a module entry point that fixes host `127.0.0.1` and debug off (FND-008).
- Delete confirmation is a server-rendered confirmation page, so it works without JavaScript.
- Python version and team skills are assumptions; if the user prefers another language, this ADR is revisited.
- Option 1 remains a viable zero-dependency fallback if the user declines installing packages.
