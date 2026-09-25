#!/usr/bin/env python3
"""The OpenTelemetry bridge (P-005; Charter Article 12.10): the event log as GenAI spans in Weave's Agents view.

  . agents/bin/env.sh && agents/.venv/bin/python agents/observability/otel_bridge.py backfill
  . agents/bin/env.sh && agents/.venv/bin/python agents/observability/otel_bridge.py follow [--every 30]
  agents/.venv/bin/python agents/observability/otel_bridge.py status         (no network, no key needed)
  agents/.venv/bin/python agents/observability/otel_bridge.py plan [--limit N] (print the spans; export nothing)

Reads the hash-chained event log (Article 12) and exports OTLP/protobuf spans to
https://trace.wandb.ai/agents/otel/v1/traces, under resource attributes wandb.entity and wandb.project.

  one agent run                    root span   invoke_agent <agent>   (gen_ai.agent.name = the roster key)
  each model call in its transcript  child     chat <model>           (model, input/output/cache tokens)
  each tool call in its transcript   child     execute_tool <tool>    (tool name only)
  each recorded action in the run    child     execute_tool <event>   (file change, board post, vote, audit, ...)
  an event outside any run         root span   invoke_agent <actor>, with one execute_tool child

Turns in one conversation share gen_ai.conversation.id (standup-<date>, the edict / amendment / project /
huddle id, talk-<agent>-<session>, or sprint-<id>-council), not a parent span. Every span carries
collective.* attributes so it can be followed back to the Record (event hash, previous hash, office,
votes, room, edict, case, project, sprint, amendment).

Privacy (E-0108): OBS_PRIVATE_MODE=metadata (default) sends only ids, types, times, models, token counts,
tool names, and public paths: never prompt or transcript text, edict text, summaries of private events,
typed shell lines, or paths under private/. "full" adds redacted text; "off" also drops edict, shell,
notification, and private-path events. Every string attribute goes through redact.py either way.

Idempotent: span and trace ids are derived from event hashes, and the last exported hash is kept in
agents/observability/.bridge_state (git-ignored), so a restart never duplicates spans. A run that hasn't
ended waits (only its own events) until it ends or is six hours old. The bridge runs in its own process,
so an unreachable W&B never touches an agent: it logs one warning and retries on the next pass.
"""
import argparse, datetime, gzip, hashlib, json, os, pathlib, re, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "agents/bin"))
from redact import redact

EVENTS = ROOT / "private/ledger/events.ndjson"
BLOBS = ROOT / "private/ledger/blobs"
STATE = HERE / ".bridge_state"
OPEN_RUN_SECS = 6 * 3600
BATCH = 400
MODE = os.environ.get("OBS_PRIVATE_MODE", "metadata")
PRIVATE_TYPES = ("edict.", "shell.", "notify.")              # sources that live only in CollectivePrivate
SAFE_KEYS = {"agent", "amendment", "case", "court", "seat", "edict", "project", "room", "mode", "model", "run_no", "files_changed", "cols", "rows",
             "pid", "bytes", "duration_s", "hidden_lines", "kind", "via", "exhibit", "position", "round", "ruling", "family", "tokens_in", "tokens_out"}
FULL_KEYS = {"from", "to", "cmd", "session", "theme", "redacted", "ended_by"}      # sent only in "full" mode (the Lawyer's opinion on P-005 v001)
ID_RE = {"edict": r"\bE-\d{4}\b", "case": r"\bCT?-\d{4}\b", "project": r"\bP-\d{3}\b", "sprint": r"\bS-\d{4}\b", "amendment": r"\bA-\d{4}\b"}

# ---------- the log ----------
def load_events():
    with open(EVENTS) as f: return [json.loads(l) for l in f if l.strip()]

def blob_text(h):
    p = BLOBS / h[:2] / h[2:]
    if not h or not p.exists(): return ""
    raw = p.read_bytes()
    try: raw = gzip.decompress(raw)
    except OSError: pass
    return raw.decode("utf-8", "replace")

def ns(ts):
    return int(datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1e9)

