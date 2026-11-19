---
name: prepare-pr
description: Validate workflow completion, prepare the PR description via pr-agent, obtain approval gate G3, and only then submit the pull request from development to main.
disable-model-invocation: true
---

# /prepare-pr

Stage: PR preparation, gate **G3**, submission. Agent: `pr-agent`.

## Inputs
- All artifacts and `docs/workflow-state.md`; clean tree on `development`; verified `Pass` for current `HEAD`.

## Steps
1. Verify branch is `development` and `git status --short` is empty. Commit outstanding workflow documents on `development` (specific files only) if needed, and tell the user. Do not discard anyone's changes.
2. Confirm G1 and G2 are recorded, no Blocker/Major is open, and verification matches `git rev-parse --short HEAD`.
3. Delegate to `pr-agent` in `PREPARE` mode. Verify it wrote only `output/pr-description.md`.
4. **G3.** Show the user the PR description (title, summary, test evidence, known limitations) and ask for explicit approval to push `development` and open a PR to `main`. Record the quote and date.
5. Only with that approval, delegate to `pr-agent` in `SUBMIT` mode, quoting the approval in the packet.
6. Report the PR URL, evidence and limitations. If the agent returns commands because no CLI or auth exists, give them to the user. Do not merge.

## Output
`output/pr-description.md`, the pull request (after G3), updated workflow state.

## Constraints
- No push or PR without explicit G3 approval for this exact state; new commits after approval need fresh approval.
- Never merge, push `main`, force-push, or touch branch protection.
