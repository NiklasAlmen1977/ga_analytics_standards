#!/usr/bin/env bash
# PreToolUse hook of the ga-standards plugin.
# Blocks the tools of MCP servers for Power BI and Fabric, such as the Power BI Modeling MCP.
# They can query the data in a semantic model, and their use is not approved during the pilot.
# There is no switch to turn this off: remove the block in the plugin once the use is approved.

input=$(tr -d '\r\n')
tool=$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

if printf '%s' "$tool" | grep -Eiq '^mcp__.*(powerbi|power_bi|fabric)'; then
  reason="Blocked by the Group Analytics pilot rules: MCP servers for Power BI and Fabric are not approved yet, because they can send model data to Claude. Work on the PBIP files (TMDL and PBIR) instead."
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
fi

exit 0