def roster():
    try: return {a["key"]: a for a in json.loads((ROOT / "agents/roster.json").read_text())["agents"]}
    except (OSError, ValueError, KeyError): return {}

# ---------- what may leave the machine ----------
def private_path(p): return p.startswith("private/") or p.startswith("agents/.env")

def safe_data(e):
    """The event's data as span attributes, per OBS_PRIVATE_MODE, always redacted."""
    d, out = e.get("data") or {}, {}
    for k, v in d.items():
        if (k in SAFE_KEYS or (MODE == "full" and k in FULL_KEYS)) and isinstance(v, (str, int, float, bool)): out[k] = v
        elif k == "path" and isinstance(v, str): out[k] = "private/…" if private_path(v) else v
        elif k == "files" and isinstance(v, list): out["files"] = len(v)
        elif k == "summary" and isinstance(v, str) and MODE == "full": out[k] = v[:300]         # free text: never in metadata mode
    if e["type"] == "shell.input": out.pop("line", None)           # typed lines never leave, in any mode
    blob = str(d.get("summary", "")) + " " + str(d.get("path", ""))
    for key, rx in ID_RE.items():                                  # ids are metadata even when the text isn't
        if key not in out:
            m = re.search(rx, blob) or re.search(rx, str(d.get(key, "")))
            if m: out[key] = m.group(0)
    return redact(out)

NOISE = ("agents/.venv/", "node_modules/")                        # tool environments swept into the log, not activity

def exported(e):
    if any(str((e.get("data") or {}).get("path", "")).startswith(n) or f"/{n}" in str((e.get("data") or {}).get("path", "")) for n in NOISE): return False
    if MODE != "off": return True
    return not e["type"].startswith(PRIVATE_TYPES) and not private_path(str((e.get("data") or {}).get("path", "")))

# ---------- transcripts: model calls and tool calls, as metadata ----------
def parse_transcript(text):
    """[(kind, name, attrs)] in order: ('chat', model, tokens) and ('tool', name, {}). Claude stream-json or Grok."""
    steps, seen, model = [], {}, None
    for line in text.splitlines():
        if not line.startswith("{"): continue
        try: j = json.loads(line)
        except ValueError: continue
        t = j.get("type")
        if t == "assistant" and isinstance(j.get("message"), dict):            # Claude Code stream-json
            m = j["message"]; mid = m.get("id") or f"m{len(steps)}"
            if mid not in seen:
                u = m.get("usage") or {}
                seen[mid] = len(steps)
                steps.append(("chat", m.get("model") or "claude", {"gen_ai.usage.input_tokens": u.get("input_tokens", 0),
                              "gen_ai.usage.output_tokens": u.get("output_tokens", 0),
                              "gen_ai.usage.cache_read.input_tokens": u.get("cache_read_input_tokens", 0)}))
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    steps.append(("tool", b.get("name", "tool"), {"gen_ai.tool.call.id": b.get("id", "")}))
        elif t == "usage" and isinstance(j.get("usage"), dict):                # Grok CLI streaming-json
            u = j["usage"]
            steps.append(("chat", None, {"gen_ai.usage.input_tokens": u.get("input_tokens", 0), "gen_ai.usage.output_tokens": u.get("output_tokens", 0),
                                         "gen_ai.usage.cache_read.input_tokens": u.get("cache_read_input_tokens", 0)}))
        elif t == "tool_call":
            steps.append(("tool", j.get("toolName") or j.get("title") or "tool", {"gen_ai.tool.call.id": j.get("toolCallId", "")}))
        elif t == "end" and isinstance(j.get("modelUsage"), dict) and j["modelUsage"]:
            model = next(iter(j["modelUsage"]))
        elif t == "result":
            model = model or next(iter(j.get("modelUsage") or {}), None)
    cost, totals = None, {}
    for line in reversed(text.splitlines()[-300:]):                             # the final result carries the true totals
        if '"total_cost_usd"' in line:
            try: j = json.loads(line); cost = float(j.get("total_cost_usd"))
            except (ValueError, TypeError): continue
            u = j.get("usage") or {}
            totals = {"gen_ai.usage.input_tokens": u.get("input_tokens", 0), "gen_ai.usage.output_tokens": u.get("output_tokens", 0),
                      "gen_ai.usage.cache_read.input_tokens": u.get("cache_read_input_tokens", 0)}
            break
    steps = [(k, n or model or "grok", a) if k == "chat" else (k, n, a) for k, n, a in steps]
    return steps, cost, model, totals

