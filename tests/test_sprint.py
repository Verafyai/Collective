"""End-to-end test of the Sprint cycle (Charter Article 14). Run: python3 tests/test_sprint.py
Uses a scratch copy; the real repo is untouched."""
import pathlib, shutil, subprocess, sys, tempfile, json, atexit
ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp())
atexit.register(shutil.rmtree, t, True)   # leave nothing behind
shutil.copytree(ROOT / "agents", t / "agents", ignore=shutil.ignore_patterns(".venv", "node_modules", ".env", "logs")); (t / "org").mkdir()
shutil.copytree(ROOT / "org" / "cases", t / "org" / "cases")
R = t / "agents/roster.json"; r = json.loads(R.read_text())                 # the scenario's nine offices, whatever the live roster says
for a in r["agents"]:
    if a["key"] == "media": a["status"] = "active"
R.write_text(json.dumps(r))
S = [sys.executable, str(t / "agents/bin/sprint.py")]
def run(*a, ok=True):
    r = subprocess.run(S + list(a), capture_output=True, text=True, cwd=t)
    if ok: assert r.returncode == 0, (a, r.stdout, r.stderr)
    return r.stdout + r.stderr
run("open", "--theme", "What is the best course of action this week?")
sp = t / "sprints/S-0001"
def proposal(role, justification="Advances the Mission and Article 1; follows C-0001 and C-0003."):
    (sp / "proposals" / f"{role}.md").write_text(f"""# {role} proposal
## Objective
Do {role} work.
## Work items
- item one
## Success criteria
- one measurable outcome
## Justification
{justification}
## Budget
10 runs
## Risks
low
## Dependencies
none
""")
for r in ["pm", "researcher", "ideas", "prototyper", "media", "social", "scribe", "lawyer", "auditor"]: proposal(r)
proposal("media", "Because I said so.")                                   # missing citations
assert "must cite" in run("check", ok=False)
assert "REFUSED" in run("freeze", ok=False)
proposal("media")
frozen = {l.split(" | ")[0]: l.split("frozen ")[1] for l in run("freeze").strip().splitlines()}
voters = ["pm", "researcher", "ideas", "prototyper", "media", "social"]
plan = {"S-0001-pm": "yes", "S-0001-social": "yes", "S-0001-researcher": "yes", "S-0001-ideas": "no",
        "S-0001-prototyper": "yes", "S-0001-media": "yes", "S-0001-scribe": "yes", "S-0001-lawyer": "yes", "S-0001-auditor": "yes"}
for v in voters:
    lines = []
    for item, vote in plan.items():
        sha8 = frozen[item] if not (v == "social" and item == "S-0001-researcher") else "deadbeef"   # stale ballot → void
        lines.append(f"{item} | {vote} | {sha8} | reason from {v}")
    (sp / "ballots" / f"{v}.md").write_text("\n".join(lines))
out = run("tally")
meta = json.loads((sp / "sprint.json").read_text())["items"]
assert meta["S-0001-ideas"]["outcome"] == "rejected", out
assert "ideas" not in meta["S-0001-ideas"]["votes"], "owner must not vote on own item"
assert "social" not in meta["S-0001-researcher"]["votes"], "stale-hash ballot must be void"
assert meta["S-0001-scribe"]["outcome"] == "approved" and len(meta["S-0001-scribe"]["votes"]) == 6   # non-voting officer: all 6 voters vote
assert all(o not in m["votes"] for o in ("scribe", "lawyer", "auditor") for m in meta.values()), "non-voting officers never vote"
out = run("steward", "--approve", "--veto", "S-0001-media", "--reason", "Video tooling not ready")
meta = json.loads((sp / "sprint.json").read_text())["items"]
assert meta["S-0001-media"]["outcome"] == "vetoed" and meta["S-0001-media"]["case"].startswith("C-")
assert all(v["case"].startswith("C-") for v in meta.values()), out
assert "S-0001-social" in (sp / "plan.md").read_text() and "S-0001-ideas: rejected" in (sp / "plan.md").read_text()
assert "REFUSED" in run("grade", ok=False)                                    # wrong phase
run("postmortem")
for g in voters:
    (sp / "postmortem/grades" / f"{g}.md").write_text("\n".join(
        f"{i} | 4 | 3 | 4 | 4 | 3 | note" for i in ["S-0001-social", "S-0001-researcher", "S-0001-prototyper", "S-0001-scribe"]))
run("grade")
rep = (sp / "postmortem/report.md").read_text()
assert "| S-0001-social | social | 4 | 3 | 4 | 4 | 3 | 3.6 | A | 5 |" in rep, rep        # 6 voters minus the owner
assert "| S-0001-scribe | scribe | 4 | 3 | 4 | 4 | 3 | 3.6 | A | 6 |" in rep, rep
case_file = next((t / "org/cases").glob(meta["S-0001-social"]["case"] + "-*.md")).read_text()
assert "post-mortem grade A" in case_file
chk = subprocess.run([sys.executable, str(t / "agents/bin/case.py"), "check"], capture_output=True, text=True, cwd=t)
assert chk.returncode == 0, chk.stdout
(t / "review.md").write_text("Continue social; stop ideas' approach; propose amendment on video tooling.")
run("review", "--file", str(t / "review.md"))
assert json.loads((sp / "sprint.json").read_text())["phase"] == "closed"
run("open", "--theme", "Sprint 2")
print("sprint tests passed")
