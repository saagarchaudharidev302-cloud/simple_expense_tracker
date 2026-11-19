---
name: create-implementation-plan
description: Convert the approved architecture and requirements into an ordered, traceable task plan in docs/impl-plan.md via planning-agent.
disable-model-invocation: true
---

# /create-implementation-plan

Stage: Planning. Agent: `planning-agent`.

## Inputs
- Approved `docs/requirements.md` and `docs/architecture.md` (+ `docs/decisions/*`), design review with no open Blocker/Major (or recorded user deferral).

## Steps
1. Verify branch is `development`.
2. Delegate to `planning-agent` with a handoff packet: artifact paths, G1/G2 approval quotes, constraints (including which dependency installs the user has approved).
3. Verify only `docs/impl-plan.md` changed. Check that every AC maps to at least one task and one test task.
4. Resolve any questions or gaps the agent reports with the user before continuing. If the plan exposes a requirements or architecture problem, take it to the user (reopen G1/G2 as needed).
5. Show the user a brief plan summary (task count, order, dependencies needing install approval). Record dependency approvals in the workflow state.

## Output
`docs/impl-plan.md`; updated workflow state.

## Constraints
- No code is written in this stage.
- Do not approve installs on the user's behalf.
