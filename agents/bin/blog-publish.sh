#!/usr/bin/env bash
# Publish an APPROVED weekly blog post into the public repo's blog/ (Charter Article 19).
# Usage: blog-publish.sh private/outbox/approved/<date>-blog-<slug>.md
# Refuses anything not approved by the Steward. The public repo is still pushed by the Steward.
set -euo pipefail
cd "$(dirname "$0")/../.."
f="${1:?approved blog draft}"; b="$(basename "$f")"
[[ "$b" == *-blog-* ]] || { echo "REFUSED: not a blog draft (name must contain -blog-)"; exit 1; }
[ -f "private/outbox/approved/$b" ] || { echo "REFUSED: $b is not in private/outbox/approved"; exit 1; }
grep -q "Approved by rex" "private/outbox/approved/$b" || { echo "REFUSED: no Steward approval stamp"; exit 1; }
[ -f org/STOP ] && { echo "REFUSED: org/STOP present"; exit 1; }
mkdir -p blog
out="blog/$(echo "$b" | cut -c1-10)-${b#*-blog-}"
sed '/^Approved by rex/d' "private/outbox/approved/$b" > "$out"
printf '\n---\n*Written by the Collective (AI agents), from its own versioned records. Approved for publication by the Steward.*\n' >> "$out"
mv "private/outbox/approved/$b" "private/outbox/posted/$b"
agents/bin/repos.sh commit "Blog: $(head -1 "$out" | sed 's/^# //')"
python3 agents/bin/eventlog.py record --actor scribe --type blog.published --data "{\"summary\": \"$(head -1 "$out" | sed 's/^# //; s/\"//g')\", \"file\": \"$out\"}"
echo "published $out (Steward pushes the public repo: agents/bin/repos.sh push --public)"
