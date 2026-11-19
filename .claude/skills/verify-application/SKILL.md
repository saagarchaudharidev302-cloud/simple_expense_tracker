---
name: verify-application
description: Execute tests and validation commands and check every acceptance criterion with evidence via verification-agent; route failures to implementation-agent and re-verify.
disable-model-invocation: true
---

# /verify-application

Stage: Verification and failure resolution. Agents: `verification-agent`, then `implementation-agent` for fixes.

## Inputs
- Code that passed code review (no open Blocker/Major), approved requirements, `docs/impl-plan.md`.

## Steps
1. Verify branch is `development` and the working tree is clean of unrelated changes. Note `HEAD`.
2. Delegate to `verification-agent` with the packet: artifact paths, the ACs to verify, the `HEAD` hash, and any user-approved install/setup constraints.
3. Verify only `docs/verification-report.md` changed and the report cites actual commands and output, separating executed, passed, failed, skipped and not-run.
4. On failures: send them to `implementation-agent` (`/implement-feature` with FND ids), re-run `/review-code` for the changed code, then re-verify.
5. Proceed only on a `Pass` for the current `HEAD`. Any later commit makes the result stale. Record results and commit hash in the workflow state.

## Output
`docs/verification-report.md` with a `Pass` for current `HEAD`; updated workflow state.

## Constraints
- The verifier never fixes code and never fabricates results.
- Same failure surviving three rounds: escalate to the user.
