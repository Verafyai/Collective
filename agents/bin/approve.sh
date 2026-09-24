#!/usr/bin/env bash
# Rex approves (or rejects) an outbox draft. Usage: approve.sh <file> [--reject "reason"]
set -euo pipefail
cd "$(dirname "$0")/../.."
f="${1:?file in private/outbox/pending}"; b="$(basename "$f")"
[ -f "private/outbox/pending/$b" ] || { echo "not in private/outbox/pending: $b"; exit 1; }
if [ "${2:-}" = "--reject" ]; then
  mkdir -p private/outbox/rejected; mv "private/outbox/pending/$b" "private/outbox/rejected/$b"
  printf '\n\nRejected %s: %s\n' "$(date -Iseconds)" "${3:-}" >> "private/outbox/rejected/$b"; echo "rejected $b"
  python3 agents/bin/eventlog.py sync --actor steward --reason "reject $b" >/dev/null
  python3 agents/bin/eventlog.py record --actor steward --type approval.rejected --data "{\"file\": \"$b\"}"
else
  printf '\n\nApproved by rex %s\n' "$(date -Iseconds)" >> "private/outbox/pending/$b"
  mv "private/outbox/pending/$b" "private/outbox/approved/$b"; echo "approved $b"
  python3 agents/bin/eventlog.py sync --actor steward --reason "approve $b" >/dev/null
  python3 agents/bin/eventlog.py record --actor steward --type approval.granted --data "{\"file\": \"$b\"}"
fi
