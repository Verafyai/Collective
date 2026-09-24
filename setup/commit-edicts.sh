#!/usr/bin/env bash
# Commit every edict not yet in git, one commit per edict, oldest first, in the
# PRIVATE repo (private/ = CollectivePrivate). Commit dates use each edict's
# issue date (reconstructed edicts are marked approximate in their files).
# Safe to re-run: already-tracked edicts are skipped.
set -euo pipefail
cd "$(dirname "$0")/../private"
[ -d .git ] || git init -q
for f in $(ls edicts/E-*.md | sort); do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then continue; fi
  id=$(basename "$f" | cut -c1-6)
  title=$(sed -n 's/^title: //p' "$f" | head -1)
  day=$(sed -n 's/^issued: \([0-9-]*\).*/\1/p' "$f" | head -1)
  when="${day:-$(date +%F)}T12:00:00"
  git add "$f"
  GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" git commit -q -m "Edict $id: $title" -- "$f"
  echo "committed $id ($when)"
done
python3 ../agents/bin/edict.py index >/dev/null
git add edicts/INDEX.md && git commit -q -m "Edicts index" -- edicts/INDEX.md 2>/dev/null || true
