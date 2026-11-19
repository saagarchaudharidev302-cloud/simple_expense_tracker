# Git Workflow

Two-branch strategy. Mandatory for all agents.

| Branch | Rules |
|--------|-------|
| `main` | Protected production branch. No direct commits or pushes. No agent checks it out, modifies it or merges into it. Changes arrive only via an approved pull request from `development`. |
| `development` | The only working branch. All code, fixes and integration happen here. No feature branches in this MVP. |

## Before any work
- The Orchestrator runs `git branch --show-current` and `git status --short` before starting a workflow. If the branch is not `development`, stop and ask the user. If `development` does not exist, ask the user to create it.
- Every specialist verifies the branch before acting and returns `Blocked` if it is not `development`. Specialists never switch, create or delete branches.
- Before any Git operation that changes state, inspect the branch and working tree. Preserve unrelated user changes: never discard, reset, stash or overwrite them.

## Commits
- The Implementation Agent commits code and tests on `development`. The Orchestrator commits workflow documents on `development` when needed so the tree is clean before PR preparation.
- Stage specific files only (no blind `git add -A` / `git add .`). Never stage `.env` or secrets.
- Messages are concise and explain why. Commit only when the workflow requires it or the user asks.

## Pull request
- Source `development`, target `main`. Only `pr-agent` creates it, only after the user's explicit approval (gate G3), and only when the current `HEAD` has a verified `Pass`.
- Nobody merges automatically. The user merges.

## Never
- Force-push, rewrite shared history, delete branches, or disable or bypass branch protection.
- Run `git reset --hard`, `git clean`, or `git checkout -- .`.

## Enforcement
Hooks (`.claude/hooks/`) block force-pushes, pushes to `main`, switching to `main`, destructive commands, and code writes outside `development`. They cannot see user intent or approvals, so approval gates and the "preserve unrelated changes" rule are enforced by agent instructions. Remote branch protection is configured on the hosting platform, not in this repository.
