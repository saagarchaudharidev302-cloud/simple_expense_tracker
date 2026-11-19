# General Conventions

Apply to every session and every agent.

- **Application-agnostic.** This repository is a framework. Never hard-code a product, language, framework, database or architecture style into agents, skills, rules or hooks. The Architecture Agent selects the stack from the approved requirements and records it in an ADR.
- **Story-driven.** Every requirement, task and test traces to an acceptance criterion in `docs/user-story.md`.
- **No scope creep.** Do not add features, abstractions or dependencies the approved requirements do not need.
- **Simplicity first.** Prefer the simplest design that satisfies the requirements; justify added technology in an ADR.
- **Small, reversible increments.** Plan and implement in small tasks that can be reviewed independently.
- **Explicit over implicit.** Record assumptions, open questions and decisions in artifacts. Never silently guess; ask when blocked.
- **Independent review.** Reviewers and verifiers report problems; they do not fix what they review.
- **Evidence over claims.** Report only results that were actually observed.

## Code conventions (any stack)
- Follow the idiomatic conventions and standard formatter/linter of the chosen language, and match existing project code.
- Small, single-purpose functions with intention-revealing names.
- Handle errors explicitly. No swallowed exceptions or silent failures.
- No dead code, commented-out code or unexplained TODOs.
- Comments explain *why*, not *what*.
- Keep responses and artifacts concise and structured. Do not create files outside the documented structure without justification.
