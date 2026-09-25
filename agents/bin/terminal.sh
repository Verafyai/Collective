#!/usr/bin/env bash
# Open a terminal to talk with one agent (Charter Article 18.8; used by the dashboard's "Open terminal").
#   agents/bin/terminal.sh <agent-key> [--standalone]
# Inside herdr: a new tab labeled "talk: <key>". Otherwise (or with --standalone): a macOS Terminal window.
# Either way it runs agents/bin/run-role.sh <key> --interactive, which records the whole conversation.
set -euo pipefail
cd "$(dirname "$0")/../.."
KEY="${1:?agent key}"; MODE="${2:-auto}"
[[ "$KEY" =~ ^[a-z][a-z0-9]{1,15}$ ]] || { echo "REFUSED: not an agent key"; exit 1; }
python3 - "$KEY" <<'PY' || exit 1
import json, sys
a = next((a for a in json.load(open("agents/roster.json"))["agents"] if a["key"] == sys.argv[1]), None)
if not a: sys.exit(f"REFUSED: no agent '{sys.argv[1]}'")
if a["status"] != "active": sys.exit(f"REFUSED: {sys.argv[1]} is {a['status']}; only active agents can talk")
PY
ROOT="$(pwd)"; CMD="agents/bin/run-role.sh $KEY --interactive"
if [ "$MODE" != "--standalone" ] && [ -n "${HERDR_SOCKET_PATH:-}" ] && command -v herdr >/dev/null 2>&1; then
  out="$(herdr tab create --cwd "$ROOT" --label "talk: $KEY" --focus)"
  pane="$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["root_pane"]["pane_id"])')"
  herdr pane run "$pane" "$CMD" >/dev/null
  echo "opened a herdr tab \"talk: $KEY\""
elif command -v open >/dev/null 2>&1; then
  dir="$HOME/Library/Caches/collective"; mkdir -p "$dir"; f="$dir/talk-$KEY.command"
  printf '#!/bin/bash\ncd %q && exec %s\n' "$ROOT" "$CMD" > "$f"; chmod 700 "$f"
  open -a Terminal "$f"
  echo "opened a Terminal window to talk with $KEY"
else
  echo "run this in a terminal: cd $ROOT && $CMD"; exit 2
fi
