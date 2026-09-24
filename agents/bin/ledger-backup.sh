#!/usr/bin/env bash
# Verify the event log, then back it up (Charter Articles 12.8 and 17):
# commit and push the private repo (CollectivePrivate), plus an optional extra
# copy to LEDGER_BACKUP_DEST.
set -euo pipefail
cd "$(dirname "$0")/../.."
[ -f agents/config.env ] && source agents/config.env
python3 agents/bin/eventlog.py verify
git -C private add -A && git -C private commit -qm "Ledger backup $(date -Is)" || true
git -C private push -q -u origin HEAD && echo "private repo pushed"
[ -n "${LEDGER_BACKUP_DEST:-}" ] && rsync -a private/ledger/ "$LEDGER_BACKUP_DEST/" && echo "extra copy → $LEDGER_BACKUP_DEST"
python3 agents/bin/eventlog.py record --actor system --type ledger.backup --data "{\"summary\": \"ledger verified and backed up\"}"
