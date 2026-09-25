#!/usr/bin/env python3
"""Mirror the Collective's event log to W&B Weave (edict E-0106).

  agents/.venv/bin/python agents/bin/weave_sync.py once            catch up (the first run backfills everything)
  agents/.venv/bin/python agents/bin/weave_sync.py follow [--every 30]
  agents/.venv/bin/python agents/bin/weave_sync.py status

Every agent run becomes one trace, `collective.run` (who, which run, how it ended, what it cost), with each
of its events as a child call: its prompt, its transcript, every file it changed, every board post. Events
outside a run (edicts, amendments, moves, huddles, projects, shells, incidents) become their own calls. The
calls keep the events' real times.

What leaves the machine, to the Steward's private Weave project (WEAVE_PROJECT, default "the-collective"):
event metadata, and the text of agent prompts and transcripts. Everything is redacted first with the event
log's own rules plus the web terminal's. Never sent: file contents, edict text, secrets, or agents/.env.
The API key is read from agents/.env (WANDB_API_KEY) and never printed. The cursor lives in
private/weave/state.json, so each event is sent once.
"""
import argparse, datetime, gzip, json, os, pathlib, re, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/bin")); sys.path.insert(0, str(ROOT / "dashboard"))
from eventlog import EVENTS, BLOBS, SECRET_RE                     # the log and its redaction (Article 12.3)
EXTRA_RE = re.compile(r"(?<![A-Za-z0-9])(?:xai-[A-Za-z0-9]{20,}|wandb_v1_[A-Za-z0-9_]{20,})|(?i:(?:api[_-]?key|secret|token|password|passwd)\s*[:=]\s*\S{6,})")
STATE = ROOT / "private/weave/state.json"
TEXT_CAP = 200_000                                               # characters of a prompt or transcript sent
OPEN_RUN_SECS = 6 * 3600                                         # a run with no end after this is sent as open
BLOB_TYPES = {"agent.prompt", "agent.transcript"}

def redact(v):
    if isinstance(v, str): return EXTRA_RE.sub("[redacted: secret]", SECRET_RE.sub("[redacted: secret]", v))
    if isinstance(v, dict): return {k: redact(x) for k, x in v.items()}
    if isinstance(v, list): return [redact(x) for x in v]
    return v

def load_env():
    for line in (ROOT / "agents/.env").read_text().splitlines():
        m = re.match(r"^(WANDB_API_KEY|WEAVE_PROJECT)=(.*)$", line.strip())
        if m and not os.environ.get(m.group(1)): os.environ[m.group(1)] = m.group(2).strip().strip("'\"")
    if not os.environ.get("WANDB_API_KEY"): sys.exit("REFUSED: WANDB_API_KEY isn't set in agents/.env")

def ts(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))

def blob_text(h, cap=TEXT_CAP):
    """A prompt or transcript; past the cap, its first and last halves (the end holds the result and its cost)."""
    p = BLOBS / h[:2] / h[2:]
    if not p.exists(): return None
    raw = p.read_bytes()
    try: raw = gzip.decompress(raw)
    except OSError: pass
    t = raw.decode("utf-8", "replace")
    if cap is None or len(t) <= cap: return t
    return t[:cap // 2] + f"\n… [{len(t) - cap} characters not sent] …\n" + t[-cap // 2:]

def cost_of(text):
    """The run's cost and tokens, if the model's output reported them (Grok and Claude JSON results)."""
    out = {}
    for line in reversed((text or "").splitlines()[-400:]):
        if '"total_cost_usd"' not in line: continue
        try: j = json.loads(line)
        except ValueError: continue
        out["cost_usd"] = j.get("total_cost_usd"); u = j.get("usage") or {}
        out.update({k: u[k] for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "reasoning_tokens") if k in u})
        break
    return out

def event_inputs(e):
    d = dict(e.get("data") or {})
    if e["type"] in BLOB_TYPES and d.get("blob"):
        d["text"] = blob_text(d["blob"])
    return redact({"seq": e["seq"], "actor": e["actor"], "type": e["type"], "run": e.get("run"), **d})

def load_state():
    try: return json.loads(STATE.read_text())
    except (OSError, ValueError): return {"seq": -1, "sent": 0}

def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=1)); tmp.replace(STATE)

