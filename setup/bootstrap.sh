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
  spec="$(echo "$line" | awk '{print $1}')"; [ -z "$spec" ] || [[ "$spec" == \#* ]] && continue
  repo="${spec%@*}"; ref=""; [ "$spec" != "$repo" ] && ref="${spec#*@}"
  tier="$(echo "$line" | awk '{print $NF}')"
  [ "$tier" = held ] && { warn "held, not installed: $repo (see docs/plugin-notes.md)"; continue; }
  [ "$tier" = optional ] && [ $OPTIONAL = 0 ] && { warn "skip optional $repo"; continue; }
  [ -z "$ref" ] && { warn "not installed: $repo has no reviewed commit pinned in setup/plugins.txt"; continue; }
  if echo "$installed" | grep -qi "$(basename "$repo")"; then ok "$repo (already installed)"
  # pinned to the reviewed commit; herdr-projects builds from that source, not a release download
  else run "HERDR_PROJECTS_BUILD=source herdr plugin install $repo --ref $ref --yes" && ok "installed $repo @ ${ref:0:7}" || warn "install failed: $repo (check its README)"; fi
done < setup/plugins.txt
# tsk is called by name (Bash(tsk:*)); link the plugin's binary onto PATH
t="$(ls -d "$HOME"/.config/herdr/plugins/github/herdr-tsk-*/target/release/tsk 2>/dev/null | head -1 || true)"
if [ -n "$t" ]; then run "mkdir -p '$HOME/.local/bin' && ln -sf '$t' '$HOME/.local/bin/tsk'" && ok "tsk linked into ~/.local/bin"
else warn "tsk binary not found; install smarzban/tsk first"; fi

echo "5) Workspace template"
if cfg="$(herdr plugin config-dir cloudmanic.herdr-plus 2>/dev/null)"; then
  run "mkdir -p '$cfg/projects' && sed 's|__ORG_ROOT__|$ROOT|' herdr/projects/collective.toml > '$cfg/projects/collective.toml'"
  ok "template installed to $cfg/projects/collective.toml"
else warn "herdr-plus config dir not found; install herdr-plus first"; fi

echo "6) Event log (replayability)"
if [ -s private/ledger/events.ndjson ]; then ok "event log exists ($(wc -l < private/ledger/events.ndjson) events)"
else run "python3 agents/bin/eventlog.py init --actor steward" && ok "event log initialized (genesis snapshot)"; fi

echo "6b) Observability: the Weave bridge and evals (Article 12.10, P-005)"
if [ -x agents/.venv/bin/python ] && agents/.venv/bin/python -c "import weave, opentelemetry.exporter.otlp.proto.http" 2>/dev/null; then ok "weave and the OTel exporter installed in agents/.venv"
else run "python3 -m venv agents/.venv && agents/.venv/bin/pip install -q 'weave==0.53.10' 'opentelemetry-sdk==1.44.0' 'opentelemetry-exporter-otlp-proto-http==1.44.0'" && ok "installed in agents/.venv (set WANDB_API_KEY in agents/.env to turn tracing on)"; fi
rules=agents/observability/gitleaks-rules.toml; want=e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf
if [ -f "$rules" ] && [ "$(shasum -a 256 "$rules" | cut -d' ' -f1)" = "$want" ]; then ok "gitleaks 8.30.1 rules present (redact.py)"
else run "curl -fsSL https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml -o $rules" \
  && [ "$(shasum -a 256 "$rules" | cut -d' ' -f1)" = "$want" ] && ok "gitleaks 8.30.1 rules fetched and checked (SHA-256)" || warn "gitleaks rules didn't match their SHA-256; redact.py runs without them"; fi

echo "7) Runtime folders"
run "mkdir -p research/briefs ideas prototypes media/exports private/outbox/{pending,approved,posted,rejected} org/board org/tasks"
ok "folders ready"

echo
run "agents/bin/repos.sh commit 'The Collective at Charter v$(sed -n "s/^Charter version: //p" CHARTER.md | head -1)'" && ok "initial commits made (not pushed)"
echo
echo "Next:"
echo "  • Fill agents/.env, then review agents/config.env (tools, caps, SOCIAL_AGENT_CMD)."
echo "  • Start everything:   herdr-plus open \"the Collective\"   (or pick it in the Projects browser)"
echo "  • Emergency stop:     touch org/STOP"
echo "  • Approve a draft:    agents/bin/approve.sh private/outbox/pending/<file>"
