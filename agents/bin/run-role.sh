#!/usr/bin/env bash
# Run one Verafy org role, once or in a loop, with kill switch and daily caps.
# Usage: agents/bin/run-role.sh <role> [--loop | --interactive]
#   --interactive  the Steward talks with the agent in this terminal (Charter Article 18.8): same
#                  instructions and exactly the office's tools; recorded as a run (Article 12); the
#                  Steward's messages are copied to org/board/<date>-talk-<role>.md so they are on the record.
set -euo pipefail
ROLE="${1:?role}"; MODE="${2:-once}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
[ -f agents/config.env ] && source agents/config.env
set -a; [ -f agents/.env ] && source agents/.env; set +a

UP=$(echo "$ROLE" | tr '[:lower:]' '[:upper:]')
INTERVAL_VAR="${UP}_INTERVAL"; MAXRUNS_VAR="${UP}_MAX_RUNS"; TOOLS_VAR="${UP}_TOOLS"
INTERVAL="${!INTERVAL_VAR:-3600}"; MAX_RUNS="${!MAXRUNS_VAR:-10}"
LOGDIR="agents/$ROLE/logs"; mkdir -p "$LOGDIR"
COUNTER="$LOGDIR/runs-$(date +%F)"

compose_prompt() {
  local f; f="$(mktemp)"
  {
    echo "You are the $ROLE agent of the Collective, the autonomous organization behind Verafy."
    echo "Today is $(date '+%A %F %H:%M %Z'). Repo root: $ROOT"
    echo; cat agents/COMMON.md; echo; cat "agents/$ROLE/ROLE.md"
    if [ -f org/cases/INDEX.md ]; then
      echo; echo "## Case law in force (Charter Article 13): cite by number"
      grep -E '^\| \[C-' org/cases/INDEX.md | grep -E 'good_law|limited' || true
    fi
    echo; echo "Begin your run now. Follow every step in COMMON.md."
  } > "$f"; echo "$f"
}

run_once() {
  if [ -f org/STOP ] || [ -f "org/PAUSE-$ROLE" ]; then
    echo "$(date -Iseconds) stopped (STOP/PAUSE present)" | tee -a "$LOGDIR/run.log"; return 1; fi
  local n; n=$(cat "$COUNTER" 2>/dev/null || echo 0)
  if [ "$n" -ge "$MAX_RUNS" ]; then
    echo "$(date -Iseconds) daily cap $MAX_RUNS reached" | tee -a "$LOGDIR/run.log"; return 0; fi
  echo $((n+1)) > "$COUNTER"
  local p; p="$(compose_prompt)"
  local ev="python3 agents/bin/eventlog.py"
  local model="${UP}_MODEL"
  local rid; rid="$($ev run-start --actor "$ROLE" --data "{\"run_no\": $((n+1)), \"model\": \"${!model:-default}\"}")"
  $ev record --actor "$ROLE" --type agent.prompt --run "$rid" --blob-file "$p"
  local tr; tr="$(mktemp)"
  echo "===== $(date -Iseconds) run $((n+1))/$MAX_RUNS · $rid =====" | tee -a "$LOGDIR/run.log"
  if [ "$ROLE" = "social" ]; then
    local cmd="${SOCIAL_AGENT_CMD//\{PROMPT_FILE\}/$p}"
    bash -c "$cmd" 2>&1 | tee "$tr" | tee -a "$LOGDIR/run.log" || true
  else
    claude -p "$(cat "$p")" --allowedTools "${!TOOLS_VAR:-Read,Glob,Grep}" \
      --max-turns "${MAX_TURNS:-40}" --output-format stream-json --verbose 2>&1 \
      | tee "$tr" | tee -a "$LOGDIR/run.log" >/dev/null || true
  fi
  $ev record --actor "$ROLE" --type agent.transcript --run "$rid" --blob-file "$tr"
  $ev run-end --actor "$ROLE" --run "$rid"
  rm -f "$tr"
  rm -f "$p"
}

