#!/usr/bin/env bash
# SessionStart hook of the ga-standards plugin.
# Makes sure the shared Group Analytics repositories are cloned next to the project repository
# and that their main branch is up to date:
#   ga_analytics_standards - instructions and naming rules imported by the project's CLAUDE.md
#   ga_templates_pbi       - the PBIP template copied into new projects
# Also says when a newer version of this plugin is available and how to update it.
# Messages are shown to the user (systemMessage) and given to Claude as context.

base_url="${GA_REPO_BASE_URL:-https://vitrolife-group.ghe.com/group-analytics}"  # override only for tests
project_dir="${CLAUDE_PROJECT_DIR:-.}"
export GIT_TERMINAL_PROMPT=0

# Only act in repositories whose CLAUDE.md imports the standards from the sibling clone.
if ! grep -qs "ga_analytics_standards/claude/" "$project_dir/CLAUDE.md"; then
  exit 0
fi

restart_how="VS Code: open a new Claude Code tab; terminal: start claude again"
messages=""
add() { messages="${messages:+$messages\n}$1"; }

# sync <repo name> <restart needed when it changes: yes|no>
sync() {
  local name="$1" restart="$2" target="$project_dir/../$1" branch before where
  local after_note=""
  [ "$restart" = "yes" ] && after_note=" Restart Claude Code to load it ($restart_how)."

  if [ ! -d "$target/.git" ]; then
    if git clone --quiet "$base_url/$name.git" "$target" 2>/dev/null; then
      add "ACTION: $name was cloned next to this repository.$after_note"
    else
      add "WARNING: $name was not found next to this repository and could not be cloned from $base_url/$name.git."
    fi
    return
  fi

  # Only update main, so that work in progress on another branch is never touched.
  branch=$(git -C "$target" branch --show-current)
  if [ "$branch" != "main" ]; then
    if [ -n "$branch" ]; then where="branch '$branch'"; else where="a detached HEAD"; fi
    add "NOTE: $name is on $where, not main, and was not updated."
    return
  fi

  before=$(git -C "$target" rev-parse HEAD)
  if ! { git -C "$target" fetch --quiet origin main && git -C "$target" merge --ff-only --quiet origin/main; } >/dev/null 2>&1; then
    add "WARNING: Could not update $name (no network access, or local changes on main). It may be out of date."
    return
  fi
  if [ "$(git -C "$target" rev-parse HEAD)" != "$before" ]; then
    add "ACTION: $name was updated to the latest main.$after_note"
  fi
}

sync ga_analytics_standards yes
sync ga_templates_pbi no

# The plugin runs from Claude Code's own copy of the marketplace. With autoUpdate on (project
# settings), Claude Code refreshes it in the background up to ten minutes after the first
# message, and the new version loads with /reload-plugins or in the next session. Say so when
# main of the standards holds a newer plugin version than the installed one, with the manual
# commands as a fallback (for example when git needs a login prompt).
plugin_version() {
  sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$1/.claude-plugin/plugin.json" 2>/dev/null | head -n 1
}
standards="$project_dir/../ga_analytics_standards"
if [ "$(git -C "$standards" branch --show-current 2>/dev/null)" = "main" ]; then
  installed=$(plugin_version "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}")
  latest=$(plugin_version "$standards")
  if [ -n "$installed" ] && [ -n "$latest" ] && [ "$installed" != "$latest" ] \
    && [ "$(printf '%s\n%s\n' "$installed" "$latest" | sort -V | tail -n 1)" = "$latest" ]; then
    add "NOTE: The ga-standards plugin is $installed and $latest is available. Claude Code updates it automatically within about 10 minutes after your first message; when it says 'Plugin updated', type /reload-plugins. Only if the next session still shows $installed, run these two commands in a terminal in this repository folder, then restart Claude Code ($restart_how):"
    add "  claude plugin marketplace update ga-collection"
    add "  claude plugin update ga-standards@ga-collection -s project"
  fi
fi

[ -z "$messages" ] && exit 0
# Messages hold no backslashes except the \n separators, so only quotes need escaping for JSON.
msg=$(printf '%s' "$messages" | sed 's/"/\\"/g')
printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$msg" "$msg"
exit 0
