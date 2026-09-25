#!/usr/bin/env python3
"""the Collective weekly Sprints (Charter Article 14).

Phases: proposing → deliberating → voting → steward → executing → postmortem → review → closed

  sprint.py open [--theme TEXT]          start sprint S-NNNN (phase: proposing)
  sprint.py check                        validate proposals in the open sprint
  sprint.py freeze                       lock final proposal versions (phase: voting)
  sprint.py tally                        count per-item ballots (phase: steward)
  sprint.py steward --approve [--veto ITEM ...] [--reason TEXT]
                                         Steward sign-off → plan.md, cases filed (phase: executing)
  sprint.py postmortem                   open the post-mortem (phase: postmortem)
  sprint.py grade                        aggregate sealed grades → report.md (phase: review)
  sprint.py review --file ACTIONS.md     record the human review; close the sprint
  sprint.py status                       phase, items, and next step

Files live in sprints/S-NNNN/. Every step is recorded in the event log.
"""
import argparse, datetime, hashlib, json, pathlib, re, statistics, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPRINTS = ROOT / "sprints"
def _roster():
    """Active agents from agents/roster.json (Article 3.6); falls back to the founding nine."""
    try:
        ags = [a for a in json.loads((ROOT / "agents/roster.json").read_text())["agents"] if a["status"] == "active"]
        return [a["key"] for a in ags if a["votes"]], [a["key"] for a in ags]
    except Exception:
        v = ["pm", "researcher", "ideas", "prototyper", "media", "social"]
        return v, v + ["scribe", "lawyer", "auditor"]
MEMBERS, PROPOSERS = _roster()   # voters; everyone who proposes (non-voting agents propose but never vote)
HEADINGS = ["Objective", "Work items", "Success criteria", "Justification", "Budget", "Risks", "Dependencies"]
DIMENSIONS = ["criteria", "quality", "mission", "charter", "cost"]
PHASES = ["proposing", "deliberating", "voting", "steward", "executing", "postmortem", "review", "closed"]

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def sha(t): return hashlib.sha256(t.encode()).hexdigest()

def event(etype, data):
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", "scribe",
                    "--type", etype, "--data", json.dumps(data)], capture_output=True)

def current():
    s = sorted(SPRINTS.glob("S-*/sprint.json"))
    if not s: sys.exit("no sprint yet: run `sprint.py open`")
    d = s[-1].parent; return d, json.loads(s[-1].read_text())

def save(d, meta): (d / "sprint.json").write_text(json.dumps(meta, indent=2))

def need(meta, *phases):
    if meta["phase"] not in phases:
        sys.exit(f"REFUSED: sprint {meta['id']} is in phase '{meta['phase']}', expected {' or '.join(phases)}")

def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m: cur = m.group(1).strip(); out[cur] = []; continue
        if cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def proposals(d):
    return {p.stem: p for p in sorted((d / "proposals").glob("*.md")) if p.stem in PROPOSERS}

def check_proposal(role, p):
    t = p.read_text(); s = sections(t); errs = []
    for h in HEADINGS:
        if not s.get(h): errs.append(f"{role}: missing '## {h}'")
    if s.get("Success criteria") and not re.search(r"^\s*[-*] ", s["Success criteria"], re.M):
        errs.append(f"{role}: success criteria must be a bulleted list of measurable outcomes")
    j = s.get("Justification", "")
    if not re.search(r"(Article \d+|Mission|MISSION)", j): errs.append(f"{role}: justification must cite the Charter (Article N) or the Mission")
    if not re.search(r"C-\d{4}", j): errs.append(f"{role}: justification must cite at least one case (C-NNNN)")
    return errs

def ballots(d):
    """Ballot files: ballots/<voter>.md, lines 'ITEM | yes|no|abstain | FROZEN_SHA8 | reason'."""
    out = {}
    for p in sorted((d / "ballots").glob("*.md")):
        if p.stem not in MEMBERS: continue
        for line in p.read_text().splitlines():
            parts = [x.strip() for x in line.split("|")]
            if len(parts) >= 3 and parts[0].startswith("S-"):
                out.setdefault(parts[0], {})[p.stem] = {"vote": parts[1].lower(), "sha8": parts[2],
                                                         "reason": parts[3] if len(parts) > 3 else ""}
    return out

