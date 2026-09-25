"""The Weave mirror (Charter Article 12.10; agents/bin/weave_sync.py). Offline: a fake client, a scratch event log.
Run: python3 tests/test_weave.py"""
import datetime, gzip, hashlib, json, pathlib, shutil, sys, tempfile, atexit

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents/bin"))
import weave_sync as w

t = pathlib.Path(tempfile.mkdtemp()); atexit.register(shutil.rmtree, t, True)
w.EVENTS, w.BLOBS, w.STATE = t / "events.ndjson", t / "blobs", t / "state.json"

def blob(text):
    raw = text.encode(); h = hashlib.sha256(raw).hexdigest()
    (w.BLOBS / h[:2]).mkdir(parents=True, exist_ok=True); (w.BLOBS / h[:2] / h[2:]).write_bytes(gzip.compress(raw)); return h

now = datetime.datetime.now(datetime.timezone.utc)
iso = lambda mins: (now - datetime.timedelta(minutes=mins)).isoformat(timespec="seconds")
key = "sk-ant-" + "a" * 40
transcript = "working...\nmy key is " + key + "\n" + json.dumps({"type": "result", "total_cost_usd": 0.42, "usage": {"input_tokens": 10, "output_tokens": 20}})
E = [
    {"seq": 0, "ts": iso(60), "actor": "steward", "type": "edict.issued", "run": None, "data": {"summary": "E-0001: a title"}},
    {"seq": 1, "ts": iso(50), "actor": "pm", "type": "run.start", "run": "pm-1", "data": {}},
    {"seq": 2, "ts": iso(50), "actor": "pm", "type": "agent.prompt", "run": "pm-1", "data": {"blob": blob("the prompt")}},
    {"seq": 3, "ts": iso(49), "actor": "ideas", "type": "run.start", "run": "ideas-1", "data": {}},        # still open
    {"seq": 4, "ts": iso(48), "actor": "pm", "type": "file.put", "run": "pm-1", "data": {"path": "org/board/x.md", "blob": "abc"}},
    {"seq": 5, "ts": iso(47), "actor": "pm", "type": "agent.transcript", "run": "pm-1", "data": {"blob": blob(transcript)}},
    {"seq": 6, "ts": iso(46), "actor": "pm", "type": "run.end", "run": "pm-1", "data": {"files_changed": "1"}},
    {"seq": 7, "ts": iso(45), "actor": "steward", "type": "agent.moved", "run": None, "data": {"summary": "moved api_key=hunter2secret"}},
]
w.EVENTS.write_text("".join(json.dumps(e) + "\n" for e in E))

class Call:
    def __init__(self, op, inputs, parent): self.op, self.inputs, self.parent, self.output = op, inputs, parent, None
class Fake:
    def __init__(self): self.calls = []
    def create_call(self, op, inputs, parent=None, **kw):
        c = Call(op, inputs, parent); self.calls.append(c); return c
    def finish_call(self, c, output=None, **kw): c.output = output
    def flush(self): pass

f = Fake(); n = w.sync(f)
ops = [c.op for c in f.calls]
assert ops.count("collective.run") == 1 and "collective.edict.issued" in ops and "collective.agent.moved" in ops, ops
run = next(c for c in f.calls if c.op == "collective.run")
kids = [c for c in f.calls if c.parent is run]
assert {c.op for c in kids} == {"collective.agent.prompt", "collective.file.put", "collective.agent.transcript"}, [c.op for c in kids]
assert run.output["cost_usd"] == 0.42 and run.output["ended"] is True, run.output
tr = next(c for c in kids if c.op == "collective.agent.transcript")
assert key not in json.dumps(tr.inputs) and "[redacted: secret]" in tr.inputs["text"], "secrets never leave the machine"
assert "hunter2secret" not in json.dumps([c.inputs for c in f.calls]), "key=value secrets are redacted too"
fp = next(c for c in kids if c.op == "collective.file.put")
assert "text" not in fp.inputs, "file contents are never sent"
st = json.loads(w.STATE.read_text())
assert st["seq"] == 7 and list(st["open"]) == ["ideas-1"], st                 # the open run waits; nothing else does
# the open run ends: only it is sent next time, once
w.EVENTS.write_text(w.EVENTS.read_text() + json.dumps({"seq": 8, "ts": iso(1), "actor": "ideas", "type": "run.end", "run": "ideas-1", "data": {}}) + "\n")
f2 = Fake(); w.sync(f2)
assert [c.op for c in f2.calls] == ["collective.run"] and f2.calls[0].output["ended"] and not json.loads(w.STATE.read_text())["open"]
f3 = Fake(); assert w.sync(f3) == 0 and not f3.calls, "each event is sent once"
print("weave tests passed")