# ---------- spans ----------
def hid(*parts, n=16):
    return int.from_bytes(hashlib.sha256("|".join(parts).encode()).digest()[:n], "big") or 1

class Span(dict):
    """A span to export: name, trace/span/parent ids, start/end in ns, attributes."""

def conversation_id(e, first):
    d = first.get("data") or {}
    if d.get("court") == "court" and re.fullmatch(r"CT?-\d{4}", str(d.get("case", ""))): return d["case"]    # a Court case is one conversation
    if d.get("sprint") and d.get("meeting"): return f"sprint-{d['sprint']}-{d['meeting']}"
    if d.get("mode") == "interactive": return f"talk-{first['actor']}-{d.get('session', first['run'])}"
    if first.get("run"): return f"standup-{first['ts'][:10]}"
    sd = safe_data(e)
    for key in ("edict", "amendment", "project", "case", "sprint"):
        if sd.get(key): return sd[key]
    if e["type"].startswith("huddle."): return f"huddle-{e['ts'][:10]}"
    return f"{e['actor']}-{e['ts'][:10]}"

def base_attrs(e, R):
    a = R.get(e["actor"], {})
    attrs = {"collective.event_hash": e.get("hash", ""), "collective.prev_hash": e.get("prev", ""), "collective.seq": e["seq"],
             "collective.office": e["actor"], "collective.votes": bool(a.get("votes", False)), "collective.room": a.get("room", ""),
             "collective.event_type": e["type"], "collective.private_mode": MODE}
    for k, v in safe_data(e).items():
        attrs[f"collective.{k}"] = v
    return attrs

def spans_for_run(rid, r, R):
    start = next((x for x in r if x["type"] == "run.start"), r[0]); end = next((x for x in r if x["type"] == "run.end"), None)
    t0 = ns(start["ts"]); t1 = max(ns((end or r[-1])["ts"]), t0 + 1_000_000)
    trace = hid("run", rid); root = hid("span", start.get("hash", rid), n=8)
    conv = conversation_id(start, start); agent = start["actor"]
    transcript = next((x for x in r if x["type"] == "agent.transcript"), None)
    steps, cost, model, totals = parse_transcript(blob_text((transcript.get("data") or {}).get("blob", ""))) if transcript else ([], None, None, {})
    native = bool((start.get("data") or {}).get("weave_native"))       # a native integration already traced it: governance only
    if native: steps = []
    model = model or (start.get("data") or {}).get("model") or ""
    tin = sum(a.get("gen_ai.usage.input_tokens", 0) or 0 for k, _, a in steps if k == "chat")
    tout = sum(a.get("gen_ai.usage.output_tokens", 0) or 0 for k, _, a in steps if k == "chat")
    attrs = {**base_attrs(start, R), "gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": agent, "gen_ai.conversation.id": conv,
             "gen_ai.request.model": model if model != "default" else "", "gen_ai.usage.input_tokens": tin, "gen_ai.usage.output_tokens": tout,
             "collective.run": rid, "collective.ended": bool(end), "collective.events": len(r), "collective.model_calls": sum(1 for s in steps if s[0] == "chat"),
             "collective.tool_calls": sum(1 for s in steps if s[0] == "tool")}
    attrs.update(totals)                                                       # true totals when the model reported them
    if cost is not None: attrs["collective.cost_usd"] = round(cost, 6)
    if end: attrs["collective.files_changed"] = str((end.get("data") or {}).get("files_changed", ""))
    out = [Span(name=f"invoke_agent {agent}", trace=trace, span=root, parent=None, start=t0, end=t1, attrs=attrs)]
    # model and tool calls: in order, spread across the run (the transcript has no per-call times)
    n = max(len(steps), 1); step = (t1 - t0) // (n + 1)
    for i, (kind, name, a) in enumerate(steps):
        s0 = t0 + step * i; s1 = t0 + step * (i + 1)
        sid = hid("step", rid, str(i), n=8)
        if kind == "chat":
            out.append(Span(name=f"chat {name}", trace=trace, span=sid, parent=root, start=s0, end=s1,
                            attrs={"gen_ai.operation.name": "chat", "gen_ai.conversation.id": conv, "gen_ai.agent.name": agent,
                                   "gen_ai.request.model": name, **a, "collective.timing": "interpolated", "collective.run": rid}))
        else:
            out.append(Span(name=f"execute_tool {name}", trace=trace, span=sid, parent=root, start=s0, end=s1,
                            attrs={"gen_ai.operation.name": "execute_tool", "gen_ai.conversation.id": conv, "gen_ai.agent.name": agent,
                                   "gen_ai.tool.name": name, **a, "collective.timing": "interpolated", "collective.run": rid}))
    # the recorded actions of the run, at their real times
    for x in r:
        if x is start or x is end or x["type"] in ("agent.prompt", "agent.transcript") or not exported(x): continue
        t = min(max(ns(x["ts"]), t0), t1)
        out.append(Span(name=f"execute_tool {x['type']}", trace=trace, span=hid("span", x.get("hash", str(x["seq"])), n=8), parent=root,
                        start=t, end=t + 1_000_000,
                        attrs={**base_attrs(x, R), "gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": x["type"],
                               "gen_ai.conversation.id": conv, "gen_ai.agent.name": agent, "collective.run": rid}))
    return out

