#!/usr/bin/env bash
# PostToolUse hook of the ga-standards plugin.
# After Claude edits a .tmdl file of a semantic model, runs validators/validate_model.py on that
# model. Reports only findings on blocking standards in the edited file, and is silent when
# there are none. Only a warning: it never blocks an edit.
# Only acts in repositories whose CLAUDE.md imports the Group Analytics standards.

project_dir="${CLAUDE_PROJECT_DIR:-.}"
grep -qs "ga_analytics_standards/claude/" "$project_dir/CLAUDE.md" || exit 0

input=$(cat)
case "$input" in
  *.tmdl*) ;;
  *) exit 0 ;;
esac

# python3 on macOS; on Windows python3 is often only a Microsoft Store stub that fails.
python=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
    python="$candidate"
    break
  fi
done
if [ -z "$python" ]; then
  # Say it once per session, not after every edit.
  session=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  marker="${TMPDIR:-/tmp}/ga_model_check_no_python_${session:-unknown}"
  if [ ! -f "$marker" ]; then
    : > "$marker" 2>/dev/null
    printf '{"systemMessage":"Group Analytics model check skipped: Python 3.8 or later was not found. Install Python to get the check after model edits (see docs/getting-started.md)."}\n'
  fi
  exit 0
fi

printf '%s' "$input" | "$python" -B "$(dirname "$0")/../validators/validate_model.py" --hook 2>/dev/null
exit 0
