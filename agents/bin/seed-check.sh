#!/usr/bin/env bash
# Prove the seed works (Charter P12, Article 20.1): rebuild the Collective from
# CHARTER.md alone in a scratch folder and compare it with the live tree.
# Exit 0 = the seed recreates every generated file exactly.
set -euo pipefail
cd "$(dirname "$0")/../.."
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/agents/bin"; cp CHARTER.md "$tmp/"
python3 - "$tmp" <<'PY'
import re, sys, pathlib
s = pathlib.Path("CHARTER.md").read_text()
m = re.search(r"## V\.\d+ `agents/bin/charter.py`\n\n````python\n(.*?)\n````\n", s, re.S)
pathlib.Path(sys.argv[1], "agents/bin/charter.py").write_text(m.group(1) + "\n")
PY
(cd "$tmp" && python3 agents/bin/charter.py materialize --include-live >/dev/null)
n=0; bad=0
while IFS= read -r f; do
  n=$((n+1))
  case "$f" in org/LEARNINGS.md|org/board/*|org/cases/*|research/papers.md|sprints/*|projects/*|amendments/*|agents/roster.json) continue;; esac  # live records evolve
  cmp -s "$tmp/$f" "$f" || { echo "DRIFT: $f"; bad=$((bad+1)); }
done < <(cd "$tmp" && find . -type f ! -name CHARTER.md | sed 's|^\./||')
if [ "$bad" -eq 0 ]; then echo "seed ok: $n files rebuilt from the Charter"; else echo "SEED FAILED: $bad files drift from the Charter"; exit 1; fi
