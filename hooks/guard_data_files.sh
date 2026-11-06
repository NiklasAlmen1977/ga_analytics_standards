#!/usr/bin/env bash
# PreToolUse hook of the ga-standards plugin.
# Stops Claude from reading files that normally hold data rather than code or metadata
# (Power BI cache, exports, extracts), so that the data is not sent to the model.
# It covers Read and Grep, and Bash or PowerShell commands that print file contents.
# Maintainers only, for testing: start Claude Code with GA_ALLOW_DATA_FILES=1 to switch it off.

[ "${GA_ALLOW_DATA_FILES:-}" = "1" ] && exit 0

input=$(tr -d '\r\n')
tool=$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
# Only look at what the tool is asked to do, not at session fields such as transcript_path.
tool_input=$(printf '%s' "$input" | sed -n 's/.*"tool_input"[[:space:]]*:\(.*\)/\1/p')

data_ext='\.(abf|pbix|csv|tsv|parquet|avro|orc|xlsx|xlsm|xlsb|xls)([^A-Za-z0-9_]|$)'
readers='(^|[^A-Za-z0-9_-])(cat|head|tail|less|more|type|gc|Get-Content|Import-Csv|Import-Excel|Select-String|sed|awk|grep|rg|sort|cut|uniq|strings|xxd|od|python|python3|py|node|duckdb|sqlite3)([^A-Za-z0-9_-]|$)|git[[:space:]]+(diff|show|blame|cat-file)'

blocked=0
case "$tool" in
  Read|Grep)
    # Only the file arguments count; a Grep search pattern that mentions a data file is metadata.
    files=$(printf '%s' "$tool_input" | grep -Eo '"(file_path|path|glob)"[[:space:]]*:[[:space:]]*"[^"]*"')
    printf '%s' "$files" | grep -Eiq "$data_ext" && blocked=1
    ;;
  Bash|PowerShell)
    if printf '%s' "$tool_input" | grep -Eiq "$data_ext" && printf '%s' "$tool_input" | grep -Eq "$readers"; then
      blocked=1
    fi
    ;;
esac

if [ "$blocked" = "1" ]; then
  reason="Blocked by the Group Analytics data guard: data files (.abf, .pbix, .csv, .tsv, .parquet, .xlsx and similar) can hold business or personal data and are not sent to Claude. Instead: describe the structure, or use an anonymised sample. If the file only holds metadata, tell the developer; questions go to dataprotection@vitrolife.com."
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
fi

exit 0
