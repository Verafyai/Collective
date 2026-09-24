#!/usr/bin/env bash
# Publish a closed amendment's record in the PUBLIC repo (Charter Articles 11 and 17).
# Usage: gov-publish.sh governance/records/A-NNNN [--dry-run]
# Refuses if the record is incomplete or the redaction scan finds anything.
set -euo pipefail
cd "$(dirname "$0")/../.."
REC="${1:?record dir}"; DRY="${2:-}"; ID="$(basename "$REC")"
for f in proposal.md amendment.json positions debate.md ballots tally.json tally.md decision.md; do
  [ -e "$REC/$f" ] || { echo "REFUSED: $REC/$f missing (record incomplete)"; exit 1; }
done
hits="$(grep -rInE \
  -e '(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9_-]{20,}' -e 'gh[pous]_[A-Za-z0-9]{30,}' -e 'xox[abprs]-' -e 'AKIA[0-9A-Z]{16}' \
  -e '(API|SECRET|TOKEN|PASSWORD)[A-Z_]*=[^[:space:]]{6,}' -e '[Bb]earer [A-Za-z0-9._~+/=-]{16,}' \
  -e '\[\s*([0-9]{1,3}\s*,\s*){63}[0-9]{1,3}\s*\]' \
  -e '/(Users|home)/[A-Za-z0-9._-]+' \
  -e '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' \
  "$REC" org/cases | grep -vE '@example\.com|/(home|Users)/(user[0-9]+|USER)\b' || true)"
if [ -n "$hits" ]; then
  echo "REFUSED: redaction scan found possible sensitive data:"; echo "$hits" | cut -c1-160
  printf '#incident\n### scribe · %s\nPublication of %s blocked by redaction scan. @rex please review.\n' "$(date -Is)" "$ID" \
    > "private/incidents/$(date +%F)-publish-$ID.md"
  exit 2
fi
if command -v gitleaks >/dev/null; then gitleaks detect --no-git --source "$REC" || { echo "REFUSED: gitleaks"; exit 2; }; fi
if [ "$DRY" = "--dry-run" ]; then echo "DRY: would publish $REC in the public repo"; exit 0; fi
python3 agents/bin/charter.py timeline >/dev/null
{ echo "# The Collective · governance records"; echo
  echo "Charter: [CHARTER.md](CHARTER.md) · structure over time: [charter/TIMELINE.md](charter/TIMELINE.md) · every version: [charter/history](charter/history) · case law: [org/cases/INDEX.md](org/cases/INDEX.md)"; echo
  echo "| Amendment | Class | Outcome |"; echo "|---|---|---|"
  for t in governance/records/*/tally.json; do
    [ -f "$t" ] && python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(f\"| [{d['id']}](records/{d['id']}/tally.md) | {d['class']} | {d['outcome']} |\")" "$t"
  done; } > governance/RECORDS.md
agents/bin/repos.sh commit "Publish governance record $ID"
python3 agents/bin/eventlog.py record --actor scribe --type governance --data "{\"summary\": \"published $ID\", \"amendment\": \"$ID\"}"
agents/bin/repos.sh push