def file_case(meta, item, info, court, verdict, reason):
    draft = ROOT / "sprints" / meta["id"] / f".case-{item}.md"
    owner = info["owner"]
    draft.write_text(f"""---
title: Sprint {meta['id']} work item by {owner} {verdict}
court: {court}
labels: [sprint, {'governance' if court != 'assembly' else owner if owner in ('social','research','ideas','media') else 'operations'}]
headnote: {owner}'s sprint work item was {verdict} ({info['yes']} yes, {info['no']} no, {info['abstain']} abstain).
source: sprints/{meta['id']}/proposals/{owner}.md (sha256 {info['sha'][:16]}); sprints/{meta['id']}/deliberation/
---
## Question
Should {owner} carry out its proposed work in sprint {meta['id']}{' (theme: ' + meta['theme'] + ')' if meta.get('theme') else ''}?
## Facts
{owner} proposed the work in sprints/{meta['id']}/proposals/{owner}.md. It was deliberated in a fusion-harness session (positions, debate, sealed ballots); the full arguments are in sprints/{meta['id']}/deliberation/.
## Holding
The work item is {verdict}. {('It is binding for this sprint, and its success criteria are the standard it will be graded against in the post-mortem.') if verdict == 'approved' else 'It is not part of this sprint.'}
## Reasoning
{reason or 'See the ballots and deliberation record for each member’s reasons.'}
## Dissent
{'; '.join(f"{v}: {b['reason']}" for v, b in info['votes'].items() if b['vote'] == 'no' and b['reason']) or 'None recorded.'}
## Scope
Sprint {meta['id']} only. Later sprints may follow, distinguish, or build on it.
""")
    r = subprocess.run([sys.executable, str(ROOT / "agents/bin/case.py"), "new", "--draft", str(draft)], capture_output=True, text=True)
    draft.unlink(missing_ok=True)
    m = re.search(r"filed (C-\d{4})", r.stdout)
    return m.group(1) if m else f"ERROR: {r.stdout.strip()}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["open", "check", "freeze", "tally", "steward", "postmortem", "grade", "review", "status"])
    ap.add_argument("--theme", default=""); ap.add_argument("--approve", action="store_true")
    ap.add_argument("--veto", nargs="*", default=[]); ap.add_argument("--reason", default="")
    ap.add_argument("--file")
    a = ap.parse_args(); SPRINTS.mkdir(exist_ok=True)

    if a.cmd == "open":
        prev = sorted(SPRINTS.glob("S-*/sprint.json"))
        if prev and json.loads(prev[-1].read_text())["phase"] != "closed":
            sys.exit("REFUSED: the previous sprint isn't closed yet")
        sid = f"S-{len(prev) + 1:04d}"; d = SPRINTS / sid
        for sub in ["proposals", "deliberation", "ballots", "postmortem/self", "postmortem/grades"]:
            (d / sub).mkdir(parents=True, exist_ok=True)
        meta = {"id": sid, "theme": a.theme, "opened": now(), "phase": "proposing", "frozen": {}, "items": {}}
        save(d, meta); event("sprint.opened", {"summary": f"{sid} opened", "theme": a.theme})
        print(f"opened {sid}: each member writes sprints/{sid}/proposals/<role>.md"); return

    d, meta = current()
    if a.cmd == "status":
        print(f"{meta['id']} · phase {meta['phase']} · theme: {meta.get('theme') or '-'}")
        for r in PROPOSERS:
            has = (d / "proposals" / f"{r}.md").exists(); it = meta["items"].get(f"{meta['id']}-{r}", {})
            print(f"  {r:<11} proposal: {'yes' if has else 'no '}  outcome: {it.get('outcome', '-')}  grade: {it.get('grade', '-')}")
        return
    if a.cmd == "check":
        errs = [e for r, p in proposals(d).items() for e in check_proposal(r, p)]
        missing = [r for r in MEMBERS if r not in proposals(d)]
        print("\n".join(errs) if errs else "proposals valid"); print(f"missing proposals: {missing or 'none'}")
        sys.exit(1 if errs else 0)
    if a.cmd == "freeze":
        need(meta, "proposing", "deliberating")
        errs = [e for r, p in proposals(d).items() for e in check_proposal(r, p)]
        if errs: sys.exit("REFUSED: fix proposals first:\n  " + "\n  ".join(errs))
        meta["frozen"] = {f"{meta['id']}-{r}": sha(p.read_text()) for r, p in proposals(d).items()}
        meta["phase"] = "voting"; save(d, meta)
        event("sprint.frozen", {"summary": f"{meta['id']} proposals frozen", "items": list(meta["frozen"])})
        for item, h in meta["frozen"].items(): print(f"{item} | frozen {h[:8]}")
        return
    if a.cmd == "tally":
        need(meta, "voting")
        b = ballots(d)
        for item, h in meta["frozen"].items():
            owner = item.split("-", 2)[2]
            eligible = [m for m in MEMBERS if m != owner]
            votes = {v: x for v, x in b.get(item, {}).items() if v in eligible and x["sha8"] == h[:8]
                     and x["vote"] in ("yes", "no", "abstain")}
            yes = sum(x["vote"] == "yes" for x in votes.values()); no = sum(x["vote"] == "no" for x in votes.values())
            quorum = len(votes) * 3 >= len(eligible) * 2
            outcome = "approved" if quorum and yes > no else ("failed_quorum" if not quorum else "rejected")
            meta["items"][item] = {"owner": owner, "sha": h, "yes": yes, "no": no, "abstain": len(votes) - yes - no,
                                   "quorum": quorum, "outcome": outcome, "votes": votes}
            print(f"{item}: {outcome} ({yes} yes / {no} no / {len(votes) - yes - no} abstain; quorum {'met' if quorum else 'NOT met'})")
        meta["phase"] = "steward"; save(d, meta)
        (d / "tally.json").write_text(json.dumps(meta["items"], indent=2))
        event("sprint.tallied", {"summary": f"{meta['id']} tallied", "outcomes": {k: v["outcome"] for k, v in meta["items"].items()}})
        return
    if a.cmd == "steward":
        need(meta, "steward")
        if not a.approve: sys.exit("REFUSED: pass --approve (optionally with --veto ITEM ...)")
        plan = [f"# Sprint {meta['id']} plan", "", f"Theme: {meta.get('theme') or '-'}", f"Approved by the Steward {now()}", ""]
        for item, info in meta["items"].items():
            if item in a.veto and info["outcome"] == "approved":
                info["outcome"] = "vetoed"
            court = "steward" if info["outcome"] == "vetoed" else "assembly"
            info["case"] = file_case(meta, item, info, court, info["outcome"], a.reason if info["outcome"] == "vetoed" else "")
            if info["outcome"] == "approved":
                s = sections((d / "proposals" / f"{info['owner']}.md").read_text())
                plan += [f"## {item} · {info['owner']} · {info['case']}", "", "**Objective**", s["Objective"], "",
                         "**Success criteria**", s["Success criteria"], ""]
        plan += ["## Not in this sprint", ""] + [f"- {i}: {x['outcome']} ({x['case']})" for i, x in meta["items"].items() if x["outcome"] != "approved"]
        (d / "plan.md").write_text("\n".join(plan) + "\n")
        (d / "steward.md").write_text(f"Approved {now()}. Vetoed: {a.veto or 'none'}. Reason: {a.reason or '-'}\n")
        meta["phase"] = "executing"; save(d, meta)
        event("sprint.approved", {"summary": f"{meta['id']} plan approved", "vetoed": a.veto})
        print(f"plan written: sprints/{meta['id']}/plan.md"); [print(f"  {i}: {x['outcome']} → {x['case']}") for i, x in meta["items"].items()]
        return
    if a.cmd == "postmortem":
        need(meta, "executing"); meta["phase"] = "postmortem"; save(d, meta)
        event("sprint.postmortem", {"summary": f"{meta['id']} post-mortem opened"})
        print("owners write postmortem/self/<role>.md; graders write postmortem/grades/<role>.md"); return
    if a.cmd == "grade":
        need(meta, "postmortem")
        rows = ["# Post-mortem report · " + meta["id"], "", "Scores 0–4 per dimension: " + ", ".join(DIMENSIONS) + ". Median of sealed grades; owners don't grade their own work.", "",
                "| Item | Owner | " + " | ".join(DIMENSIONS) + " | Overall | Grade | Graders |", "|---" * (len(DIMENSIONS) + 5) + "|"]
        grades = {}
        for p in sorted((d / "postmortem/grades").glob("*.md")):
            if p.stem not in MEMBERS: continue
            for line in p.read_text().splitlines():
                parts = [x.strip() for x in line.split("|")]
                if len(parts) >= 6 and parts[0].startswith("S-"):
                    try: grades.setdefault(parts[0], {})[p.stem] = [max(0, min(4, int(x))) for x in parts[1:6]]
                    except ValueError: pass
        for item, info in meta["items"].items():
            if info["outcome"] != "approved": continue
            g = {k: v for k, v in grades.get(item, {}).items() if k != info["owner"]}
            if not g:
                rows.append(f"| {item} | {info['owner']} | " + " | ".join("-" for _ in DIMENSIONS) + " | - | ungraded | 0 |"); continue
            med = [statistics.median(v[i] for v in g.values()) for i in range(len(DIMENSIONS))]
            overall = round(sum(med) / len(med), 2)
            letter = "A" if overall >= 3.5 else "B" if overall >= 2.5 else "C" if overall >= 1.5 else "D" if overall >= 0.5 else "F"
            info["grade"] = f"{letter} ({overall})"
            rows.append(f"| {item} | {info['owner']} | " + " | ".join(f"{m:g}" for m in med) + f" | {overall} | {letter} | {len(g)} |")
            cp = next(iter((ROOT / "org/cases").glob(f"{info['case']}-*.md")), None)
            if cp: cp.write_text(cp.read_text().rstrip() + f"\n- {now()[:10]}: post-mortem grade {letter} ({overall}) in sprints/{meta['id']}/postmortem/report.md.\n")
        rows += ["", "## Suggested follow-on actions (for human review)", "",
                 "- Items graded C or below: decide continue / change / stop.",
                 "- Items graded A: consider making their approach a precedent for future sprints.",
                 "- Any policy or structure changes: propose as amendments."]
        (d / "postmortem/report.md").write_text("\n".join(rows) + "\n")
        subprocess.run([sys.executable, str(ROOT / "agents/bin/case.py"), "index"], capture_output=True)
        meta["phase"] = "review"; save(d, meta)
        event("sprint.graded", {"summary": f"{meta['id']} graded", "grades": {k: v.get("grade") for k, v in meta["items"].items()}})
        print(f"report: sprints/{meta['id']}/postmortem/report.md"); return
    if a.cmd == "review":
        need(meta, "review")
        if not a.file: sys.exit("REFUSED: pass --file with the human review and follow-on actions")
        (d / "postmortem/human-review.md").write_text(pathlib.Path(a.file).read_text())
        meta["phase"] = "closed"; meta["closed"] = now(); save(d, meta)
        event("sprint.closed", {"summary": f"{meta['id']} closed after human review"})
        print(f"{meta['id']} closed. Open the next sprint with `sprint.py open`."); return

if __name__ == "__main__":
    import pathlib, sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "observability")); from ops import run_cli   # Weave ops, best effort (P-005)
    run_cli(main, 'sprint', rename={'tally': 'sprint.count_votes', 'steward': 'sprint.steward_signoff', 'grade': 'sprint.postmortem_grade'})
