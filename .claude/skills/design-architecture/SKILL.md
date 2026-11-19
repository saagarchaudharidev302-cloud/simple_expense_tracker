---
name: design-architecture
description: Produce docs/architecture.md and ADRs from approved requirements via architecture-agent, then obtain approval gate G2.
disable-model-invocation: true
---

# /design-architecture

Stage: Architecture and gate **G2**. Agent: `architecture-agent`.

## Inputs
- `docs/requirements.md` with status `Approved` (G1 recorded). If not approved, stop and run `/analyze-requirements` first.
- For revisions: `docs/design-review.md` findings (Blocker/Major) or the user's change requests.

## Steps
1. Verify branch is `development`.
2. Delegate to `architecture-agent` with a handoff packet: requirements path, G1 approval quote, user constraints (stack preferences, approved dependencies), and for revisions the exact findings or requests to address.
3. Verify with `git status` that only `docs/architecture.md` and `docs/decisions/*` changed.
4. **G2.** Present the architecture (stack choice and rationale, components, data, key ADRs, risks) and ask for explicit approval. Resolve the agent's open questions with the user first. On approval, set `docs/architecture.md` to `Approved` and record the quote and date. If changes are requested, re-delegate and ask again.

## Output
Approved `docs/architecture.md` and `docs/decisions/*`; updated workflow state.

## Constraints
- The stack comes from the requirements; do not impose a language, framework or database yourself.
- Any later architecture change reopens G2.
