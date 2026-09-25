#!/usr/bin/env python3
"""Compile the week's facts for the Collective's blog (Charter Article 19).

  weekly-digest.py [--end YYYY-MM-DD] [--days 7]
      → blog/_facts/<end-date>.md: everything the Collective did that week, each line
        with its source (event #, case, commit, file). Media writes the human-readable
        post from it; the post must cover every section.

Private material is never included: edicts, drafts, incidents, and transcripts
appear only as counts.
"""
import argparse, datetime, glob, json, pathlib, re, subprocess, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVENTS = ROOT / "private" / "ledger" / "events.ndjson"

def in_range(ts, start, end): return start <= ts[:10] <= end

def events(start, end):
    if not EVENTS.exists(): return []
    out = []
    for line in EVENTS.read_text().splitlines():
        e = json.loads(line)
        if in_range(e["ts"], start, end): out.append(e)
    return out

def fm(path):
    t = pathlib.Path(path).read_text()
    if not t.startswith("---\n"): return {}
    d = {}
    for line in t[4:].split("\n---\n", 1)[0].splitlines():
        if ":" in line: k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--end", default=datetime.datetime.now(datetime.timezone.utc).date().isoformat()); ap.add_argument("--days", type=int, default=7)   # --end in UTC, like every event timestamp
    a = ap.parse_args()
    end = a.end; start = (datetime.date.fromisoformat(end) - datetime.timedelta(days=a.days - 1)).isoformat()
    ev = events(start, end); L = []
    add = L.append
    add(f"# Week in facts: {start} → {end}"); add("")
    add("Compiled by `agents/bin/weekly-digest.py` from versioned records. Every line cites its source. Private material appears only as counts."); add("")

    # Sprints
    add("## Sprints")
    found = False
    for sj in sorted(glob.glob(str(ROOT / "sprints/S-*/sprint.json"))):
        m = json.loads(pathlib.Path(sj).read_text()); sid = m["id"]
        touched = m.get("opened", "")[:10] >= start or any(e["data"].get("summary", "").startswith(sid) for e in ev if e["type"].startswith("sprint."))
        if not touched: continue
        found = True
        add(f"- **{sid}** · theme: {m.get('theme') or '-'} · phase: {m['phase']} (sprints/{sid}/sprint.json)")
        for item, i in m.get("items", {}).items():
            add(f"  - {item} ({i['owner']}): {i['outcome']}" + (f", grade {i['grade']}" if i.get("grade") else "") + (f" · {i['case']}" if i.get("case") else ""))
    if not found: add("- No sprint activity this week.")
    add("")

    # Votes (P8): every sprint ballot and governance tally this week
    add("## Votes")
    nv = 0
    for sj in sorted(glob.glob(str(ROOT / "sprints/S-*/sprint.json"))):
        m = json.loads(pathlib.Path(sj).read_text())
        if not any(e["type"] == "sprint.tallied" and e["data"].get("summary", "").startswith(m["id"]) for e in ev): continue
        for item, i in m.get("items", {}).items():
            add(f"- {item}: {i['yes']} yes / {i['no']} no / {i['abstain']} abstain → {i['outcome']} (sprints/{m['id']}/tally.json)"); nv += 1
    for tj in sorted(glob.glob(str(ROOT / "governance/records/*/tally.json"))):
        t = json.loads(pathlib.Path(tj).read_text())
        if any(e["type"] == "governance" and e["data"].get("amendment") == t["id"] for e in ev):
            add(f"- {t['id']} (Class {t['class']}): {t['yes']} yes / {t['no']} no / {t['abstain']} abstain → {t['outcome']} ({pathlib.Path(tj).relative_to(ROOT)})"); nv += 1
    if not nv: add("- No votes this week.")
    add("")

    # Discussion (P8): every board thread started this week
    add("## Discussion")
    threads = sorted(p for p in glob.glob(str(ROOT / "org/board/*.md")) if start <= pathlib.Path(p).name[:10] <= end)
    for p in threads:
        first = pathlib.Path(p).read_text().splitlines()[0] if pathlib.Path(p).read_text() else ""
        posts = pathlib.Path(p).read_text().count("\n### ")
        add(f"- {pathlib.Path(p).name} · {first} · {posts + 1} posts (org/board/)")
    if not threads: add("- No new board threads this week.")
    add("")

    # Changes (P8): every file changed this week, by area
    add("## Changes")
    ch_ev = [e for e in ev if e["type"] in ("file.put", "file.delete") and e["data"].get("reason") != "genesis snapshot"]
    areas = collections.Counter(e["data"]["path"].split("/")[0] for e in ch_ev)
    add(f"- {len(ch_ev)} file changes across {len(areas)} areas: " + (", ".join(f"{a} {n}" for a, n in areas.most_common()) or "none") + " (event log)")
    add("")

    # Agent activity
    add("## Agent activity")
    runs = collections.Counter(e["actor"] for e in ev if e["type"] == "run.start")
    files = collections.Counter(e["actor"] for e in ev if e["type"] in ("file.put", "file.delete") and e["actor"] not in ("system", "steward", "external"))
    if runs:
        for role in sorted(runs):
            add(f"- **{role}**: {runs[role]} runs, {files.get(role, 0)} file changes (event log)")
    else: add("- No recorded agent runs this week.")
    add("")

    # Decisions
    add("## Decisions (case law)")
    cs = [(p, fm(p)) for p in sorted(glob.glob(str(ROOT / "org/cases/C-*.md")))]
    wk = [(p, f) for p, f in cs if start <= f.get("date", "") <= end]
    for p, f in wk: add(f"- {f['id']} ({f['court']}): {f['title']}. {f['headnote']} ({pathlib.Path(p).relative_to(ROOT)})")
    if not wk: add("- No new cases this week.")
    add("")

    # Amendments
    add("## Charter amendments")
    ch = (ROOT / "CHARTER.md").read_text()
    am = re.findall(r"### (A-\d{4}) · v([\d.]+) · ([\d-]+) · Class (\w) · (.+)", ch)
    wa = [x for x in am if start <= x[2] <= end]
    for aid, v, d, c, t in wa: add(f"- {aid} → v{v} (Class {c}): {t} (CHARTER.md Part VI)")
    if not wa: add("- No amendments this week.")
    add("")

    # Work products
    add("## Research, prototypes, media")
    def puts(prefix):   # real work only: no genesis snapshot, no placeholder files
        return sorted({e["data"]["path"] for e in ev if e["type"] == "file.put"
                       and e["data"].get("path", "").startswith(prefix)
                       and e["data"].get("reason") != "genesis snapshot"
                       and not e["data"]["path"].endswith(".gitkeep")})
    for label, prefix in [("Research briefs", "research/briefs/"), ("Proposals", "ideas/"), ("Prototypes", "prototypes/"), ("Media exports", "media/exports/")]:
        items = puts(prefix)
        add(f"- {label}: {len(items)}" + ("" if not items else " (" + ", ".join(items[:8]) + (" …" if len(items) > 8 else "") + ")"))
    posted = [e for e in ev if e["type"] == "effect.posted"]
    add(f"- Posts published on X: {len(posted)}" + ("" if not posted else " (" + ", ".join(p["data"].get("url", "") for p in posted[:8]) + ")"))
    add("")

    # Governance & oversight (counts only for private things)
    add("## Governance and oversight")
    add(f"- Steward approvals: {sum(e['type'] == 'approval.granted' for e in ev)}, rejections: {sum(e['type'] == 'approval.rejected' for e in ev)} (event log)")
    add(f"- Steward edicts issued: {sum(e['type'] == 'edict.issued' for e in ev)} (count only; edicts are private)")
    add(f"- Incidents: {sum(e['type'] == 'incident' for e in ev)} (count only; details are private)")
    add(f"- Governance publications: {sum(e['type'] == 'governance' for e in ev)}")
    add("")

    # Learnings
    add("## What we learned")
    lt = (ROOT / "org/LEARNINGS.md").read_text() if (ROOT / "org/LEARNINGS.md").exists() else ""
    ls = [(d, t) for d, t in re.findall(r"^## (\d{4}-\d{2}-\d{2}) · [^·]+ · (.+)$", lt, re.M) if start <= d <= end]
    for d, t in ls: add(f"- {d}: {t} (org/LEARNINGS.md)")
    if not ls: add("- No new learnings recorded this week.")
    add("")

    # Metrics
    add("## Metrics")
    snaps = sorted(glob.glob(str(ROOT / "metrics/*.json")))
    snaps = [s for s in snaps if pathlib.Path(s).stem <= end]
    if snaps:
        m = json.loads(pathlib.Path(snaps[-1]).read_text())
        for k, v in m.items(): add(f"- {k}: {v}")
        add(f"(metrics/{pathlib.Path(snaps[-1]).name})")
    else: add("- No metrics snapshot yet.")
    add("")
    add(f"Event log: {len(ev)} events this week" + (f" (#{ev[0]['seq']}–#{ev[-1]['seq']})" if ev else "") + ".")

    out = ROOT / "blog" / "_facts" / f"{end}.md"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n"); print(f"facts: {out.relative_to(ROOT)} ({len(ev)} events)")

if __name__ == "__main__":
    main()
