#!/usr/bin/env python3
"""The Collective's amendments folder (Charter Article 7.12).

Every amendment is a file, amendments/amendment-NNN.md, attached to the Charter.
It starts as a proposal, is deliberated and voted on, and is either ratified
(and applied to CHARTER.md) or rejected. Numbers match the Charter's amendment
log: amendment-013.md is A-0013. Rejected and withdrawn proposals keep their
number, so the sequence has no gaps and nothing disappears.

  amendment.py new --title T --class A|B|C|M --proposer ROLE --file TEXT.md
                                   propose (status: proposed); the text says exactly what changes
  amendment.py status NNN STATUS [--note TEXT]
                                   proposed → deliberating → voting → passed | rejected | withdrawn
  amendment.py sync                write a ratified file for every Charter log entry lacking one
  amendment.py list                every amendment, its class, status, and Charter version
  amendment.py check               numbering, frozen text, and agreement with the Charter log
"""
import argparse, datetime, hashlib, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIR = ROOT / "amendments"
FLOW = {"proposed": {"deliberating", "withdrawn"}, "deliberating": {"voting", "withdrawn"},
        "voting": {"passed", "rejected"}, "passed": {"ratified", "vetoed"},
        "ratified": set(), "rejected": set(), "withdrawn": set(), "vetoed": set()}
ENTRY = re.compile(r"### (A-(\d{4})) · v([\d.]+) · ([\d-]+) · Class (\w) · ([^\n]+)\n(.*?)(?=\n### A-|\Z)", re.S)

def sha(t): return hashlib.sha256(t.encode()).hexdigest()
def today(): return datetime.date.today().isoformat()
def path(n): return DIR / f"amendment-{int(n):03d}.md"

