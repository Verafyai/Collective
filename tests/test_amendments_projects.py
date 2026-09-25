"""Amendments folder (Article 7.12) and projects (Article 21). Run: python3 tests/test_amendments_projects.py
Works on a scratch copy."""
import pathlib, shutil, subprocess, sys, tempfile, re, atexit
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
atexit.register(shutil.rmtree, t.parent, True)   # leave nothing behind
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".venv", "node_modules", ".git", "ledger", "logs", "pdfs", ".env", "secrets", "*.key"))
py = sys.executable
def run(*a, ok=True):
    r = subprocess.run([py, *a], capture_output=True, text=True, cwd=t)
    if ok: assert r.returncode == 0, (a, r.stdout, r.stderr)
    return r.stdout + r.stderr
A, P = "agents/bin/amendment.py", "agents/bin/projects.py"

# --- amendments ---
for f in (t / "amendments").glob("amendment-*.md"):                   # drop every file the log can regenerate;
    if "status: ratified" in f.read_text(): f.unlink()                 # open proposals (not in the log) stay
run(A, "sync"); assert "ok:" in run(A, "check")
n_log = len(list((t / "amendments").glob("amendment-*.md")))
assert (t / "amendments/amendment-001.md").exists() and "status: ratified" in (t / "amendments/amendment-001.md").read_text()
(t / "prop.md").write_text("Add Article 99: agents say thank you.")
out = run(A, "new", "--title", "Gratitude", "--class", "C", "--proposer", "social", "--file", "prop.md")
new = n_log
assert f"amendment-{new:03d}.md" in out, out
assert "REFUSED" in run(A, "status", str(new), "voting", ok=False)            # can't skip deliberation
run(A, "status", str(new), "deliberating"); run(A, "status", str(new), "voting")
f = t / f"amendments/amendment-{new:03d}.md"; orig = f.read_text()
f.write_text(orig.replace("thank you", "thanks a lot"))                      # tamper with the frozen text
assert "changed after it was frozen" in run(A, "check", ok=False)
f.write_text(orig); run(A, "status", str(new), "rejected")
assert "REFUSED" in run(A, "status", str(new), "passed", ok=False)           # rejected is final
assert "ok:" in run(A, "check")                                              # a rejected proposal keeps its number
last = max(int(f.stem[-3:]) for f in (t / "amendments").glob("amendment-*.md") if "status: ratified" in f.read_text())
(t / f"amendments/amendment-{last:03d}.md").unlink()                          # a logged one: sync can regenerate it
assert "missing (numbers never skip" in run(A, "check", ok=False)
run(A, "sync"); assert "ok:" in run(A, "check")                               # regenerated from the verified log
g = t / "amendments/amendment-001.md"; good = g.read_text()                  # a number used twice is caught (A-0021, A-0037)
g.write_text(re.sub(r"^title: .*$", "title: Spawn Someone Else (Scholar)", good, count=1, flags=re.M))
assert "a number used twice" in run(A, "check", ok=False); g.write_text(good)

# --- projects ---
assert "REFUSED" in run(P, "new", "--name", "X", "--slug", "x", "--owner", "prototyper", ok=False)   # no spec, no project
(t / "tiny.md").write_text("too short")
assert "REFUSED" in run(P, "new", "--name", "X", "--slug", "x", "--owner", "prototyper", "--spec", "tiny.md", ok=False)
(t / "spec.md").write_text("# Source linkage\n\n" + "Trace every claim to its sources and catch circular citation. " * 6)
NP = max(int(x.name[:3]) for x in (t / "projects").glob("[0-9][0-9][0-9]-*")) + 1   # the next project number, whatever exists live
assert f"created P-{NP:03d}" in run(P, "new", "--name", "Source linkage", "--slug", "source linkage", "--owner", "prototyper", "--spec", "spec.md")
d = t / f"projects/{NP:03d}-source-linkage"
for fn in ("PROJECT.md", "spec.md", "discussion.md"): assert (d / fn).exists()
run(P, "version", str(NP), "--title", "First slice"); run(P, "version", str(NP), "--title", "Second slice")
assert sorted(p.name for p in (d / "versions").glob("*.md")) == ["version-001.md", "version-002.md"]
assert "REFUSED" in run(P, "release", str(NP), "1", ok=False)                      # release notes required
v1 = d / "versions/version-001.md"
v1.write_text(v1.read_text().replace("(filled in on release: what a human will see, what's known not to work)", "Shows claim-to-source links for one article."))
run(P, "release", str(NP), "1")
assert "current_version: 001" in (d / "PROJECT.md").read_text()
v2 = d / "versions/version-002.md"
v2.write_text(v2.read_text().replace("(filled in on release: what a human will see, what's known not to work)", "Adds circular-citation detection."))
run(P, "release", str(NP), "2")
assert "status: superseded" in v1.read_text() and "current_version: 002" in (d / "PROJECT.md").read_text()
run(P, "comment", str(NP), "--author", "human:rex", "--kind", "suggestion", "--text", "Try it on the Wikipedia article about the Moon.")
disc = (d / "discussion.md").read_text()
assert "### human:rex" in disc and "suggestion" in disc and disc.count("\n### ") >= 5   # created, 2 versions, 2 releases, comment
assert "REFUSED" in run(P, "comment", str(NP), "--author", "x", "--kind", "shout", "--text", "hi", ok=False)
assert f"ok: {NP} projects valid" in run(P, "check")
assert f"P-{NP:03d}" in (t / "projects/INDEX.md").read_text()
print("amendments and projects tests passed")
