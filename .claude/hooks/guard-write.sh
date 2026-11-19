#!/usr/bin/env bash
# PreToolUse hook for Write/Edit. Purpose: (1) never write .env files other
# than .env.example, (2) keep application code and tests (src/, tests/) off
# any branch except development. Exit 2 blocks and explains on stderr.
input=$(cat)

block() {
  echo "Blocked by .claude/hooks/guard-write.sh: $1" >&2
  exit 2
}

# Windows paths arrive JSON-escaped (C:\\Users\\...); normalize to /c/Users/...
norm() {
  printf '%s' "$1" | sed -e 's#\\\\#/#g' -e 's#\\#/#g' -e 's#^\([A-Za-z]\):#/\L\1#'
}

file=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
[ -z "$file" ] && exit 0

path=$(norm "$file")
root=$(norm "${CLAUDE_PROJECT_DIR:-$PWD}")
rel=${path#"$root"/}
name=${path##*/}

case "$name" in
  .env.example) ;;
  .env|.env.*) block "writing $name is not allowed; secrets stay out of the repository." ;;
esac

case "$rel" in
  src/*|tests/*)
    branch=$(git -C "${CLAUDE_PROJECT_DIR:-.}" branch --show-current 2>/dev/null)
    [ "$branch" = "development" ] \
      || block "application code and tests may only change on the development branch (current: ${branch:-detached/unknown})."
    ;;
esac

exit 0
