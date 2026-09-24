#!/usr/bin/env bash
# Download (if missing) and verify every library PDF against the manifest in LIBRARY.md.
# PDFs live in the private repo (private/library/pdfs) because of licensing.
set -euo pipefail
cd "$(dirname "$0")"; PDFS="../../private/library/pdfs"; mkdir -p "$PDFS"; fail=0
sha() { (command -v sha256sum >/dev/null && sha256sum "$1" || shasum -a 256 "$1") | awk '{print $1}'; }
while read -r name url want; do
  if [ ! -f "$PDFS/$name" ]; then
    if [ "$url" = "private" ]; then echo "MISSING $name (private document: restore it from the private repo)"; fail=1; continue; fi
    echo "fetching $name"; curl -sfL -A "verafy-library" -o "$PDFS/$name" "$url"; sleep 3
  fi
  got="$(sha "$PDFS/$name")"
  if [ "$got" = "$want" ]; then echo "ok   $name"; else echo "BAD  $name (hash mismatch)"; fail=1; fi
done < <(awk '/^## Manifest/{f=1} f && /\.pdf  (https|private)/{print $1, $2, $3}' LIBRARY.md)
exit $fail
