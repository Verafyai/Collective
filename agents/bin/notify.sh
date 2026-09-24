#!/usr/bin/env bash
# Send the Steward a short notification (Charter Part III R8; NOTIFY_CMD in agents/config.env).
#   agents/bin/notify.sh "Title" ["Body"]
# Local only for now (edict E-0039: no Telegram yet): a herdr notification when herdr is
# reachable, otherwise a macOS notification. Every notification is also recorded as an event.
# Text is passed as arguments, never interpolated into a script. Never send secrets through this.
set -euo pipefail
cd "$(dirname "$0")/../.."
clean() { printf '%s' "$1" | LC_ALL=C tr -d '\000-\010\013-\037\177' | cut -c1-"$2"; }
title="$(clean "${1:?title}" 80)"; body="$(clean "${2:-}" 400)"
sent=""
if command -v herdr >/dev/null 2>&1 && herdr notification show "$title" --body "$body" --sound request >/dev/null 2>&1; then
  sent="herdr"
elif command -v osascript >/dev/null 2>&1 && osascript -e 'on run argv' -e 'display notification (item 2 of argv) with title (item 1 of argv)' -e 'end run' "$title" "$body" >/dev/null 2>&1; then
  sent="macos"
fi
python3 agents/bin/eventlog.py record --actor system --type notify.sent \
  --data "$(python3 -c 'import json,sys; print(json.dumps({"summary": sys.argv[1], "via": sys.argv[2] or "none"}))' "$title" "$sent")" >/dev/null 2>&1 || true
[ -n "$sent" ] && echo "notified via $sent: $title" || { echo "no notification channel available (recorded on the event log only)"; exit 1; }
