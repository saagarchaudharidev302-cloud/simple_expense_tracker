# Agent Orchestration

## Roles
- **The Orchestrator is the main Claude Code session.** There is no Orchestrator subagent. It receives the story, delegates each stage to exactly one specialist, relays questions and findings to the user, obtains approvals, routes findings, and maintains `docs/workflow-state.md`.
- **Specialists** (`.claude/agents/`) do one stage, write their own artifact and return a structured report. They never invoke, message or hand off to other specialists. Only one is active at a time unless parallel work is recorded in the workflow state.

| Agent | Writes | Tools |
|-------|--------|-------|
| `requirements-agent` | `docs/requirements.md` | Read, Write, Edit, Grep, Glob |
| `architecture-agent` | `docs/architecture.md`, `docs/decisions/*` | Read, Write, Edit, Grep, Glob |
| `design-review-agent` | `docs/design-review.md` | Read, Write, Grep, Glob |
| `planning-agent` | `docs/impl-plan.md` | Read, Write, Edit, Grep, Glob |
| `implementation-agent` | `src/`, `tests/`, local commits on `development` | Read, Write, Edit, Grep, Glob, Bash |
| `code-review-agent` | `docs/code-review.md` | Read, Write, Grep, Glob, Bash (read-only use) |
| `verification-agent` | `docs/verification-report.md` | Read, Write, Grep, Glob, Bash (runs tests) |
| `pr-agent` | `output/pr-description.md`, the pull request | Read, Write, Grep, Glob, Bash |

Tool lists limit capabilities; path-level limits (such as "review agents write only their own report") are enforced by agent instructions and the Orchestrator's post-checks.

## Handoff packet
Subagents start with fresh context and know only what the packet and its listed files tell them. Every delegation includes:
```
HANDOFF
Workflow ID / Jira key:
Stage and agent:
Current branch: <output of git branch --show-current, verified by Orchestrator>
Goal for this invocation:
Input artifacts (paths): <only what is needed>
Approvals so far: <gate, status, date; quote user approval where relevant>
Relevant decisions / user clarifications: <quoted, not summarized away>
Scope: <TASK-### or FND-### to handle; revision round number>
Constraints: <user constraints, approved dependency installs>
Expected output: <artifact paths and the report format from the agent's definition>
```
- Pass paths and facts, not pasted documents. Do not make agents re-fetch Jira or re-discover known context.
- Never describe an approval that has not been given. Never ask an agent to skip its own checks.
- After each agent returns, verify its claims against the repository (`git status`, `git log`, diffs) before recording the stage complete. Check that only permitted files changed.

## Approval gates
Stop and obtain the user's explicit approval at exactly these gates; record the approver's words and date in `docs/workflow-state.md`.

| Gate | When | Approves |
|------|------|----------|
| G1 | Before finalizing requirements | `docs/requirements.md`, including answers to open questions |
| G2 | Before accepting the architecture | `docs/architecture.md` and ADRs |
| G3 | Before submitting the pull request | Pushing `development` and creating the PR to `main` |

- Silence, an approval for another artifact, or a general "go ahead" is not approval.
- Approval covers the artifact version shown. A material change (for example architecture changed by design review) reopens the gate.
- Agents never mark an artifact `Approved` and never record approvals.
- Also ask before: installing dependencies, adding technologies outside the approved architecture, creating or changing Jira issues, and any destructive or hard-to-reverse action.

## Sequence
1. **Intake**: check branch/tree, write `docs/user-story.md`, create the workflow ID, initialize state.
2. **Requirements** (`requirements-agent`) and **clarification**: relay questions, re-delegate with answers quoted until none block.
3. **G1**.
4. **Architecture** (`architecture-agent`), then **G2**.
5. **Design review** (`design-review-agent`; receives artifacts, not the author's rationale).
6. **Resolve design findings**: Blocker/Major go to `architecture-agent`, then re-review. Any architecture change reopens G2. User-owned decisions go to the user. Proceed with no open Blocker/Major, or on the user's explicit deferral.
7. **Planning** (`planning-agent`); resolve its questions first.
8. **Implementation** (`implementation-agent`) in scoped chunks of tasks; verify the report against `git status`/`git log`.
9. **Code review** (`code-review-agent`), then **resolve findings**: Blocker/Major to `implementation-agent`, re-review, repeat. Minor/Info are fixed or recorded as known limitations. Findings that reveal a requirements or architecture problem go to the user (reopen G1/G2).
10. **Verification** (`verification-agent`); failures go to `implementation-agent`, then re-run code review for changed code and verification. Proceed only on `Pass` for the current `HEAD`.
11. **G3**: tree clean on `development`; show the `pr-agent` `PREPARE` draft and ask for approval.
12. **PR submission**: `pr-agent` in `SUBMIT` mode with the user's quoted approval. Final report; never merge.

Loop limit: if the same finding survives three fix/re-review rounds, escalate to the user.
Do not skip or reorder steps without recording the reason in the workflow state and telling the user. Never silently change approved requirements.

## Workflow state
After every delegation, return and approval, update `docs/workflow-state.md`. It must show: current stage, completed and pending stages, G1-G3 status, agent execution status, artifact paths, review findings, test/verification status (with commit), blockers, and execution history. In a new session read it first and resume from it; reuse approved artifacts instead of redoing work.
