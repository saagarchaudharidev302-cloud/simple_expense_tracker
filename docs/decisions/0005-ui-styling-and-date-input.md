# 0005 UI styling and native date input

- Status: Accepted (amendment; user chose "Short amendment, no gate reopen (Recommended)" on 2026-11-17)
- Date: 2026-11-17
- Workflow: WF-EPMCDMETST-71369-20261116

## Context
Change requests CR-001 (cleaner UI) and CR-002 (calendar date picker, teal accent), requested by the user on 2026-11-17 and already implemented. They must fit ADR 0001 (server-rendered, no JavaScript), ADR 0003 (server-side validation) and ADR 0004 (log policy).

## Options considered
Styling: (1) CSS framework or CDN; (2) one hand-written static stylesheet.
Date input: (1) JavaScript date-picker library; (2) native `<input type="date">`.

## Decision
- Styling: option 2. A single hand-written `src/expense_tracker/static/style.css`, served by Flask's default static route and linked from `base.html` and the standalone `error.html`. No CDN, JavaScript or new dependencies. Static requests pass through the existing `before_request` Host check (FND-005) and are not logged by the application (ADR 0004 unchanged). Teal accent; goal is WCAG AA contrast for text and the focus ring.
- Date input: option 2. `expense_date` (form) and `start`/`end` (list filters) use `type="date"`. Server-side validation (`^[0-9]{4}-[0-9]{2}-[0-9]{2}$` fullmatch, real date, not in the future) is unchanged and remains authoritative; the browser control is a convenience only.

## Consequences
- No new attack surface or dependencies; no change to routes, data model or validation.
- Known limitation (FND-023, accepted): a hand-edited non-ISO value in the URL or a re-rendered form is dropped by the browser's date control, so the field displays empty although the server reported the error.
- Contrast and picker appearance depend on the browser; verified by inspection, not automated.
