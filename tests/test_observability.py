"""Observability (P-005; Charter Article 12.10): redaction, the OpenTelemetry bridge, ops, and the privacy mode.
Offline: a scratch event log, a fake exporter, and an unreachable endpoint. Run: python3 tests/test_observability.py
(system python for redaction and ops; the bridge parts need agents/.venv and are skipped without it)."""
import datetime, gzip, hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile, atexit

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents/observability")); sys.path.insert(0, str(ROOT / "agents/bin"))
os.environ["OBS_PRIVATE_MODE"] = "metadata"
from redact import redact

# ---- redaction: secrets, emails, and phones go; ordinary Collective text stays ----
j = "".join
secrets = [j(["sk-", "ant-api03-", "x" * 90]), j(["gh", "p_", "a1B2" * 9]), j(["AK", "IA", "IOSFODNN7EXAMPLE"]), j(["wandb", "_v1_", "Q" * 60]),
           j(["xai", "-", "R" * 40]), "rex@example.com", "425-555-0142", j(["pass", "word = ", "hunter22x"])]
for s in secrets: assert s not in redact(f"before {s} after"), s
clean = "The Lawyer filed opinion C-0012 on sprint S-0001 at 2026-09-25T02:00:00Z; run pm-20260925T011824-5fea64 changed 7 files."
assert redact(clean) == clean
assert redact({"a": [f"x {secrets[0]}"]})["a"][0] == "x [redacted]"

# ---- the env file never holds a key ----
assert "wandb_v1_" not in (ROOT / "agents/bin/env.sh").read_text() and "WANDB_API_KEY=" not in (ROOT / "agents/bin/env.sh").read_text().replace("WANDB_API_KEY=$", "")

# ---- ops: the function runs as before, the spool gets metadata only, OBS_OPS=0 turns it off ----
t = pathlib.Path(tempfile.mkdtemp()); atexit.register(shutil.rmtree, t, True)
import ops
ops.SPOOL = t / "spool.ndjson"
@ops.op("test.greet", keep=("who",))
def greet(who, secret_note): return f"hello {who}"
assert greet("pm", "private words E-0001 " + secrets[0]) == "hello pm"
rec = json.loads(ops.SPOOL.read_text().splitlines()[-1])
assert rec["op"] == "test.greet" and rec["inputs"]["who"] == "pm" and rec["inputs"]["secret_note"]["type"] == "str", rec
assert "private words" not in ops.SPOOL.read_text() and secrets[0] not in ops.SPOOL.read_text()
@ops.op("test.boom")
def boom(): raise ValueError("no")
try: boom(); raise AssertionError("the exception must propagate")
except ValueError: pass
assert json.loads(ops.SPOOL.read_text().splitlines()[-1])["ok"] is False
os.environ["OBS_OPS"] = "0"; n = len(ops.SPOOL.read_text().splitlines()); greet("x", "y"); assert len(ops.SPOOL.read_text().splitlines()) == n
os.environ["OBS_OPS"] = "1"
# a traced script behaves exactly as before
out = subprocess.run([sys.executable, str(ROOT / "agents/bin/edict.py"), "check"], capture_output=True, text=True, env={**os.environ, "OBS_OPS": "0"})
assert out.returncode == 0

VENV = ROOT / "agents/.venv/bin/python"
if not VENV.exists() or os.environ.get("_OBS_IN_VENV") != "1":
    if VENV.exists():                                                   # the bridge needs the OTel SDK: rerun this file in the venv
        r = subprocess.run([str(VENV), __file__], env={**os.environ, "_OBS_IN_VENV": "1"}, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr[-2000:]); sys.exit(r.returncode)
    print("observability tests passed (bridge skipped: no agents/.venv)"); sys.exit(0)

# ---- the bridge, on a scratch log ----
import otel_bridge as b
b.EVENTS, b.BLOBS, b.STATE = t / "events.ndjson", t / "blobs", t / "state.json"
def blob(text):
    raw = text.encode(); h = hashlib.sha256(raw).hexdigest()
    (b.BLOBS / h[:2]).mkdir(parents=True, exist_ok=True); (b.BLOBS / h[:2] / h[2:]).write_bytes(gzip.compress(raw)); return h
