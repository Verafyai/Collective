"""Spawning, cloning, and retiring agents (Charter Articles 3.6, 3.8; P11).
Run: python3 tests/test_spawn.py   (scratch copy)"""
import json, pathlib, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
import atexit, os
atexit.register(shutil.rmtree, t.parent, True)   # leave nothing behind
os.environ["GIT_CONFIG_GLOBAL"] = str(t.parent / "gitconfig")   # never touch the Steward's ~/.gitconfig
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs", "__pycache__", ".env", "secrets", "*.key"))
for d in (t / "agents/_proposed",):
    if d.exists(): shutil.rmtree(d)
def run(*a, ok=True):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True, cwd=t)
    if ok: assert r.returncode == 0, (a, r.stdout, r.stderr)
    return r.stdout + r.stderr
S = "agents/bin/spawn.py"
def roster(): return {a["key"]: a for a in json.loads((t / "agents/roster.json").read_text())["agents"]}
# refusals
assert "can't be spawned" in run(S, "propose", "--class", "officer", "--name", "Lawyer Two", "--focus", "a second legal opinion", ok=False)
assert "already exists" in run(S, "propose", "--class", "scholar", "--name", "Researcher", "--key", "researcher", "--focus", "duplicate key check", ok=False)
assert "focus" in run(S, "propose", "--class", "scholar", "--name", "Reed", "--focus", "short", ok=False)
assert "can't be used" in run(S, "propose", "--class", "scholar", "--name", "System", "--key", "system", "--focus", "reserved key check", ok=False)
# propose and clone: motions, ghosts, no votes
out = run(S, "propose", "--class", "verifier", "--name", "Vera", "--focus", "Fact-check viral health claims with two primary sources")
assert "proposed Vera as A-" in out
out2 = run(S, "clone", "researcher", "--name", "Reed", "--focus", "Track new benchmarks for LLM judges and agent evaluation")
r = roster(); assert r["vera"]["status"] == "proposed" and r["vera"]["votes"] is False
assert r["reed"]["class"] == "scholar" and r["reed"]["clone_of"] == "researcher"
vera_n = int(r["vera"]["motion"].split("-")[1])
assert "status: proposed" in (t / f"amendments/amendment-{vera_n:03d}.md").read_text()
assert "class: M" in (t / f"amendments/amendment-{vera_n:03d}.md").read_text()
# activation only after the vote passes
assert "must pass first" in run(S, "activate", "vera", ok=False)
for st in ["deliberating", "voting", "passed"]: run("agents/bin/amendment.py", "status", str(vera_n), st)
run(S, "activate", "vera")
assert (t / "agents/vera/ROLE.md").exists() and roster()["vera"]["status"] == "active"
cfg = (t / "agents/config.example.env").read_text()
assert "VERA_INTERVAL=7200" in cfg and 'VERA_TOOLS="Read,Glob,Grep,Write(org/board/**)' in cfg and "awaiting the Steward's ratification" in cfg
assert "WebSearch" not in cfg.split("VERA_TOOLS=")[1].split("\n")[0], "requested tools must not be granted before ratification"
assert 'name = "vera"' in (t / "herdr/projects/collective.toml").read_text()
# sprints: Vera proposes but doesn't vote
out = subprocess.run([sys.executable, "-c", "import sys; sys.argv=['x','status']; sys.path.insert(0,'agents/bin'); import sprint; print(sprint.MEMBERS, 'vera' in sprint.PROPOSERS)"],
                     capture_output=True, text=True, cwd=t).stdout
assert "'vera'" not in out.split("]")[0] and out.strip().endswith("True"), out
# retiring takes its own vote; officers can't be retired this way
assert "officers can't be retired" in run(S, "retire", "lawyer", ok=False)
out = run(S, "retire", "vera", "--reason", "test"); n = int(out.split("A-")[1][:4])
assert "retirement motion" in run(S, "retire-apply", "vera", ok=False)
for st in ["deliberating", "voting", "passed"]: run("agents/bin/amendment.py", "status", str(n), st)
run(S, "retire-apply", "vera")
assert roster()["vera"]["status"] == "retired" and (t / "org/PAUSE-vera").exists()
assert "ok:" in run("agents/bin/amendment.py", "check")
print("spawn tests passed")
