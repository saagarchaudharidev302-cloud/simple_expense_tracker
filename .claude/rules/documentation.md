---
paths:
  - "docs/**"
  - "output/**"
  - "README.md"
---

# Documentation Standards

## Artifact locations
| Artifact | Path |
|----------|------|
| User story | `docs/user-story.md` |
| Requirements | `docs/requirements.md` |
| Architecture | `docs/architecture.md` |
| Design review | `docs/design-review.md` |
| Implementation plan | `docs/impl-plan.md` |
| Code review | `docs/code-review.md` |
| Verification report | `docs/verification-report.md` |
| Workflow state | `docs/workflow-state.md` |
| Decision records | `docs/decisions/NNNN-short-title.md` (zero-padded, kebab-case) |
| PR description draft | `output/pr-description.md` (git-ignored) |

## Conventions
- IDs: workflow `WF-<JIRA-KEY>-<YYYYMMDD>`; requirements `REQ-###` (non-functional `REQ-NFR-###`); acceptance criteria `AC-###`; tasks `TASK-###`; findings `FND-###`.
- Each artifact starts with a header block: workflow ID, Jira key, author role, date, status.
- Status values: `Not started`, `Draft`, `In review`, `Approved`, `Superseded`. Only the Orchestrator sets `Approved`, and only after the user's approval.
- Overwrite an artifact only for the current workflow. History lives in git, not in file copies.
- Each artifact has one owner agent (see `agent-orchestration.md`); other agents do not edit it.
- Be concise and structured. Link between artifacts by ID instead of duplicating content.

## Decision recording
- Significant technical decisions are ADRs in `docs/decisions/`, written by the Architecture Agent: context, options considered, decision, consequences.
- User clarifications and approvals are recorded verbatim, with dates, in `docs/workflow-state.md`.
- Assumptions and open questions are recorded in the artifact that depends on them.
