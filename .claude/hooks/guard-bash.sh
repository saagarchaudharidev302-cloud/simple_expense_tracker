#!/usr/bin/env bash
# PreToolUse hook for Bash. Purpose: deterministic Git safeguards from
# .claude/rules/git-workflow.md. Exit 2 blocks the command and shows the
# message on stderr to Claude. It matches on the raw hook JSON text, so it is
# a coarse safety net, not a parser; it cannot judge intent or approvals.
input=$(cat)

block() {
  echo "Blocked by .claude/hooks/guard-bash.sh: $1" >&2
  exit 2
}

has() { printf '%s' "$input" | grep -Eq -- "$1"; }

has 'git[[:space:]]+push[^"]*(--force|--force-with-lease|[[:space:]]-f([[:space:]]|"|$)|[[:space:]]\+)' \
  && block "force-push is never allowed."
has 'git[[:space:]]+push[^"]*([[:space:]:]|/)(main|master)([[:space:]"]|$)' \
  && block "pushing to main is not allowed; changes reach main only via an approved PR."
has 'git[[:space:]]+push[^"]*--delete' \
  && block "deleting remote branches is not allowed."
has 'git[[:space:]]+(checkout|switch)([[:space:]]+-[A-Za-z-]+)*[[:space:]]+(main|master)([[:space:]"]|$)' \
  && block "agents must not switch to main."
has 'git[[:space:]]+reset[^"]*--hard' \
  && block "git reset --hard can discard user changes."
has 'git[[:space:]]+clean' \
  && block "git clean can delete user files."
has 'git[[:space:]]+checkout[[:space:]]+--[[:space:]]' \
  && block "discarding working-tree changes is not allowed."
has 'git[[:space:]]+branch[[:space:]]+(-D|-d|--delete)' \
  && block "deleting branches is not allowed."
has '--no-verify' \
  && block "bypassing git hooks is not allowed."
has 'rm[[:space:]]+(-[A-Za-z]*r[A-Za-z]*f|-[A-Za-z]*f[A-Za-z]*r)' \
  && block "recursive forced deletion is not allowed."
has '(cat|type|less|more|head|tail|grep|source)[[:space:]][^|;&"]*\.env([[:space:]"]|$)' \
  && block "reading .env files is not allowed."

# Commits, merges and rebases are not allowed while main is checked out.
if has 'git[[:space:]]+(commit|merge|rebase|cherry-pick)'; then
  branch=$(git -C "${CLAUDE_PROJECT_DIR:-.}" branch --show-current 2>/dev/null)
  case "$branch" in
    main|master) block "no direct commits or merges on $branch; work on the development branch." ;;
  esac
fi

exit 0