SUBJECT_TYPES = ("agent.", "project.assigned")                   # events about an agent are filed under that agent (E-0113)

def spans_for_event(e, R):
    if not exported(e): return []
    trace = hid("event", e.get("hash", str(e["seq"]))); root = hid("span", e.get("hash", str(e["seq"])), n=8)
    t = ns(e["ts"]); conv = conversation_id(e, e)
    subject = (e.get("data") or {}).get("agent") if e["type"].startswith(SUBJECT_TYPES) else None
    who = subject if isinstance(subject, str) and re.fullmatch(r"[a-z][a-z0-9]{1,15}", subject) else e["actor"]
    dd = e.get("data") or {}
    if dd.get("court") == "court":                        # Court turns: the seat, never the office itself (the Lawyer's opinion on P-006)
        seat = dd.get("seat") or (e["actor"] if e["actor"] not in ("court", "system", "steward") else None)
        if seat and re.fullmatch(r"[a-z][a-z0-9]{1,15}", str(seat)): who = f"court-{seat}"
    attrs = {**base_attrs(e, R), "gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": who, "gen_ai.conversation.id": conv,
             "collective.by": e["actor"]}
    d = e.get("data") or {}
    court_turn = d.get("court") == "court" and (d.get("model") or d.get("judge_model"))
    extra = []
    if court_turn:              # a Court turn: the advocate's, Judge's, or juror's model call, with its model and tokens (P-006)
        model = str(d.get("model") or d.get("judge_model"))
        extra = [Span(name=f"chat {model}", trace=trace, span=hid("court-chat", e.get("hash", str(e["seq"])), n=8), parent=root, start=t, end=t + 1_000_000,
                      attrs={"gen_ai.operation.name": "chat", "gen_ai.request.model": model, "gen_ai.agent.name": who, "gen_ai.conversation.id": conv,
                             "gen_ai.usage.input_tokens": int(d.get("tokens_in") or 0), "gen_ai.usage.output_tokens": int(d.get("tokens_out") or 0),
                             "collective.family": str(d.get("family") or ""), "collective.event_hash": e.get("hash", "")})]
    return extra + [Span(name=f"invoke_agent {who}", trace=trace, span=root, parent=None, start=t, end=t + 2_000_000, attrs=attrs),
            Span(name=f"execute_tool {e['type']}", trace=trace, span=hid("act", e.get("hash", str(e["seq"])), n=8), parent=root,
                 start=t, end=t + 1_000_000,
                 attrs={"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": e["type"], "gen_ai.agent.name": who,
                        "gen_ai.conversation.id": conv, "collective.event_hash": e.get("hash", ""), "collective.seq": e["seq"]})]

