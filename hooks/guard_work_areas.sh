#!/usr/bin/env bash
# Hook of the ga-standards plugin: one work area per session, for repositories that hold more than
# one kind of work (for example Engineering, Data models and Reports in a landing zone repository).
# Acts only in repositories with .claude/work_areas.conf; elsewhere it does nothing.
#
# .claude/work_areas.conf, one line per work area (# starts a comment):
#   <work area name> | <folder> | <folders that are blocked in this work area, space separated>
#   Engineering      | Engineering/ | Data_models/ Reports/
#
# Called with one argument:
#   start   SessionStart: Claude asks the developer for the work area (or shows it on resume)
#   record  PostToolUse on AskUserQuestion: stores the developer's answer to the work area question
#   prompt  UserPromptSubmit: the developer can also type "work area: <name>" to choose or switch
#   check   PreToolUse: blocks file edits, and shell commands that write files, in a blocked folder;
#           before a work area is chosen, all folders in the file are blocked
# Only the developer's answer sets the work area; the state is kept outside the repository, and
# Claude cannot change it or .claude/work_areas.conf. Shell commands are checked by keywords (a folder name plus a writing
# command): a guard, not a sandbox.

action="$1"
input=$(tr -d '\r\n')

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
config="$project_dir/.claude/work_areas.conf"
[ -f "$config" ] || exit 0

repo=$(basename "$project_dir")
session_id=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
state_dir="${TMPDIR:-${TEMP:-/tmp}}/ga-standards-work-areas"
state_file="$state_dir/${session_id:-unknown}"
question="Which work area of $repo do you work on in this session?"

# Lowercase path with forward slashes, a c:/ style drive and no trailing slash, for comparisons
norm() {
  printf '%s' "$1" | sed 's#\\\\#/#g; s#\\#/#g' | tr 'A-Z' 'a-z' | sed 's#^/\([a-z]\)/#\1:/#; s#/*$##'
}

# Work areas from the file: name|folder|blocked, trimmed, without comments and empty lines
areas=$(sed 's/#.*//; s/[[:space:]]*|[[:space:]]*/|/g; s/^[[:space:]]*//; s/[[:space:]]*$//' "$config" | tr -d '\r' | grep '|')
[ -n "$areas" ] || exit 0
names=$(printf '%s\n' "$areas" | cut -d'|' -f1)
names_list=$(printf '%s\n' "$names" | sed "s/.*/'&'/" | paste -sd, - | sed 's/,/, /g')
names_regex=$(printf '%s\n' "$names" | paste -sd'|' -)

field_of() {
  printf '%s\n' "$areas" | awk -F'|' -v n="$(printf '%s' "$1" | tr 'A-Z' 'a-z')" -v f="$2" 'tolower($1) == n { print $f; exit }'
}

context() {
  printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"%s"}}\n' "$1" "$2"
}

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

save_area() {
  mkdir -p "$state_dir"
  printf '%s\n' "$1" > "$state_file"
}

switch_hint="The developer switches by typing: work area: <name>."

case "$action" in
  start)
    mkdir -p "$state_dir"
    find "$state_dir" -type f -mtime +14 -delete 2>/dev/null
    if [ -f "$state_file" ]; then
      context "SessionStart" "Work area for this session: $(cat "$state_file"). Edits in its blocked folders are stopped by the ga-standards work area guard. $switch_hint"
    else
      context "SessionStart" "This repository has work areas (.claude/work_areas.conf). In your first answer, before any change, ask the developer with AskUserQuestion, header 'Work area', exactly this question: '$question' with exactly these option labels: $names_list (ask it in the same AskUserQuestion call as the mode question). A hook stores the answer; until then edits in the work area folders are blocked. Each work area blocks edits in the folders listed for it in .claude/work_areas.conf. $switch_hint Never try to get around the guard."
    fi
    ;;

  record)
    answer=$(printf '%s' "$input" | grep -Eo "in this session\\?\\\\*\"[[:space:]]*[:=][[:space:]]*\\\\*\"($names_regex)" | tail -n 1 | grep -Eo "($names_regex)\$")
    [ -n "$answer" ] || exit 0
    save_area "$answer"
    context "PostToolUse" "Work area set to $answer by the developer. Edits in its blocked folders are now stopped."
    ;;

  prompt)
    prompt=$(printf '%s' "$input" | sed -n 's/.*"prompt"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    choice=$(printf '%s' "$prompt" | sed -n 's/^[[:space:]]*[Ww]ork area:[[:space:]]*\(.*[^[:space:]]\)[[:space:]]*$/\1/p' | tr '_' ' ')
    [ -n "$choice" ] || exit 0
    name=$(field_of "$choice" 1)
    [ -n "$name" ] || exit 0
    save_area "$name"
    context "UserPromptSubmit" "The developer set the work area to $name. Edits in its blocked folders are now stopped."
    ;;

  check)
    tool=$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    tool_input=$(printf '%s' "$input" | sed -n 's/.*"tool_input"[[:space:]]*:\(.*\)/\1/p')
    state_reason="The work area is set by the developer's answer only and cannot be changed by Claude."
    config_reason="The work areas in .claude/work_areas.conf are changed by the developer, not by Claude: tell the developer what to change."

    area=""
    [ -f "$state_file" ] && area=$(cat "$state_file")
    if [ -n "$area" ]; then
      blocked=$(field_of "$area" 3)
      why="Work area is $area: this change is in a folder that is blocked for it. If the change is intended, ask the developer to switch (type: work area: <name>)."
    else
      blocked=$(printf '%s\n' "$areas" | cut -d'|' -f2 | paste -sd' ' -)
      why="No work area chosen for this session yet. Ask the developer: '$question' ($names_list), or let them type: work area: <name>."
    fi

    case "$tool" in
      Edit|Write|MultiEdit|NotebookEdit)
        path=$(norm "$(printf '%s' "$tool_input" | sed -n 's/.*"\(file_path\|notebook_path\)"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\2/p')")
        case "$path" in *ga-standards-work-areas*) deny "$state_reason" ;; esac
        root=$(norm "$project_dir")
        [ "$path" = "$root/.claude/work_areas.conf" ] && deny "$config_reason"
        for folder in $blocked; do
          folder=$(norm "$folder")
          case "$path/" in "$root/$folder/"*) deny "$why" ;; esac
        done
        ;;
      Bash|PowerShell)
        # The description is free text; only the command itself counts
        command=$(norm "$(printf '%s' "$tool_input" | sed 's/"description"[[:space:]]*:[[:space:]]*"[^"]*"//')")
        case "$command" in *ga-standards-work-areas*) deny "$state_reason" ;; esac
        writes='(^|[^a-z_-])(rm|mv|cp|touch|mkdir|rmdir|tee|truncate|ln|remove-item|move-item|copy-item|new-item|rename-item|set-content|add-content|clear-content|out-file)([^a-z_-]|$)|sed[[:space:]]+-i|(^|[^0-9&])>|git[[:space:]]+(checkout|restore|rm|mv|reset|clean|stash|apply|am|cherry-pick|revert|merge|rebase|pull)'
        printf '%s' "$command" | grep -Eq "$writes" || exit 0
        case "$command" in *work_areas.conf*) deny "$config_reason" ;; esac
        for folder in $blocked; do
          folder=$(norm "$folder")
          printf '%s' "$command" | grep -Eq "(^|[^a-z0-9_])$folder(/|[\"' ]|\$)" && deny "$why (The command writes files and mentions $folder/.)"
        done
        ;;
    esac
    ;;
esac

exit 0
