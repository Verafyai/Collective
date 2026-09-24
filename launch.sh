#!/usr/bin/env bash
# launch.sh — start the Collective. Run it in the Collective folder.
#
#   ./launch.sh              setup phase until private/.setup-complete exists, then operating phase
#   ./launch.sh --tmux       same, using tmux instead of herdr (fallback)
#   ./launch.sh --dry-run    show what would happen, change nothing
#   ./launch.sh --phase setup|operate    force a phase
#
# SETUP phase: opens the "Collective Setup" workspace:
#   the first Claude Code agent (with its setup instructions) + a live event feed,
#   and a dashboard tab that starts the dashboard as soon as the agent has built it.
# OPERATE phase: opens the "Collective" workspace: every office running on its
#   schedule, the live feed, the dashboard, and the approvals queue.
#
# herdr-plus needs a running herdr. If you're not inside herdr yet:
#   cd <this folder> && herdr        then run ./launch.sh in its first pane.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
MODE=herdr; DRY=0; PHASE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --tmux) MODE=tmux;; --dry-run) DRY=1;; --phase) PHASE="${2:?setup or operate}"; shift;;
    -h|--help) sed -n '2,17p' "$0"; exit 0;;
    *) echo "unknown option: $1"; exit 1;;
  esac; shift
done
run() { if [ $DRY = 1 ]; then echo "  DRY: $*"; else eval "$@"; fi; }
say() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m!\033[0m %s\n' "$*"; }
die() { printf '  \033[31m✗\033[0m %s\n' "$*"; exit 1; }

[ -f CHARTER.md ] || die "run this in the Collective folder (no CHARTER.md here)"
say "The Collective · Charter v$(sed -n 's/^Charter version: //p' CHARTER.md | head -1)"

# ---------- 1. preflight ----------
say "1) Checking prerequisites"
need=(claude git python3)
[ $MODE = herdr ] && need+=(herdr) || need+=(tmux)
missing=0
for c in "${need[@]}"; do
  if command -v "$c" >/dev/null 2>&1; then ok "$c"; else warn "$c not found"; missing=1; fi
done
[ $missing = 1 ] && die "install what's missing (herdr: see herdr.dev; Claude Code: see docs.claude.com), then re-run"
[ -f org/STOP ] && die "org/STOP is present: the Collective is stopped. Remove it (Steward) to launch."

# ---------- 2. local config ----------
say "2) Local configuration"
[ -f agents/config.env ] || { run "cp agents/config.example.env agents/config.env"; ok "created agents/config.env"; }
if [ ! -f agents/.env ]; then
  if [ -f private/secrets/env.age ] && command -v age >/dev/null; then
    run "agents/bin/secrets.sh unseal" && ok "unsealed agents/.env from the private repo"
  else
    run "cp agents/.env.example agents/.env && chmod 600 agents/.env"
    warn "created an empty agents/.env; the setup agent will walk you through filling it"
  fi
else ok "agents/.env present"; fi
[ -s private/ledger/events.ndjson ] || { run "python3 agents/bin/eventlog.py init --actor steward >/dev/null"; ok "event log started (genesis)"; }
chmod +x setup/*.sh agents/bin/* 2>/dev/null || true

# ---------- 3. phase ----------
if [ -z "$PHASE" ]; then [ -f private/.setup-complete ] && PHASE=operate || PHASE=setup; fi
say "3) Phase: $PHASE"
if [ $PHASE = setup ]; then
  echo "   The first Claude Code agent will set up the Collective and stop for your review at each step."
  echo "   Answer it in its pane. Events appear live beside it; the dashboard tab lights up once it's built."
else
  echo "   Every office starts on its schedule. Watch the live tab and the dashboard; approve in the approvals tab."
fi
python3 agents/bin/eventlog.py record --actor steward --type org.launch --data "{\"summary\": \"launch.sh ($PHASE, $MODE)\"}" 2>/dev/null || true

# ---------- 4a. herdr ----------
if [ $MODE = herdr ]; then
  say "4) herdr"
  # Installed? (herdr knows the plugin's config folder only once it's installed.)
  cfg="$(herdr plugin config-dir cloudmanic.herdr-plus 2>/dev/null || true)"
  if [ -z "$cfg" ]; then
    run "herdr plugin install cloudmanic/herdr-plus" && ok "installed herdr-plus"
    cfg="$(herdr plugin config-dir cloudmanic.herdr-plus 2>/dev/null || true)"
  else ok "herdr-plus plugin installed"; fi
  [ -z "$cfg" ] && [ $DRY = 0 ] && die "couldn't find herdr-plus's config folder (herdr ≥ 0.7 is required)"
  cfg="${cfg:-<herdr-plus config dir>}"
  # The plugin install doesn't put the herdr-plus program on PATH, so find its binary.
  HP="$(command -v herdr-plus 2>/dev/null || true)"
  if [ -z "$HP" ]; then
    for d in "$HOME/.config/herdr" "$HOME/Library/Application Support/herdr" "$HOME/.local/share/herdr"; do
      [ -d "$d" ] || continue
      HP="$(find "$d" -type f -name herdr-plus -perm -u+x 2>/dev/null | head -1)"
      [ -n "$HP" ] && break
    done
  fi
  if [ -z "$HP" ] && [ $DRY = 0 ]; then
    warn "the herdr-plus program wasn't found (the plugin is installed, but its binary isn't on PATH)."
    echo "   Install it with Homebrew, then re-run ./launch.sh:"
    echo "       brew tap cloudmanic/herdr-plus https://github.com/cloudmanic/herdr-plus"
    echo "       brew install cloudmanic/herdr-plus/herdr-plus"
    exit 1
  fi
  ok "herdr-plus program: ${HP:-<found at run time>}"
  for t in collective-setup collective; do
    run "mkdir -p '$cfg/projects' && sed 's|__ORG_ROOT__|$ROOT|' herdr/projects/$t.toml > '$cfg/projects/$t.toml'"
  done
  ok "workspaces installed: \"Collective Setup\" and \"Collective\""
  name="Collective"; [ $PHASE = setup ] && name="Collective Setup"
  if [ $DRY = 1 ]; then echo "  DRY: herdr-plus open \"$name\""; exit 0; fi
  if "$HP" open "$name"; then
    ok "opened \"$name\" — switch to its tab to watch"
    if [ $PHASE = operate ] && command -v open >/dev/null; then (sleep 4; open "http://127.0.0.1:4848" 2>/dev/null) & fi
    exit 0
  fi
  echo
  warn "herdr isn't running here yet, and herdr-plus needs it."
  echo "   Next, type these two commands:"
  echo "       herdr"
  echo "       ./launch.sh          (inside herdr's first pane, which opens in this folder)"
  echo "   Everything else is already set up. Or, to skip herdr:  ./launch.sh --tmux"
  exit 1
fi

# ---------- 4b. tmux fallback ----------
say "4) tmux (fallback)"
S=collective
if tmux has-session -t $S 2>/dev/null; then ok "session '$S' already running"; [ $DRY = 1 ] || exec tmux attach -t $S; exit 0; fi
if [ $PHASE = setup ]; then
  run "tmux new-session -d -s $S -n setup -c '$ROOT' 'setup/start-claude.sh'"
  run "tmux split-window -h -p 35 -t $S:setup -c '$ROOT' 'python3 agents/bin/playback.py --follow'"
  run "tmux new-window -t $S -n dashboard -c '$ROOT' 'setup/wait-for-dashboard.sh'"
  run "tmux new-window -t $S -n shell -c '$ROOT'"
  run "tmux select-window -t $S:setup"
else
  run "tmux new-session -d -s $S -n officers -c '$ROOT' 'agents/bin/run-role.sh pm --loop'"
  run "tmux split-window -h -t $S:officers -c '$ROOT' 'agents/bin/run-role.sh scribe --loop'"
  run "tmux split-window -v -t $S:officers.0 -c '$ROOT' 'agents/bin/run-role.sh lawyer --loop'"
  run "tmux split-window -v -t $S:officers.1 -c '$ROOT' 'agents/bin/run-role.sh auditor --loop'"
  run "tmux new-window -t $S -n makers -c '$ROOT' 'agents/bin/run-role.sh researcher --loop'"
  for r in ideas prototyper media social; do run "tmux split-window -t $S:makers -c '$ROOT' 'agents/bin/run-role.sh $r --loop'"; done
  run "tmux select-layout -t $S:makers tiled"
  run "tmux new-window -t $S -n live -c '$ROOT' 'python3 agents/bin/playback.py --follow'"
  run "tmux new-window -t $S -n dashboard -c '$ROOT' 'setup/wait-for-dashboard.sh'"
  run "tmux new-window -t $S -n approvals -c '$ROOT' \"watch -n 30 'ls -1t private/outbox/pending | head -20'\""
  run "tmux select-window -t $S:live"
  if command -v open >/dev/null && [ $DRY = 0 ]; then (sleep 4; open "http://127.0.0.1:4848" 2>/dev/null) & fi
fi
[ $DRY = 1 ] && exit 0
ok "started tmux session '$S' (detach with Ctrl-b d; stop everything with: touch org/STOP)"
exec tmux attach -t $S
