---
name: review-code
description: Run an independent code review of the implementation via code-review-agent, route Blocker/Major findings to implementation-agent, and request re-review until clean.
disable-model-invocation: true
---

# /review-code

Stage: Code review and resolution. Agents: `code-review-agent`, then `implementation-agent` for fixes.

## Inputs
- Implemented code and tests on `development`, approved requirements/architecture, `docs/impl-plan.md`.

## Steps
1. Verify branch is `development`. Note the current `HEAD` hash.
2. Delegate to `code-review-agent` with the packet: artifact paths, commit range to review, scope (all changes or only changes since the last round), round number. Do not include the implementer's self-assessment.
3. Verify only `docs/code-review.md` changed and no application files were modified.
4. Record findings (FND-###, severity, status) in the workflow state.
5. Send open Blocker/Major findings to `implementation-agent` (use `/implement-feature` with the FND ids), then request re-review of the changed code. Repeat until no Blocker/Major is open.
6. Minor/Info: fix or record as known limitations with the user's agreement. Findings revealing a requirements/architecture problem go to the user (reopen G1/G2).

## Output
`docs/code-review.md` with no open Blocker/Major; updated workflow state.

## Constraints
- Reviewers do not fix code. Fixers do not review their own fixes.
- Same finding surviving three rounds: escalate to the user.