# ---------- the roster: every agent on the floor is an agent in Weave, before its first run too (E-0113) ----------
def roster_spans(R, classes, now_ns):
    """One registration turn per agent, whose ids come from its roster entry: a new or changed agent gets a new
    turn, and an unchanged one is never sent twice."""
    out = []
    for k, a in R.items():
        c = classes.get(a.get("class", ""), {})
        entry = json.dumps({x: a.get(x) for x in ("name", "class", "room", "status", "votes", "motion")}, sort_keys=True)
        trace = hid("roster", k, entry); root = hid("roster-span", k, entry, n=8)
        attrs = {"gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": k, "gen_ai.agent.id": k,
                 "gen_ai.agent.description": redact(f"{a.get('name', k)}: {c.get('name', a.get('class', ''))}. {c.get('about', '')}")[:300],
                 "gen_ai.conversation.id": f"roster-{k}", "collective.office": k, "collective.class": a.get("class", ""),
                 "collective.room": a.get("room", ""), "collective.status": a.get("status", ""), "collective.votes": bool(a.get("votes")),
                 "collective.motion": a.get("motion", "") or "", "collective.event_type": "agent.registered", "collective.private_mode": MODE}
        out.append(Span(name=f"invoke_agent {k}", trace=trace, span=root, parent=None, start=now_ns, end=now_ns + 1_000_000, attrs=attrs))
        out.append(Span(name="execute_tool agent.registered", trace=trace, span=hid("roster-act", k, entry, n=8), parent=root, start=now_ns,
                        end=now_ns + 1_000_000, attrs={"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": "agent.registered",
                                                       "gen_ai.agent.name": k, "gen_ai.conversation.id": f"roster-{k}"}))
    return out

def register_roster(exp):
    """Send the registration of any agent whose roster entry is new or changed since the last pass."""
    from opentelemetry.sdk.trace.export import SpanExportResult
    st = load_state(); sent = set(st.get("registered", []))
    try: classes = json.loads((ROOT / "agents/classes.json").read_text())["classes"]
    except (OSError, ValueError, KeyError): classes = {}
    spans = [s for s in roster_spans(roster(), classes, time.time_ns()) if s["parent"] is None and f"{s['trace']:x}" not in sent]
    if not spans: return 0
    todo = [s for s in roster_spans(roster(), classes, spans[0]["start"]) if s["trace"] in {x["trace"] for x in spans}]
    try: ok = exp.export(to_otel(todo)) == SpanExportResult.SUCCESS
    except Exception: ok = False
    if not ok: return -1
    st = load_state(); st["registered"] = sorted(sent | {f"{s['trace']:x}" for s in spans}); save_state(st)
    return len(spans)

# ---------- state ----------
def load_state():
    try: return json.loads(STATE.read_text())
    except (OSError, ValueError): return {"last_hash": None, "last_seq": -1, "open": {}, "exported_spans": 0}

def save_state(st):
    tmp = STATE.with_suffix(".tmp"); tmp.write_text(json.dumps(st, indent=1)); tmp.replace(STATE)

def pending(evs, st):
    """The events not yet exported: after the last exported hash, plus those held with still-open runs."""
    if st.get("last_hash"):
        idx = next((i for i, e in enumerate(evs) if e.get("hash") == st["last_hash"]), None)
        if idx is None: raise SystemExit("REFUSED: the last exported event isn't in the log any more (a rewind?). Check before exporting again.")
    else: idx = -1
    held = {int(q) for seqs in st.get("open", {}).values() for q in seqs}
    return [e for i, e in enumerate(evs) if i > idx or e["seq"] in held]

