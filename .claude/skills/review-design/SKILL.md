---
name: review-design
description: Run an independent design review of the approved architecture via design-review-agent, route Blocker/Major findings back to architecture-agent, and repeat until resolved.
disable-model-invocation: true
---

# /review-design

Stage: Design review and resolution. Agents: `design-review-agent`, then `architecture-agent` for fixes.

## Inputs
- Approved `docs/requirements.md` and `docs/architecture.md` (+ `docs/decisions/*`).

## Steps
1. Verify branch is `development`.
2. Delegate to `design-review-agent`. Pass artifact paths and approval status only; do not pass the architect's rationale or your opinion (independence).
3. Verify only `docs/design-review.md` changed.
4. Record findings (FND-###, severity) in the workflow state.
5. For each open Blocker/Major: delegate to `architecture-agent` with the finding text quoted, then repeat steps 2-4. Any architecture change reopens **G2**: present the change and obtain approval again.
6. Findings that are the user's decision (for example trade-offs on cost or scope) go to the user. Proceed only when no Blocker/Major is open, or the user explicitly defers them (record the quote).
7. Minor/Info items: record as known limitations or fix at the user's choice.

## Output
`docs/design-review.md` with no open Blocker/Major; updated workflow state.

## Constraints
- The reviewer never edits the architecture; the architect never reviews its own work.
- Same finding surviving three rounds: escalate to the user.
