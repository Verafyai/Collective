"""Amendments folder (Article 7.12) and projects (Article 21). Run: python3 tests/test_amendments_projects.py
Works on a scratch copy."""
import pathlib, shutil, subprocess, sys, tempfile, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs"))
py = sys.executable
def run(*a, ok=True):
    r = subprocess.run([py, *a], capture_output=True, text=True, cwd=t)
    if ok: assert r.returncode == 0, (a, r.stdout, r.stderr)
    return r.stdout + r.stderr
A, P = "agents/bin/amendment.py", "agents/bin/projects.py"

# --- amendments ---
shutil.rmtree(t / "amendments")
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
(t / f"amendments/amendment-{new-1:03d}.md").unlink()
assert "missing (numbers never skip" in run(A, "check", ok=False)
run(A, "sync"); assert "ok:" in run(A, "check")                               # regenerated from the verified log

# --- projects ---
assert "REFUSED" in run(P, "new", "--name", "X", "--slug", "x", "--owner", "prototyper", ok=False)   # no spec, no project
(t / "tiny.md").write_text("too short")
assert "REFUSED" in run(P, "new", "--name", "X", "--slug", "x", "--owner", "prototyper", "--spec", "tiny.md", ok=False)
(t / "spec.md").write_text("# Source linkage\n\n" + "Trace every claim to its sources and catch circular citation. " * 6)
assert "created P-002" in run(P, "new", "--name", "Source linkage", "--slug", "source linkage", "--owner", "prototyper", "--spec", "spec.md")
d = t / "projects/002-source-linkage"
for fn in ("PROJECT.md", "spec.md", "discussion.md"): assert (d / fn).exists()
run(P, "version", "2", "--title", "First slice"); run(P, "version", "2", "--title", "Second slice")
assert sorted(p.name for p in (d / "versions").glob("*.md")) == ["version-001.md", "version-002.md"]
assert "REFUSED" in run(P, "release", "2", "1", ok=False)                      # release notes required
v1 = d / "versions/version-001.md"
v1.write_text(v1.read_text().replace("(filled in on release: what a human will see, what's known not to work)", "Shows claim-to-source links for one article."))
run(P, "release", "2", "1")
assert "current_version: 001" in (d / "PROJECT.md").read_text()
v2 = d / "versions/version-002.md"
v2.write_text(v2.read_text().replace("(filled in on release: what a human will see, what's known not to work)", "Adds circular-citation detection."))
run(P, "release", "2", "2")
assert "status: superseded" in v1.read_text() and "current_version: 002" in (d / "PROJECT.md").read_text()
run(P, "comment", "2", "--author", "human:rex", "--kind", "suggestion", "--text", "Try it on the Wikipedia article about the Moon.")
disc = (d / "discussion.md").read_text()
assert "### human:rex" in disc and "suggestion" in disc and disc.count("\n### ") >= 5   # created, 2 versions, 2 releases, comment
assert "REFUSED" in run(P, "comment", "2", "--author", "x", "--kind", "shout", "--text", "hi", ok=False)
assert "ok: 2 projects valid" in run(P, "check")
assert "P-002" in (t / "projects/INDEX.md").read_text()
print("amendments and projects tests passed")
