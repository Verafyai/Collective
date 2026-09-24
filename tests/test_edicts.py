"""Tests for agents/bin/edict.py (Charter Article 15). Run: python3 tests/test_edicts.py
Needs the private repo checked out at private/ (edicts are private)."""
import pathlib, shutil, subprocess, sys, tempfile, atexit
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp())
atexit.register(shutil.rmtree, t, True)   # leave nothing behind
shutil.copytree(ROOT / "agents", t / "agents", ignore=shutil.ignore_patterns(".env", "logs")); shutil.copytree(ROOT / "private" / "edicts", t / "private" / "edicts")
E = [sys.executable, str(t / "agents/bin/edict.py")]
def run(*a): return subprocess.run(E + list(a), capture_output=True, text=True, cwd=t)
assert run("check").returncode == 0
n = len(list((t / "private" / "edicts").glob("E-*.md")))
r = run("new", "--title", "Supersede test", "--text", "New direction.", "--supersedes", "E-0001")
assert f"issued E-{n+1:04d}" in r.stdout, r.stdout
assert "superseded by" in next((t / "private" / "edicts").glob("E-0001-*.md")).read_text()
assert "REFUSED" in run("new", "--title", "x", "--text", "y", "--supersedes", "E-9999").stdout + run("new", "--title", "x", "--text", "y", "--supersedes", "E-9999").stderr
f = next((t / "private" / "edicts").glob("E-0002-*.md")); orig = f.read_text()
f.write_text(orig.replace("simple and easy", "complex")); r = run("check")
assert r.returncode == 1 and "original words changed" in r.stdout, r.stdout
f.write_text(orig + "- later: outcome note.\n"); assert run("check").returncode == 0
assert "E-0022" in run("replay", "--from", "E-0022", "--to", "E-0022").stdout
print("edict tests passed")
