---
name: analyze-requirements
description: Run requirements analysis on docs/user-story.md via requirements-agent, relay clarification questions to the user, and obtain approval gate G1 for docs/requirements.md.
disable-model-invocation: true
---

# /analyze-requirements

Stage: Requirements, clarification and gate **G1**. Agent: `requirements-agent`.

## Inputs
- `docs/user-story.md` (must exist; if not, ask the user for the story).
- `docs/workflow-state.md` (workflow ID, Jira key).

## Steps
1. Verify branch is `development` (`git branch --show-current`).
2. Delegate to `requirements-agent` with a handoff packet (see `.claude/rules/agent-orchestration.md`): story path, workflow ID/key, any prior user answers quoted, and for revisions the previous requirements and feedback.
3. Verify with `git status` that only `docs/requirements.md` changed.
4. If the report has `QUESTIONS FOR USER`, present them to the user (use AskUserQuestion for choice-style questions). Re-delegate with the answers quoted verbatim. Repeat until no blocking question remains.
5. **G1.** Show the user the requirements (summary, open items, assumptions) and ask for explicit approval. On approval, set `docs/requirements.md` status to `Approved` and record the quote and date in the workflow state. If the user asks for changes, re-delegate and ask again.

## Output
Approved `docs/requirements.md`; updated workflow state.

## Constraints
- Never change or reword acceptance criteria yourself; do not decide open questions for the user.
- Do not proceed to architecture without G1.
