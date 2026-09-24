#!/usr/bin/env bash
# Bootstrap the Verafy org in herdr. Idempotent: safe to re-run.
# Usage: setup/bootstrap.sh [--with-optional] [--dry-run]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
OPTIONAL=0; DRY=0
for a in "$@"; do case "$a" in --with-optional) OPTIONAL=1;; --dry-run) DRY=1;; esac; done
run() { if [ $DRY = 1 ]; then echo "DRY: $*"; else eval "$@"; fi; }
ok() { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; MISSING=1; }

echo "1) Prerequisites"; MISSING=0
for c in herdr claude git python3 node ffmpeg jq watch; do
  if command -v "$c" >/dev/null 2>&1; then ok "$c"; else fail "$c not found"; fi
done
if command -v herdr >/dev/null; then
  v="$(herdr --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"
  [ -n "$v" ] && ok "herdr $v (herdr-plus needs >= 0.7.0)"
fi
command -v grok >/dev/null 2>&1 && ok "grok" || warn "grok CLI not found: set SOCIAL_AGENT_CMD in agents/config.env"
[ $MISSING = 1 ] && { echo "Install the missing tools (see herdr.dev for herdr), then re-run."; exit 1; }

echo "2) Config and secrets"
[ -f agents/config.env ] || { run "cp agents/config.example.env agents/config.env"; ok "created agents/config.env"; }
if [ ! -f agents/.env ]; then run "cp agents/.env.example agents/.env && chmod 600 agents/.env"; warn "created agents/.env: fill in keys (never commit it)"; else ok "agents/.env exists"; fi

echo "3) Repositories (public: Verafyai/Collective · private: Verafyai/CollectivePrivate)"
run "agents/bin/repos.sh init" && ok "both repos ready (private/ is git-ignored by public)"
run "setup/commit-edicts.sh" && ok "edicts committed to the private repo, one commit each"
if [ -f private/secrets/env.age ] && [ ! -f agents/.env ]; then run "agents/bin/secrets.sh unseal" && ok "secrets unsealed from the private repo"; fi

echo "4) herdr plugins"
installed="$(herdr plugin list 2>/dev/null || true)"
while read -r line; do
  repo="$(echo "$line" | awk '{print $1}')"; [ -z "$repo" ] || [[ "$repo" == \#* ]] && continue
  tier="$(echo "$line" | awk '{print $NF}')"
  [ "$tier" = optional ] && [ $OPTIONAL = 0 ] && { warn "skip optional $repo"; continue; }
  if echo "$installed" | grep -qi "$(basename "$repo")"; then ok "$repo (already installed)"
  else run "herdr plugin install $repo" && ok "installed $repo" || warn "install failed: $repo (check its README)"; fi
done < setup/plugins.txt

echo "5) Workspace template"
if cfg="$(herdr plugin config-dir cloudmanic.herdr-plus 2>/dev/null)"; then
  run "mkdir -p '$cfg/projects' && sed 's|__ORG_ROOT__|$ROOT|' herdr/projects/collective.toml > '$cfg/projects/collective.toml'"
  ok "template installed to $cfg/projects/collective.toml"
else warn "herdr-plus config dir not found; install herdr-plus first"; fi

echo "6) Event log (replayability)"
if [ -s private/ledger/events.ndjson ]; then ok "event log exists ($(wc -l < private/ledger/events.ndjson) events)"
else run "python3 agents/bin/eventlog.py init --actor steward" && ok "event log initialized (genesis snapshot)"; fi

echo "7) Runtime folders"
run "mkdir -p research/briefs ideas prototypes media/exports private/outbox/{pending,approved,posted,rejected} org/board"
ok "folders ready"

echo
run "agents/bin/repos.sh commit 'The Collective at Charter v$(sed -n "s/^Charter version: //p" CHARTER.md | head -1)'" && ok "initial commits made (not pushed)"
echo
echo "Next:"
echo "  • Fill agents/.env, then review agents/config.env (tools, caps, SOCIAL_AGENT_CMD)."
echo "  • Start everything:   herdr-plus open \"the Collective\"   (or pick it in the Projects browser)"
echo "  • Emergency stop:     touch org/STOP"
echo "  • Approve a draft:    agents/bin/approve.sh private/outbox/pending/<file>"
