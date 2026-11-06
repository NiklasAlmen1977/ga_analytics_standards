#!/usr/bin/env bash
# SessionStart hook of the ga-standards plugin.
# Shows where the session is connected: repository, branch, Jira ticket (from the branch name),
# uncommitted changes and the plugin version, and points to the ga-start skill.
# Only acts in repositories whose CLAUDE.md imports the Group Analytics standards.

project_dir="${CLAUDE_PROJECT_DIR:-.}"
grep -qs "ga_analytics_standards/claude/" "$project_dir/CLAUDE.md" || exit 0

repo=$(basename "$(cd "$project_dir" && pwd)")
branch=$(git -C "$project_dir" branch --show-current 2>/dev/null)
changes=$(git -C "$project_dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
ticket=$(printf '%s' "$branch" | sed -n 's/^feature_\([A-Za-z][A-Za-z0-9]*-[0-9][0-9]*\)_.*/\1/p')
version=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/.claude-plugin/plugin.json" 2>/dev/null | head -n 1)

status="Connected to $repo"
status="$status - branch ${branch:-(none)}"
[ -n "$ticket" ] && status="$status - ticket $ticket"
status="$status - $changes uncommitted change(s) - ga-standards ${version:-?}"

if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  hint="You are on $branch. Start with /ga-standards:ga-start to pick a Jira ticket and create a feature branch."
else
  hint="Type /ga-standards:ga-start to choose what to work on, or describe your task."
fi

context="$status. $hint If the user's first message does not say what to work on, offer the ga-start skill before doing anything else."

printf '{"systemMessage":"%s\\n%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
  "$(printf '%s' "$status" | sed 's/"/\\"/g')" "$hint" "$(printf '%s' "$context" | sed 's/"/\\"/g')"
exit 0