now = datetime.datetime.now(datetime.timezone.utc)
iso = lambda m: (now - datetime.timedelta(minutes=m)).isoformat(timespec="seconds")
claude_tr = "\n".join([
    json.dumps({"type": "assistant", "message": {"id": "m1", "model": "claude-x", "usage": {"input_tokens": 5, "output_tokens": 7}, "content": [{"type": "text", "text": "SECRET REASONING"}, {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": "private/edicts/E-0001.md"}}]}}),
    json.dumps({"type": "assistant", "message": {"id": "m2", "model": "claude-x", "usage": {"input_tokens": 3, "output_tokens": 4}, "content": [{"type": "tool_use", "id": "t2", "name": "Write", "input": {}}]}}),
    json.dumps({"type": "result", "total_cost_usd": 0.5, "usage": {"input_tokens": 8, "output_tokens": 11, "cache_read_input_tokens": 99}})])
grok_tr = "\n".join([json.dumps({"type": "usage", "usage": {"input_tokens": 10, "output_tokens": 2}}), json.dumps({"type": "tool_call", "toolName": "read_file", "toolCallId": "c1"}),
                     json.dumps({"type": "end", "modelUsage": {"grok-4.7": {}}, "total_cost_usd": "0.1", "usage": {"input_tokens": 10, "output_tokens": 2}})])
E = [{"type": "edict.issued", "actor": "steward", "run": None, "data": {"summary": "E-0001: a private title", "edict": "E-0001"}},
     {"type": "run.start", "actor": "pm", "run": "pm-1", "data": {"model": "default"}},
     {"type": "agent.prompt", "actor": "pm", "run": "pm-1", "data": {"blob": blob("PRIVATE PROMPT TEXT")}},
     {"type": "file.put", "actor": "pm", "run": "pm-1", "data": {"path": "private/outbox/pending/x.md", "blob": "ab"}},
     {"type": "file.put", "actor": "pm", "run": "pm-1", "data": {"path": "org/board/2026-09-25-standup.md", "blob": "cd"}},
     {"type": "agent.transcript", "actor": "pm", "run": "pm-1", "data": {"blob": blob(claude_tr)}},
     {"type": "run.end", "actor": "pm", "run": "pm-1", "data": {"files_changed": "2"}},
     {"type": "run.start", "actor": "social", "run": "social-1", "data": {}},
     {"type": "agent.transcript", "actor": "social", "run": "social-1", "data": {"blob": blob(grok_tr)}},
     {"type": "run.end", "actor": "social", "run": "social-1", "data": {}},
     {"type": "run.start", "actor": "ideas", "run": "ideas-1", "data": {}},                        # still open
     {"type": "shell.input", "actor": "steward", "run": None, "data": {"line": "export TOKEN=abc", "cmd": "shell"}},
     {"type": "file.put", "actor": "external", "run": None, "data": {"path": "agents/.venv/lib/x.py", "blob": "ef"}},
     {"type": "agent.moved", "actor": "steward", "run": None, "data": {"summary": "Charlie moved", "agent": "charlie", "from": "lab", "to": "studio"}}]
prev = "GENESIS"
for i, e in enumerate(E):
    e.update(seq=i + 1, ts=iso(60 - i), prev=prev); e["hash"] = hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest(); prev = e["hash"]
b.EVENTS.write_text("".join(json.dumps(e) + "\n" for e in E))
spans, held, last = b.plan(b.load_events(), b.load_state())
names = [s["name"] for s in spans]
pm = next(s for s in spans if s["name"] == "invoke_agent pm")
kids = [s for s in spans if s["parent"] == pm["span"]]
assert [s["name"] for s in kids if s["name"].startswith("chat")] == ["chat claude-x", "chat claude-x"], names
assert {"execute_tool Read", "execute_tool Write", "execute_tool file.put"} <= {s["name"] for s in kids}
assert pm["attrs"]["gen_ai.usage.output_tokens"] == 11 and pm["attrs"]["collective.cost_usd"] == 0.5 and pm["attrs"]["gen_ai.conversation.id"].startswith("standup-")
assert any(s["name"] == "chat grok-4.7" for s in spans) and any(s["name"] == "execute_tool read_file" for s in spans)
dump = json.dumps([s["attrs"] for s in spans])
for bad in ("SECRET REASONING", "PRIVATE PROMPT TEXT", "private/outbox", "a private title", "export TOKEN", "private/edicts"):
    assert bad not in dump, bad                                                  # metadata mode: no text, no private paths, no typed lines
assert '"collective.edict": "E-0001"' in dump, "ids are metadata"
assert not any("agents/.venv" in json.dumps(s["attrs"]) for s in spans), "tool environments aren't activity"
moved = next(s for s in spans if s["attrs"].get("collective.event_type") == "agent.moved" and s["parent"] is None)
assert moved["attrs"]["gen_ai.agent.name"] == "charlie" and moved["attrs"]["collective.by"] == "steward", "events about an agent are filed under it"
assert list(held) == ["ideas-1"] and last["seq"] == len(E)
spans2, _, _ = b.plan(b.load_events(), b.load_state())
assert [(s["trace"], s["span"]) for s in spans] == [(s["trace"], s["span"]) for s in spans2], "span ids come from the log: a resend never duplicates"

# exporting: success advances the cursor forward only; a failure changes nothing and nothing crashes
from opentelemetry.sdk.trace.export import SpanExportResult
class Fake:
    def __init__(self, ok=True): self.ok, self.got = ok, []
    def export(self, spans): self.got += spans; return SpanExportResult.SUCCESS if self.ok else SpanExportResult.FAILURE
f = Fake(); assert b.export_once(f, {}) == len(spans) and b.load_state()["last_seq"] == len(E)
assert b.export_once(f, {}) == 0, "nothing new: nothing sent, the cursor stays"
assert b.load_state()["last_seq"] == len(E)
st0 = b.STATE.read_text(); b.EVENTS.write_text(b.EVENTS.read_text() + json.dumps({**E[0], "seq": len(E) + 1, "hash": "z" * 64, "prev": prev}) + "\n")
assert b.export_once(Fake(ok=False), {}) == -1 and b.STATE.read_text() == st0, "a failed export leaves the state alone"
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
dead = OTLPSpanExporter(endpoint="http://127.0.0.1:9/agents/otel/v1/traces", headers={"wandb-api-key": "x"}, timeout=2)
assert b.export_once(dead, {}) == -1 and b.STATE.read_text() == st0, "W&B unreachable: one warning, no crash, nothing lost"

# every agent on the roster registers once; a changed entry registers again
R = {"pm": {"name": "PM", "class": "officer", "room": "council", "status": "active"}, "charlie": {"name": "Charlie", "class": "sentinel", "room": "studio", "status": "active"}}
r1 = b.roster_spans(R, {}, 1); r2 = b.roster_spans(R, {}, 2)
assert [s["trace"] for s in r1] == [s["trace"] for s in r2] and {s["attrs"]["gen_ai.agent.name"] for s in r1} == {"pm", "charlie"}
R["charlie"]["room"] = "lab"; assert b.roster_spans(R, {}, 3)[2]["trace"] != r1[2]["trace"]
print("observability tests passed")