def events_after(seq):
    with open(EVENTS) as f:
        for line in f:
            e = json.loads(line)
            if e["seq"] > seq: yield e

def send_run(client, rid, r):
    start = next((x for x in r if x["type"] == "run.start"), r[0]); end = next((x for x in r if x["type"] == "run.end"), None)
    transcript = next((x for x in r if x["type"] == "agent.transcript"), None)
    cost = cost_of(blob_text(transcript["data"]["blob"], cap=None)) if transcript and (transcript.get("data") or {}).get("blob") else {}
    parent = client.create_call("collective.run", redact({"actor": start["actor"], "run": rid, **(start.get("data") or {})}),
                                attributes={"actor": start["actor"], "kind": "run"}, display_name=f"{start['actor']} · run",
                                use_stack=False, started_at=ts(start["ts"]))
    n = 0
    for x in r:
        if x is start or x is end: continue
        c = client.create_call(f"collective.{x['type']}", event_inputs(x), parent=parent, attributes={"actor": x["actor"]},
                               display_name=f"{x['actor']} · {x['type']}", use_stack=False, started_at=ts(x["ts"]))
        client.finish_call(c, output={"seq": x["seq"]}, ended_at=ts(x["ts"])); n += 1
    client.finish_call(parent, output=redact({"ended": bool(end), "events": len(r), **((end or {}).get("data") or {}), **cost}),
                       ended_at=ts((end or r[-1])["ts"]))
    return n + 1

def sync(client):
    """Send every new event once. A run is sent whole when it ends (or after OPEN_RUN_SECS, marked open);
    until then only its own events wait: they're kept in state["open"], and everything else goes now."""
    st = load_state(); st.setdefault("open", {})
    held = {int(q) for seqs in st["open"].values() for q in seqs}
    evs = [e for e in (json.loads(l) for l in open(EVENTS)) if e["seq"] > st["seq"] or e["seq"] in held]
    if not evs: return 0
    runs = {}
    for e in evs:
        if e.get("run"): runs.setdefault(e["run"], []).append(e)
    now = datetime.datetime.now(datetime.timezone.utc); sent = 0
    for e in evs:
        rid = e.get("run")
        if rid:
            r = runs.pop(rid, None)
            if r is None: continue                                  # sent (or held) with its run already
            ended = any(x["type"] == "run.end" for x in r)
            if not ended and (now - ts(r[0]["ts"])).total_seconds() < OPEN_RUN_SECS:
                st["open"][rid] = [x["seq"] for x in r]; continue
            sent += send_run(client, rid, r); st["open"].pop(rid, None)
        else:
            if e["seq"] in held: continue
            c = client.create_call(f"collective.{e['type']}", event_inputs(e), attributes={"actor": e["actor"], "kind": "event"},
                                   display_name=f"{e['actor']} · {e['type']}", use_stack=False, started_at=ts(e["ts"]))
            client.finish_call(c, output={"seq": e["seq"]}, ended_at=ts(e["ts"])); sent += 1
    client.flush()
    st["seq"] = max(st["seq"], max(e["seq"] for e in evs)); st["sent"] = st.get("sent", 0) + sent
    st["last_sync"] = now.isoformat(timespec="seconds"); save_state(st)
    return sent

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["once", "follow", "status"]); ap.add_argument("--every", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "status":
        st = load_state(); last = max((json.loads(l)["seq"] for l in open(EVENTS)), default=-1)
        print(f"synced through event {st['seq']} of {last}; {st.get('sent', 0)} calls sent; {len(st.get('open', {}))} runs still open; "
              f"last sync {st.get('last_sync', 'never')}"); return
    load_env()
    os.environ.setdefault("WEAVE_PRINT_CALL_LINK", "false")               # quiet: no link per call
    os.environ.setdefault("WEAVE_IMPLICITLY_PATCH_INTEGRATIONS", "false")  # this process calls no models
    import weave
    client = weave.init(os.environ.get("WEAVE_PROJECT", "the-collective"))
    st = load_state(); st["url"] = f"https://wandb.ai/{client.entity}/{client.project}/weave"; save_state(st)   # for the dashboard's link
    while True:
        n = sync(client)
        if a.cmd == "once": print(f"sent {n} calls"); return
        time.sleep(max(10, a.every))

if __name__ == "__main__":
    main()