def plan(evs, st, now=None):
    """Group pending events into spans. Returns (spans, new_open, last_event)."""
    now = now or datetime.datetime.now(datetime.timezone.utc); R = roster()
    todo = pending(evs, st); runs = {}
    for e in todo:
        if e.get("run"): runs.setdefault(e["run"], []).append(e)
    held = {int(q) for seqs in st.get("open", {}).values() for q in seqs}
    spans, new_open, done = [], {}, set()
    for e in todo:
        rid = e.get("run")
        if rid:
            if rid in done: continue
            done.add(rid); r = runs[rid]
            young = (now - datetime.datetime.fromisoformat(r[0]["ts"].replace("Z", "+00:00"))).total_seconds() < OPEN_RUN_SECS
            if not any(x["type"] == "run.end" for x in r) and young:
                new_open[rid] = [x["seq"] for x in r]; continue
            spans += spans_for_run(rid, r, R)
        elif e["seq"] not in held:
            spans += spans_for_event(e, R)
    newest = [e for e in todo if e["seq"] > st.get("last_seq", -1)]                  # the cursor only moves forward
    return spans, new_open, (newest[-1] if newest else None)

# ---------- export ----------
def exporter():
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    key = os.environ.get("WANDB_API_KEY")
    if not key: return None
    return OTLPSpanExporter(endpoint=os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "https://trace.wandb.ai/agents/otel/v1/traces"),
                            headers={"wandb-api-key": key}, timeout=30)

def to_otel(spans):
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope
    from opentelemetry.trace import SpanContext, SpanKind, TraceFlags, Status, StatusCode
    res = Resource({"wandb.entity": os.environ.get("WEAVE_ENTITY", "rexstjohn-verafy"),
                    "wandb.project": os.environ.get("WEAVE_PROJECT_NAME", "The Collective"),
                    "service.name": "the-collective"})
    scope = InstrumentationScope("collective.otel_bridge", "1")
    out = []
    for s in spans:
        ctx = SpanContext(s["trace"], s["span"], is_remote=False, trace_flags=TraceFlags(TraceFlags.SAMPLED))
        parent = SpanContext(s["trace"], s["parent"], is_remote=False, trace_flags=TraceFlags(TraceFlags.SAMPLED)) if s["parent"] else None
        attrs = {k: v for k, v in s["attrs"].items() if isinstance(v, (str, bool, int, float)) and v != ""}
        out.append(ReadableSpan(name=s["name"], context=ctx, parent=parent, resource=res, attributes=attrs, kind=SpanKind.INTERNAL,
                                start_time=s["start"], end_time=s["end"], status=Status(StatusCode.OK), instrumentation_scope=scope))
    return out

