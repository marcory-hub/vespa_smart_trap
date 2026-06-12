#!/bin/bash
# Project hook: gate destructive shell commands (VST safety policy).
# stdin: JSON with .command field (beforeShellExecution).

set -euo pipefail

input=$(cat)
command=""
if command -v jq >/dev/null 2>&1; then
  command=$(echo "$input" | jq -r '.command // empty')
else
  command=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("command",""))' <<<"$input" 2>/dev/null || true)
fi

deny() {
  local user_message="$1"
  local agent_message="$2"
  printf '%s\n' "{\"permission\":\"deny\",\"user_message\":\"$user_message\",\"agent_message\":\"$agent_message\"}"
  exit 0
}

ask() {
  local user_message="$1"
  local agent_message="$2"
  printf '%s\n' "{\"permission\":\"ask\",\"user_message\":\"$user_message\",\"agent_message\":\"$agent_message\"}"
  exit 0
}

# Git rebase forbidden (global-rules.mdc)
if echo "$command" | grep -qE '(^|[[:space:]])git[[:space:]]+rebase|git[[:space:]]+pull[[:space:]]+--rebase|pull\.rebase'; then
  deny \
    "git rebase is blocked by project policy. Use git pull --no-rebase (merge) instead." \
    "Hook denied git rebase per global-rules.mdc."
fi

# Flash / esptool overwrite risk
if echo "$command" | grep -qiE 'esptool|xmodem|output\.img|\.tflite'; then
  if echo "$command" | grep -qiE 'write_flash|flash|xmodem'; then
    ask \
      "WARNING: Irreversible operation. Flash may overwrite GV2 firmware or model slots. Approve to continue?" \
      "Hook flagged a possible GV2 flash command. Confirm with user before running."
  fi
fi

# Destructive rm
if echo "$command" | grep -qE '(^|[[:space:]])rm[[:space:]]+(-[^[:space:]]*r|-[^[:space:]]*f|--recursive|--force)'; then
  ask \
    "WARNING: Irreversible operation. rm may delete data permanently. Approve to continue?" \
    "Hook flagged recursive or forced rm."
fi

# rsync --delete
if echo "$command" | grep -qE 'rsync.*--delete'; then
  ask \
    "WARNING: Irreversible operation. rsync --delete may remove destination files. Approve to continue?" \
    "Hook flagged rsync --delete."
fi

printf '%s\n' '{"permission":"allow"}'
exit 0