def log_entries():
    text = (ROOT / "CHARTER.md").read_text()
    log = text[[m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", text)][-1]:]
    out = {}
    for m in ENTRY.finditer(log):
        body = dict(re.findall(r"^(\w+): (.*)$", m.group(7), re.M))
        out[int(m.group(2))] = {"id": m.group(1), "version": m.group(3), "date": m.group(4),
                                "class": m.group(5), "title": m.group(6).strip(), **body}
    return out

def parse(p):
    t = p.read_text(); fm_raw, body = t[4:].split("\n---\n", 1)
    fm = dict(l.split(": ", 1) for l in fm_raw.splitlines() if ": " in l)
    return fm, body

def text_block(body):
    m = re.search(r"## Proposed text\n\n(.*?)\n## ", body, re.S)
    return m.group(1).strip() if m else ""

def write(n, fm, sections):
    head = ["---"] + [f"{k}: {v}" for k, v in fm.items()] + ["---", ""]
    body = [f"# Amendment {int(n):03d} · {fm['title']}", ""]
    for k in ["Proposed text", "Reason", "Discussion", "Vote", "Outcome", "History"]:
        body += [f"## {k}", "", sections.get(k, "").strip() or "—", ""]
    path(n).write_text("\n".join(head + body))

def event(etype, data):
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", "scribe",
                    "--type", etype, "--data", json.dumps(data)], capture_output=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["new", "status", "sync", "list", "check"])
    ap.add_argument("args", nargs="*"); ap.add_argument("--title"); ap.add_argument("--class", dest="cls")
    ap.add_argument("--proposer"); ap.add_argument("--file"); ap.add_argument("--note", default="")
    a = ap.parse_args(); DIR.mkdir(exist_ok=True)
    log = log_entries()
    files = {int(p.stem.split("-")[1]): p for p in DIR.glob("amendment-*.md")}

    if a.cmd == "new":
        if not (a.title and a.cls and a.proposer and a.file): sys.exit("REFUSED: --title, --class, --proposer, and --file are required")
        if a.cls.upper() not in ("A", "B", "C", "M"): sys.exit("REFUSED: class must be A, B, C, or M")
        n = max(list(files) + list(log) + [-1]) + 1
        txt = pathlib.Path(a.file).read_text().strip()
        fm = {"id": f"A-{n:04d}", "title": a.title, "class": a.cls.upper(), "status": "proposed",
              "proposer": a.proposer, "proposed": today(), "text_sha256": sha(txt), "charter_version": "(pending)"}
        write(n, fm, {"Proposed text": txt, "Reason": "(the proposer states the reason and evidence here)",
                      "Discussion": f"Board thread: org/board/{today()}-amendment-{n:03d}.md\nLawyer's opinion: (pending)",
                      "History": f"- {today()}: proposed by {a.proposer}."})
        event("amendment.proposed", {"summary": f"amendment-{n:03d}: {a.title}", "amendment": fm["id"]})
        print(f"proposed {path(n).relative_to(ROOT)} (A-{n:04d}, Class {fm['class']})"); return

    if a.cmd == "status":
        n, new = int(a.args[0]), a.args[1]
        p = files.get(n) or sys.exit(f"no amendment-{n:03d}.md")
        fm, body = parse(p)
        if new not in FLOW.get(fm["status"], set()):
            sys.exit(f"REFUSED: {fm['status']} → {new} isn't allowed (allowed: {sorted(FLOW[fm['status']]) or 'none, it is final'})")
        if fm["status"] == "proposed" and new == "deliberating":
            fm["text_sha256"] = sha(text_block(body))            # freeze the text for the vote
        fm["status"] = new
        body = body.rstrip() + f"\n- {today()}: {new}." + (f" {a.note}" if a.note else "") + "\n"
        p.write_text("---\n" + "\n".join(f"{k}: {v}" for k, v in fm.items()) + "\n---\n" + body)
        event("amendment.status", {"summary": f"amendment-{n:03d} → {new}", "amendment": fm["id"]})
        print(f"amendment-{n:03d}: {new}"); return

    if a.cmd == "sync":
        made = 0
        for n, e in sorted(log.items()):
            if n in files:
                fm, body = parse(files[n])
                if fm.get("title", "").strip() != e["title"].strip():   # a number used twice: never mark someone else's motion ratified
                    print(f"sync: amendment-{n:03d}.md is '{fm.get('title')}' but the log's {e['id']} is '{e['title']}'; renumber the file's motion", file=sys.stderr)
                    continue
                if fm["status"] != "ratified":                     # proposal just applied to the Charter
                    fm.update(status="ratified", charter_version=f"v{e['version']}", log_entry_hash=e.get("entry_hash", ""))
                    body = body.rstrip() + f"\n- {e['date']}: ratified and applied to the Charter as v{e['version']}.\n"
                    files[n].write_text("---\n" + "\n".join(f"{k}: {v}" for k, v in fm.items()) + "\n---\n" + body)
                    made += 1
                continue
            fm = {"id": e["id"], "title": e["title"], "class": e["class"], "status": "ratified",
                  "proposer": e.get("proposed_by", ""), "proposed": e["date"], "charter_version": f"v{e['version']}",
                  "log_entry_hash": e.get("entry_hash", "")}
            vote = e.get("vote", "")
            write(n, fm, {
                "Proposed text": f"Recorded before amendment files existed; the full text is Charter v{e['version']} "
                                 f"(`charter/history/CHARTER-v{e['version']}.md`). Compare with the version before it:\n"
                                 f"`agents/bin/charter.py diff <previous> v{e['version']}`.",
                "Reason": e.get("change", ""),
                "Discussion": f"Board thread: {e.get('thread', '—')}",
                "Vote": vote + (f"\nRatified by: {e.get('ratified_by', '')}" if e.get("ratified_by") else ""),
                "Outcome": f"Ratified and applied to the Charter as v{e['version']} on {e['date']}.\n"
                           f"Amendment log entry hash: `{e.get('entry_hash', '')}` (verify: `agents/bin/charter-verify.py`).",
                "History": f"- {e['date']}: ratified (Charter v{e['version']}). File generated from the verified amendment log."})
            made += 1
        print(f"sync: {made} amendment files written or updated"); return

    if a.cmd == "list":
        for n in sorted(set(files) | set(log)):
            if n in files:
                fm, _ = parse(files[n]); print(f"amendment-{n:03d}  A-{n:04d}  Class {fm['class']}  {fm['status']:<12} {fm.get('charter_version', '')}  {fm['title']}")
            else:
                print(f"amendment-{n:03d}  A-{n:04d}  (in the Charter log, no file yet: run sync)")
        return

    if a.cmd == "check":
        errs = []
        top = max(list(files) + list(log) + [-1])
        for n in range(0, top + 1):
            if n not in files: errs.append(f"amendment-{n:03d}.md is missing (numbers never skip; run sync)")
        for n, p in sorted(files.items()):
            fm, body = parse(p)
            if fm.get("status") not in FLOW: errs.append(f"amendment-{n:03d}: unknown status {fm.get('status')}")
            if n in log:
                if fm.get("title", "").strip() != log[n]["title"].strip(): errs.append(f"amendment-{n:03d}: its title isn't the log's ('{log[n]['title']}'): a number used twice")
                if fm.get("status") != "ratified": errs.append(f"amendment-{n:03d}: in the Charter log but status is {fm.get('status')}")
                if fm.get("charter_version") != f"v{log[n]['version']}": errs.append(f"amendment-{n:03d}: Charter version disagrees with the log")
                if fm.get("log_entry_hash") and fm["log_entry_hash"] != log[n].get("entry_hash"): errs.append(f"amendment-{n:03d}: log hash disagrees with the Charter")
            elif fm.get("status") == "ratified":
                errs.append(f"amendment-{n:03d}: marked ratified but not in the Charter log")
            if fm.get("status") in ("voting", "passed", "rejected") and fm.get("text_sha256") != sha(text_block(body)):
                errs.append(f"amendment-{n:03d}: proposed text changed after it was frozen for the vote")
        print("\n".join(errs) if errs else f"ok: {len(files)} amendments consistent with the Charter log"); sys.exit(1 if errs else 0)

if __name__ == "__main__":
    import pathlib, sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "observability")); from ops import run_cli   # Weave ops, best effort (P-005)
    run_cli(main, 'amendment', only=('new', 'status', 'sync', 'check'), keep_flags=('--class',))
