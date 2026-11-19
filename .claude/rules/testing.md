---
paths:
  - "src/**"
  - "tests/**"
  - "docs/verification-report.md"
  - "docs/impl-plan.md"
---

# Testing Standards

- **Tests ship with code.** Behavior is delivered together with automated tests that prove it.
- **Layout.** Unit tests in `tests/unit/`, integration tests in `tests/integration/`. Add end-to-end tests only where acceptance criteria describe user-visible flows that lower levels cannot prove.
- **Traceability.** Every acceptance criterion has at least one test, or a documented reason it cannot be automated (with the manual check performed).
- **Quality.** Tests are deterministic and independent: no reliance on order, wall-clock time, network or shared state unless controlled. Cover the happy path, error paths and boundaries named in the requirements.
- **No gaming.** Never skip, weaken or delete a test to get a green run.
- **Tooling.** Use the test runner and linter native to the stack chosen in the architecture; do not add tooling the plan does not call for.

## Test evidence
- Implementation reports the exact commands run and actual pass/fail/skip counts.
- Verification re-runs tests itself and records, per command: the command, exit status and relevant output. It separates **executed**, **passed**, **failed**, **skipped** and **not run (with reason)**. Results are never inferred or fabricated.
- A verified `Pass` is tied to the `HEAD` commit it ran against; any later commit makes it stale.
