---
name: implement-feature
description: Implement approved plan tasks (or assigned review/verification findings) with tests on the development branch via implementation-agent, in scoped chunks.
argument-hint: "[TASK-### list | FND-### list]"
disable-model-invocation: true
---

# /implement-feature

Stage: Implementation, and fixes for review/verification findings. Agent: `implementation-agent`.

## Inputs
- `$ARGUMENTS`: tasks (`TASK-###`) or findings (`FND-###`) to handle. If empty, take the next unfinished tasks in dependency order from `docs/impl-plan.md`, in a small coherent chunk.
- Approved requirements and architecture (G1, G2 recorded), `docs/impl-plan.md`.

## Steps
1. **Branch check (hard stop).** Run `git branch --show-current` and `git status --short`. If not `development`, stop and tell the user; do not switch. Note unrelated uncommitted changes and tell the agent to preserve them.
2. Delegate to `implementation-agent` with the handoff packet: scope, artifact paths, approval quotes, explicit dependency-install approvals (or "none"), and for fixes the finding text.
3. Verify the report against `git status` and `git log --oneline`: only expected paths changed, commits are on `development`, nothing was pushed, nothing touched `main`, `.claude/` or approved docs.
4. Check reported test results are actual command outputs. Update task status and results in the workflow state.
5. Repeat for the next chunk until all tasks are done, then proceed to `/review-code`.

## Output
Code and tests in `src/` and `tests/`, local commits on `development`; updated workflow state.

## Constraints
- Never install dependencies without the user's explicit approval.
- Plan or architecture problems found by the agent go to the user, not into improvised changes.