def export_once(exp, warned):
    from opentelemetry.sdk.trace.export import SpanExportResult
    st = load_state(); evs = load_events()
    spans, new_open, last = plan(evs, st)
    if last is None and new_open == st.get("open", {}) and not spans: return 0
    for i in range(0, len(spans), BATCH):
        try: ok = exp.export(to_otel(spans[i:i + BATCH])) == SpanExportResult.SUCCESS
        except Exception as ex: ok = False; err = str(ex)[:200]
        if not ok:
            if not warned.get("w"): print(f"warning: Weave export failed; will retry next pass ({locals().get('err', 'export refused')})", file=sys.stderr)
            warned["w"] = True; return -1                              # nothing advances: the next pass resends this batch's events
    warned["w"] = False
    st["open"] = new_open
    if last is not None: st["last_hash"] = last.get("hash"); st["last_seq"] = last["seq"]
    st["exported_spans"] = st.get("exported_spans", 0) + len(spans)
    st["last_export"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"); save_state(st)
    return len(spans)

# ---------- ops (layer 3B): the spool written by ops.py, sent as Weave ops ----------
OPS_SPOOL = HERE / ".ops_spool.ndjson"
_weave = {}

def weave_client():
    """weave.init once, in this long-running process only; None (after one warning) if it can't."""
    if "c" in _weave: return _weave["c"]
    os.environ.setdefault("WEAVE_PRINT_CALL_LINK", "false"); os.environ.setdefault("WEAVE_IMPLICITLY_PATCH_INTEGRATIONS", "false")
    try:
        import weave
        _weave["c"] = weave.init(f"{os.environ.get('WEAVE_ENTITY', 'rexstjohn-verafy')}/{os.environ.get('WEAVE_PROJECT_NAME', 'The Collective')}")
    except Exception as e:
        print(f"warning: Weave ops not sent this pass ({str(e)[:120]})", file=sys.stderr); return None
    return _weave["c"]

def ship_ops():
    """Send spooled ops from the saved byte offset; the offset only advances past ops Weave accepted."""
    if not OPS_SPOOL.exists(): return 0
    st = load_state(); off = st.get("ops_offset", 0); size = OPS_SPOOL.stat().st_size
    if size <= off: return 0
    c = weave_client()
    if c is None: return -1
    with open(OPS_SPOOL) as f:
        f.seek(off); chunk = f.read(); 
    lines = chunk.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"): lines = lines[:-1]                  # a half-written line waits
    sent = 0
    for line in lines:
        try:
            rec = json.loads(line)
            call = c.create_call(rec["op"], redact(rec.get("inputs") or {}), use_stack=False, display_name=rec["op"],
                                 started_at=datetime.datetime.fromisoformat(rec["started_at"]),
                                 attributes={"kind": "op", "pid": rec.get("pid")})
            ex = None if rec.get("ok", True) else Exception(rec.get("exception", "failed"))
            c.finish_call(call, output=rec.get("output"), exception=ex,
                          ended_at=datetime.datetime.fromisoformat(rec.get("ended_at") or rec["started_at"]))
            sent += 1
        except (ValueError, KeyError): pass                                            # a malformed line is skipped
        off += len(line.encode())
    c.flush()
    st = load_state(); st["ops_offset"] = off; st["ops_sent"] = st.get("ops_sent", 0) + sent; save_state(st)
    return sent

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["backfill", "follow", "status", "plan"])
    ap.add_argument("--every", type=int, default=30); ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()
    if a.cmd == "status":
        st = load_state(); evs = load_events()
        try: waiting = len(pending(evs, st))
        except SystemExit as e: waiting = str(e)
        print(json.dumps({"last_exported_seq": st.get("last_seq"), "last_exported_hash": st.get("last_hash"), "log_last_seq": evs[-1]["seq"] if evs else -1,
                          "waiting": waiting, "open_runs": len(st.get("open", {})), "exported_spans": st.get("exported_spans", 0), "ops_sent": st.get("ops_sent", 0),
                          "ops_waiting": max(0, (OPS_SPOOL.stat().st_size if OPS_SPOOL.exists() else 0) - st.get("ops_offset", 0)),
                          "last_export": st.get("last_export"), "mode": MODE, "key_set": bool(os.environ.get("WANDB_API_KEY"))}, indent=1)); return
    if a.cmd == "plan":
        spans, new_open, last = plan(load_events(), load_state())
        for s in spans[:a.limit]: print(json.dumps({"name": s["name"], "parent": bool(s["parent"]), **s["attrs"]}, default=str)[:400])
        print(f"{len(spans)} spans; {len(new_open)} runs still open"); return
    exp = exporter()
    if exp is None: print("warning: WANDB_API_KEY isn't set (source agents/bin/env.sh); nothing exported", file=sys.stderr); return
    warned = {}
    try:
        while True:
            n = export_once(exp, warned)
            try: register_roster(exp)
            except Exception as e: print(f"warning: roster not registered ({str(e)[:120]})", file=sys.stderr)
            try: ship_ops()
            except Exception as e: print(f"warning: ops not sent ({str(e)[:120]})", file=sys.stderr)
            if a.cmd == "backfill":
                while n > 0: n = export_once(exp, warned)
                print(f"backfill done: {load_state().get('exported_spans', 0)} spans exported in all"); return
            time.sleep(max(10, a.every))
    except KeyboardInterrupt: pass
    finally: exp.shutdown()

if __name__ == "__main__":
    main()
