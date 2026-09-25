"""Weekly blog pipeline (Charter Article 19): facts → draft → approval → publish.
Run: python3 tests/test_blog.py   (scratch copy, offline)"""
import pathlib, shutil, subprocess, sys, tempfile, datetime, os, atexit
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
atexit.register(shutil.rmtree, t.parent, True)   # leave nothing behind
os.environ["GIT_CONFIG_GLOBAL"] = str(t.parent / "gitconfig")   # never touch the Steward's ~/.gitconfig
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs", ".env", "secrets", "*.key"))
if (t / "private" / ".git").exists(): shutil.rmtree(t / "private" / ".git")
shutil.rmtree(t / "sprints", True); (t / "sprints").mkdir()        # a fresh week: the live sprints aren't this test's
def sh(*cmd, ok=True):
    r = subprocess.run(list(cmd), capture_output=True, text=True, cwd=t)
    if ok: assert r.returncode == 0, (cmd, r.stdout, r.stderr)
    return r.stdout + r.stderr
py = sys.executable
sh("git", "config", "--global", "user.email", "rex@example.com"); sh("git", "config", "--global", "user.name", "Rex St. John")
sh("agents/bin/repos.sh", "init", "--offline")
sh(py, "agents/bin/eventlog.py", "init", "--actor", "steward")
# a week of activity: a researcher run that writes a brief, a sprint, a post, an incident
rid = sh(py, "agents/bin/eventlog.py", "run-start", "--actor", "researcher").strip()
(t / "research/briefs").mkdir(parents=True, exist_ok=True); (t / "research/briefs/du-2023.md").write_text("# Brief\n")
sh(py, "agents/bin/eventlog.py", "run-end", "--actor", "researcher", "--run", rid)
sh(py, "agents/bin/sprint.py", "open", "--theme", "Best course of action")
sh(py, "agents/bin/eventlog.py", "record", "--actor", "social", "--type", "effect.posted", "--data", '{"url": "https://x.com/VerafyAI/status/1"}')
sh(py, "agents/bin/eventlog.py", "record", "--actor", "system", "--type", "incident", "--data", '{"kind": "out_of_band_change"}')
sh(py, "agents/bin/edict.py", "new", "--title", "Private edict", "--text", "SECRET-ISH WORDS THAT MUST NOT BE PUBLISHED")
out = sh(py, "agents/bin/weekly-digest.py")
facts = next((t / "blog/_facts").glob("*.md")).read_text()
for must in ["## Votes", "## Discussion", "## Changes", "file changes across", "## Sprints", "S-0001", "**researcher**: 1 runs, 1 file changes", "Research briefs: 1 (research/briefs/du-2023.md)",
             "Posts published on X: 1", "Incidents: 1 (count only", "Steward edicts issued: 1 (count only", "C-0006", "A-0009"]:
    assert must in facts, (must, facts)
assert "SECRET-ISH" not in facts, "edict content must never reach the facts file"
# the post can't be published without approval
day = datetime.date.today().isoformat()
draft = t / "private/outbox/pending" / f"{day}-blog-week-one.md"
draft.parent.mkdir(parents=True, exist_ok=True); draft.write_text("# Week of " + day + ": The Collective wakes up\n\nFacts-based post.\n")
assert "REFUSED" in sh("agents/bin/blog-publish.sh", str(draft), ok=False)
sh("agents/bin/approve.sh", str(draft))
r = sh("agents/bin/blog-publish.sh", f"private/outbox/approved/{draft.name}")
post = t / "blog" / f"{day}-week-one.md"
assert post.exists() and "Approved by rex" not in post.read_text() and "Written by the Collective" in post.read_text(), r
assert f"blog/{day}-week-one.md" in sh("git", "ls-files", "blog/")
assert (t / "private/outbox/posted" / draft.name).exists()
assert "blog.published" in sh(py, "agents/bin/playback.py")
print("blog tests passed")
