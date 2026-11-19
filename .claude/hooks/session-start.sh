#!/usr/bin/env bash
# SessionStart hook. Purpose: show the Orchestrator the current branch and
# workflow stage at session start. Read-only; stdout is added to the context.
root="${CLAUDE_PROJECT_DIR:-.}"
branch=$(git -C "$root" branch --show-current 2>/dev/null)
echo "SDLC framework: current branch is '${branch:-unknown}' (workflow work must happen on 'development')."
if [ -f "$root/docs/workflow-state.md" ]; then
  grep -m 2 -E '^\| (Current stage|Workflow status) ' "$root/docs/workflow-state.md"
  echo "Read docs/workflow-state.md before acting. Use /start-sdlc to start or resume."
fi
exit 0
