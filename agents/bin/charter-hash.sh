#!/usr/bin/env bash
# Print the SHA-256 of CHARTER.md as it stands now (record this in the next
# Amendment Log entry BEFORE appending the entry), and the last entry's hash.
set -euo pipefail
cd "$(dirname "$0")/../.."
now=$( (command -v sha256sum >/dev/null && sha256sum CHARTER.md || shasum -a 256 CHARTER.md) | awk '{print $1}')
prev=$(grep -Eo 'entry_hash: [0-9a-f]{64}' CHARTER.md | tail -1 | awk '{print $2}')
echo "charter_sha256_before_entry: $now"
echo "prev_entry_hash: ${prev:-GENESIS}"
echo "entry_hash = sha256(prev_entry_hash + charter_sha256_before_entry + amendment_id):"
printf '%s%s%s' "${prev:-GENESIS}" "$now" "${1:-A-XXXX}" | (command -v sha256sum >/dev/null && sha256sum || shasum -a 256) | awk '{print "entry_hash: "$1}'
