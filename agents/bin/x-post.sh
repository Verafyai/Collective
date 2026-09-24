#!/usr/bin/env bash
# Post an APPROVED outbox item to X. Refuses anything outside private/outbox/approved.
# The actual API call is implemented by the setup agent in agents/bin/x_post.py
# (official X API, credentials from agents/.env). This wrapper is the gate.
set -euo pipefail
cd "$(dirname "$0")/../.."
f="${1:?approved file}"; b="$(basename "$f")"
[ -f "private/outbox/approved/$b" ] || { echo "REFUSED: $b is not in private/outbox/approved"; exit 1; }
grep -q "Approved by rex" "private/outbox/approved/$b" || { echo "REFUSED: no approval stamp"; exit 1; }
[ -f org/STOP ] && { echo "REFUSED: org/STOP present"; exit 1; }
set -a; source agents/.env; set +a
url="$(python3 agents/bin/x_post.py "private/outbox/approved/$b" | tail -1)"
mv "private/outbox/approved/$b" "private/outbox/posted/$b"
# External effect: recorded, never re-executed on replay (Charter 12.4)
python3 agents/bin/eventlog.py sync --actor social --reason "posted $b" >/dev/null
python3 agents/bin/eventlog.py record --actor social --type effect.posted --data "{\"file\": \"$b\", \"url\": \"$url\"}"
