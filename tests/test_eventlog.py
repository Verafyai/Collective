"""The event log under concurrent writers (Charter Article 12; the Auditor's 2026-09-25 fork incident).
Twenty processes append at once; the chain must still verify, with every seq exactly once. Run: python3 tests/test_eventlog.py"""
import atexit, json, pathlib, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()); atexit.register(shutil.rmtree, t, True)
for rel in ("agents/bin/eventlog.py", "agents/observability/ops.py", "agents/observability/redact.py"):
    (t / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy(ROOT / rel, t / rel)
(t / "CHARTER.md").write_text("# a stand-in charter\n"); (t / "private").mkdir()
env = {"PATH": "/usr/bin:/bin", "OBS_OPS": "0"}
EL = [sys.executable, str(t / "agents/bin/eventlog.py")]
assert subprocess.run(EL + ["init", "--actor", "steward"], cwd=t, capture_output=True, env=env).returncode == 0
procs = [subprocess.Popen(EL + ["run-start", "--actor", f"a{i}"] if i % 2 else EL + ["record", "--actor", f"a{i}", "--type", "test.event", "--data", json.dumps({"i": i})],
                          cwd=t, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) for i in range(20)]
for p in procs: p.wait(); assert p.returncode == 0, p.stderr.read()
seqs = [json.loads(l)["seq"] for l in (t / "private/ledger/events.ndjson").read_text().splitlines()]
assert seqs == list(range(1, len(seqs) + 1)), "every seq exactly once, in order"
v = subprocess.run(EL + ["verify"], cwd=t, capture_output=True, text=True, env=env)
assert v.returncode == 0 and v.stdout.startswith("ok"), v.stdout + v.stderr
print("eventlog tests passed")
