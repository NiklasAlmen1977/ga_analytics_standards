#!/usr/bin/env bash
# SessionStart hook of the ga-standards plugin.
# Shows the Vitrolife AI rules (claude/session_rules.md) when a session starts: in full at
# startup, as a three-line reminder on resume and clear. Shows the permission mode, and at
# startup asks Claude to let the developer choose the mode once. Claude always gets the full
# rules as context. Warns when the session runs in auto or bypass mode.

input=$(tr -d '\r\n')
mode=$(printf '%s' "$input" | sed -n 's/.*"permission_mode"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
source=$(printf '%s' "$input" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

rules_file="${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}/claude/session_rules.md"
[ -f "$rules_file" ] || exit 0

# Escape the rules as a JSON string: backslashes, quotes, tabs and line breaks.
rules=$(awk '{ gsub(/\r/, ""); gsub(/\\/, "\\\\"); gsub(/"/, "\\\""); gsub(/\t/, " "); printf "%s\\n", $0 }' "$rules_file")

shown="$rules"
if [ "$source" != "startup" ]; then
  shown="Vitrolife AI rules apply (shown in full at startup): no patient, genetic, MAR or other restricted data.\\nData files and the Power BI and Fabric MCP servers are blocked; Claude works on the PBIP metadata.\\nQuestions: dataprotection@vitrolife.com\\n"
fi

case "$mode" in
  acceptEdits) mode_name="Edit automatically" ;;
  plan) mode_name="Plan" ;;
  auto) mode_name="Auto" ;;
  bypassPermissions) mode_name="Bypass permissions" ;;
  *) mode_name="Ask before edits" ;;
esac
shown="${shown}\\nMode: $mode_name. Ask before edits: you approve every change and command. Edit automatically: file changes in this repository are made without asking; commands, web access and other folders still ask; review with git diff before you commit. Auto and bypass are off in the pilot."

warning=""
ask=""
case "$mode" in
  auto|bypassPermissions)
    warning="\\nWARNING: this session runs in '$mode_name' mode, which the pilot does not allow: switch to 'Ask before edits' or 'Edit automatically' in the mode menu under the prompt box."
    ;;
esac
if [ "$source" = "startup" ]; then
  ask="\\n\\nAt the start of this session, in your first answer and before any change, ask the developer once (AskUserQuestion) which mode to work in: 'Ask before edits' (approve every change; recommended when new or for sensitive work) or 'Edit automatically' (file changes in this repository without asking; commands, web access and other folders still ask; review with git diff before commit; git can undo). The session now runs in '$mode_name'. Claude cannot switch the mode: the developer switches it in the mode menu under the prompt box (VS Code) or with Shift+Tab (terminal). Auto and bypass are not allowed in the pilot. Then continue with the developer's request, or offer ga-start."
fi

context="The user was shown the Vitrolife AI rules below at session start. Follow them in this session and warn the user when a request would break them.\\n\\n$rules$warning$ask"

printf '{"systemMessage":"%s%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
  "$shown" "$warning" "$context"

exit 0
