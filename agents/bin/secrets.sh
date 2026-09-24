#!/usr/bin/env bash
# Auth for the Collective, kept ENCRYPTED in the private repo (Charter Article 17.3).
# Plaintext agents/.env is never committed to either repo.
#   secrets.sh keygen   make the Steward's age key at ~/.config/age/collective.key (once, on Rex's Mac)
#   secrets.sh seal     encrypt agents/.env → private/secrets/env.age (for every recipient)
#   secrets.sh unseal   decrypt private/secrets/env.age → agents/.env (mode 600)
# Requires age (brew install age).
set -euo pipefail
cd "$(dirname "$0")/../.."
KEY="${AGE_KEY:-$HOME/.config/age/collective.key}"; REC=private/secrets/recipients.txt; OUT=private/secrets/env.age
command -v age >/dev/null || { echo "install age first: brew install age"; exit 1; }
case "${1:-}" in
  keygen) mkdir -p "$(dirname "$KEY")"; [ -f "$KEY" ] || age-keygen -o "$KEY" 2>/dev/null; chmod 600 "$KEY"
          mkdir -p private/secrets; grep -o 'age1[0-9a-z]*' "$KEY" | head -1 >> "$REC"; sort -u "$REC" -o "$REC"
          echo "key: $KEY (back it up somewhere safe; losing it means losing the sealed secrets)"; echo "recipient added to $REC";;
  seal)   [ -f agents/.env ] || { echo "no agents/.env"; exit 1; }
          age -R "$REC" -o "$OUT" agents/.env && echo "sealed → $OUT (commit it with repos.sh commit)";;
  unseal) age -d -i "$KEY" -o agents/.env "$OUT" && chmod 600 agents/.env && echo "unsealed → agents/.env";;
  *) sed -n '2,8p' "$0"; exit 1;;
esac