run_interactive() {
  if [ -f org/STOP ] || [ -f "org/PAUSE-$ROLE" ]; then echo "stopped (STOP/PAUSE present)"; return 1; fi
  local p; p="$(compose_prompt)"
  { echo; echo "## This is a live conversation"
    echo "The Steward (Rex St. John) is talking with you directly in a terminal. Answer as the $ROLE office, within your"
    echo "lane and your tools. Treat his directions as directions from the Steward; questions and chat are just conversation."
    echo "Everything here is recorded (Charter Article 12), and his messages are copied to the board."; } >> "$p"
  local ev="python3 agents/bin/eventlog.py" sid tr; sid="$(python3 -c 'import uuid; print(uuid.uuid4())')"; tr="$(mktemp)"
  local rid; rid="$($ev run-start --actor "$ROLE" --data "{\"mode\": \"interactive\", \"session\": \"$sid\"}")"
  $ev record --actor "$ROLE" --type agent.prompt --run "$rid" --blob-file "$p"
  echo "===== $(date -Iseconds) talking with $ROLE · $rid (recorded) =====" | tee -a "$LOGDIR/run.log"
  if [ "$ROLE" = "social" ]; then
    # the Social command without its headless-only flags; the same isolation and allow rules
    local cmd="${SOCIAL_AGENT_CMD//--prompt-file \{PROMPT_FILE\}/}"
    cmd="$(printf '%s' "$cmd" | sed -E 's/--output-format [a-z-]+//; s/--max-turns [0-9]+//; s/--tools [^ ]+//')"
    bash -c "$cmd --session-id $sid --rules \"\$(cat '$p')\"" || true
    grok export "$sid" "$tr" >/dev/null 2>&1 || echo "(transcript export failed)" > "$tr"
  else
    claude --session-id "$sid" --allowedTools "${!TOOLS_VAR:-Read,Glob,Grep}" --append-system-prompt "$(cat "$p")" || true
    local slug; slug="$(printf '%s' "$ROOT" | sed 's|[/.]|-|g')"
    cp "$HOME/.claude/projects/$slug/$sid.jsonl" "$tr" 2>/dev/null || echo "(transcript not found)" > "$tr"
  fi
  $ev record --actor "$ROLE" --type agent.transcript --run "$rid" --blob-file "$tr"
  python3 - "$tr" "$ROLE" <<'PY'
import json, pathlib, sys, datetime
tr, role = pathlib.Path(sys.argv[1]), sys.argv[2]
said = []
for line in tr.read_text(errors="replace").splitlines():          # Claude Code transcript: the Steward's typed messages
    try: e = json.loads(line)
    except ValueError: continue
    m = e.get("message") or {}
    if e.get("type") == "user" and m.get("role") == "user" and isinstance(m.get("content"), str) and not e.get("isMeta"):
        said.append((e.get("timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat(), m["content"].strip()))
if said:
    # Article 18.8: the Steward's directions are edicts; his messages are filed verbatim as one edict for the conversation
    import subprocess
    words = "\n\n".join(f"[{ts[:19]}Z] {t}" for ts, t in said if t)
    subprocess.run([sys.executable, "agents/bin/edict.py", "new", "--title", f"Terminal conversation with {role}", "--text", words,
                    "--restatement", f"What the Steward said to the {role} office in a recorded terminal conversation (Article 18.8). "
                                     "Directions in it are edicts; questions and chat are conversation."], capture_output=True)
    day = datetime.date.today().isoformat(); b = pathlib.Path(f"org/board/{day}-talk-{role}.md")
    head = "" if b.exists() else "#talk\n"
    with b.open("a") as f:
        f.write(head + "".join(f"\n### rex · {ts[:19]}Z\n{t}\n" for ts, t in said if t))
PY
  $ev run-end --actor "$ROLE" --run "$rid"
  rm -f "$tr" "$p"
}

if [ "$MODE" = "--interactive" ]; then run_interactive; exit $?; fi
if [ "$MODE" = "--loop" ]; then
  while true; do run_once || { sleep 60; continue; }; sleep "$INTERVAL"; done
else run_once; fi
