#!/usr/bin/env python3
"""the Collective case law (Charter Article 13).

Decisions become numbered, labeled cases in org/cases/. Later decisions cite
them. A citator derives each case's status from how later cases treat it.

  case.py new --draft DRAFT.md      file a case from a draft (assigns the number); courts: officer < assembly < steward
  case.py check                     validate every case and citation (exit 1 on error)
  case.py index                     rebuild org/cases/INDEX.md and CITATOR.md
  case.py search QUERY [--label L] [--status S] [--court C]
  case.py show C-0003               a case's headnote, holding, status, and citing cases
  case.py review [--within DAYS]    cases due for periodic review
  case.py stats                     precedent statistics, incl. survival rate

Case file = front matter + sections. Front matter keys:
  id, title, date, court (steward|assembly|officer), labels [..], headnote,
  source, cites (list of {case: C-NNNN, treatment: follows|distinguishes|limits|overrules}),
  review_by, holding_sha256
Sections (in order): Question, Facts, Holding, Reasoning, Dissent, Scope, History.
Everything above "## History" is frozen once filed; History is append-only.
"""
import argparse, datetime, hashlib, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CASES = ROOT / "org" / "cases"
COURT_RANK = {"officer": 1, "chief": 1, "assembly": 2, "steward": 3}   # "chief" = pre-v6.1 name for officer
TREATMENTS = {"follows", "distinguishes", "limits", "overrules"}
LABELS = {"governance", "policy", "safety", "social", "research", "ideas", "prototyping",
          "media", "budget", "operations", "tooling", "honesty", "transparency", "replay", "library", "sprint"}
SECTIONS = ["Question", "Facts", "Holding", "Reasoning", "Dissent", "Scope", "History"]
ID_RE = re.compile(r"^C-\d{4}$")

def extra_labels():
    f = CASES / "labels.txt"
    return {l.strip() for l in f.read_text().splitlines() if l.strip() and not l.startswith("#")} if f.exists() else set()

# ---------- minimal front-matter parser (restricted YAML subset) ----------
def parse(text):
    if not text.startswith("---\n"): raise ValueError("missing front matter")
    fm_raw, body = text[4:].split("\n---\n", 1)
    fm, cur_list = {}, None
    for line in fm_raw.splitlines():
        if not line.strip(): continue
        if line.startswith("  - ") and cur_list is not None:
            item = line[4:].strip()
            if item.startswith("{"):
                d = {}
                for kv in item.strip("{}").split(","):
                    k, v = kv.split(":", 1); d[k.strip()] = v.strip()
                fm[cur_list].append(d)
            else:
                fm[cur_list].append(item)
            continue
        k, v = line.split(":", 1); k, v = k.strip(), v.strip()
        if v == "":
            fm[k] = []; cur_list = k
        elif v.startswith("[") and v.endswith("]"):
            fm[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]; cur_list = None
        else:
            fm[k] = v; cur_list = None
    secs, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^## (\w+)\s*$", line)
        if m: cur = m.group(1); secs[cur] = []; continue
        if cur: secs[cur].append(line)
    secs = {k: "\n".join(v).strip() for k, v in secs.items()}
    return fm, secs, body

def dump(fm, secs):
    lines = ["---"]
    for k in ["id", "title", "date", "court", "labels", "headnote", "source", "cites", "review_by", "holding_sha256"]:
        v = fm.get(k)
        if k == "labels": lines.append(f"labels: [{', '.join(v or [])}]")
        elif k == "cites":
            lines.append("cites:")
            for c in v or []: lines.append(f"  - {{case: {c['case']}, treatment: {c['treatment']}}}")
        elif v is not None: lines.append(f"{k}: {v}")
    lines.append("---")
    for s in SECTIONS:
        lines += ["", f"## {s}", "", secs.get(s, "").strip() or ("None." if s != "History" else "")]
    return "\n".join(lines).rstrip() + "\n"

def frozen_part(body):
    return body.split("\n## History", 1)[0].strip()

def load_all():
    out = {}
    for p in sorted(CASES.glob("C-*.md")):
        fm, secs, body = parse(p.read_text())
        out[fm["id"]] = {"path": p, "fm": fm, "secs": secs, "body": body}
    return out

# ---------- status derivation (the citator) ----------
def citator(cases):
    status = {cid: "good_law" for cid in cases}
    cited_by = {cid: [] for cid in cases}
    for cid in sorted(cases):
        for c in cases[cid]["fm"].get("cites", []):
            if c["case"] in cited_by:
                cited_by[c["case"]].append((cid, c["treatment"]))
                if c["treatment"] == "overrules": status[c["case"]] = "overruled"
                elif c["treatment"] == "limits" and status[c["case"]] == "good_law": status[c["case"]] = "limited"
    return status, cited_by

def check(cases):
    errs, ids = [], sorted(cases)
    labels = LABELS | extra_labels()
    for i, cid in enumerate(ids, 1):
        c = cases[cid]; fm, secs = c["fm"], c["secs"]
        if not ID_RE.match(cid) or int(cid[2:]) != i: errs.append(f"{cid}: numbering must be sequential from C-0001 (expected C-{i:04d})")
        if not c["path"].name.startswith(cid + "-"): errs.append(f"{cid}: file name must start with its id")
        for k in ["title", "date", "court", "headnote", "source", "review_by", "holding_sha256"]:
            if not fm.get(k): errs.append(f"{cid}: missing {k}")
        if fm.get("court") not in COURT_RANK: errs.append(f"{cid}: court must be steward|assembly|officer")
        bad = [l for l in fm.get("labels", []) if l not in labels]
        if not fm.get("labels"): errs.append(f"{cid}: at least one label required")
        if bad: errs.append(f"{cid}: unknown labels {bad} (add to org/cases/labels.txt by Class C amendment)")
        for s in SECTIONS[:-1]:
            if not secs.get(s): errs.append(f"{cid}: missing section {s}")
        if hashlib.sha256(frozen_part(c["body"]).encode()).hexdigest() != fm.get("holding_sha256"):
            errs.append(f"{cid}: frozen text changed after filing (only ## History may be appended)")
        for cit in fm.get("cites", []):
            t, tgt = cit.get("treatment"), cit.get("case")
            if t not in TREATMENTS: errs.append(f"{cid}: bad treatment '{t}'")
            if tgt not in cases: errs.append(f"{cid}: cites unknown case {tgt}"); continue
            if tgt >= cid: errs.append(f"{cid}: can only cite earlier cases ({tgt})")
            if t in ("overrules", "limits") and COURT_RANK.get(fm.get("court"), 0) < COURT_RANK.get(cases[tgt]["fm"].get("court"), 9):
                errs.append(f"{cid}: a {fm.get('court')} case cannot {t[:-1]} a {cases[tgt]['fm'].get('court')} case ({tgt})")
    return errs

def record_event(etype, data):
    try:
        subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", "scribe",
                        "--type", etype, "--data", json.dumps(data)], check=False, capture_output=True)
    except Exception:
        pass

def cmd_new(draft):
    fm, secs, _ = parse(pathlib.Path(draft).read_text())
    cases = load_all()
    cid = f"C-{len(cases) + 1:04d}"
    fm["id"] = cid
    fm.setdefault("date", datetime.date.today().isoformat())
    fm.setdefault("review_by", (datetime.date.today() + datetime.timedelta(days=90)).isoformat())
    fm.setdefault("cites", []); fm["holding_sha256"] = "pending"
    slug = re.sub(r"[^a-z0-9]+", "-", fm.get("title", "case").lower()).strip("-")[:50]
    secs.setdefault("History", ""); secs["History"] = (secs["History"] + f"\n- {fm['date']}: filed.").strip()
    text = dump(fm, secs)
    _, _, body = parse(text)
    fm["holding_sha256"] = hashlib.sha256(frozen_part(body).encode()).hexdigest()
    path = CASES / f"{cid}-{slug}.md"; path.write_text(dump(fm, secs))
    cases = load_all(); errs = [e for e in check(cases) if e.startswith(cid)]
    if errs:
        path.unlink(); print("REFUSED:\n  " + "\n  ".join(errs)); sys.exit(1)
    for cit in fm["cites"]:  # note the treatment in the cited case's History (append-only)
        tp = cases[cit["case"]]["path"]
        tp.write_text(tp.read_text().rstrip() + f"\n- {fm['date']}: {cit['treatment']} by {cid}.\n")
    cmd_index(); record_event("case.filed", {"summary": f"{cid} {fm['title']}", "case": cid, "court": fm["court"]})
    print(f"filed {cid}: {path.relative_to(ROOT)}")

def cmd_index():
    cases = load_all(); status, cited_by = citator(cases)
    idx = ["# Case law index", "", "Generated by `agents/bin/case.py index`. Don't edit.", "",
           "| Case | Title | Court | Labels | Date | Status | Headnote |", "|---|---|---|---|---|---|---|"]
    for cid in sorted(cases):
        fm = cases[cid]["fm"]
        idx.append(f"| [{cid}]({cases[cid]['path'].name}) | {fm['title']} | {fm['court']} | {', '.join(fm.get('labels', []))} | {fm['date']} | {status[cid]} | {fm['headnote']} |")
    (CASES / "INDEX.md").write_text("\n".join(idx) + "\n")
    cit = ["# Citator", "", "How later cases treat each case. Status is derived from these treatments.", ""]
    for cid in sorted(cases):
        refs = ", ".join(f"{c} ({t})" for c, t in cited_by[cid]) or "not yet cited"
        cit.append(f"- **{cid}** · {status[cid]} · cited by: {refs}")
    (CASES / "CITATOR.md").write_text("\n".join(cit) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["new", "check", "index", "search", "show", "review", "stats"])
    ap.add_argument("arg", nargs="?"); ap.add_argument("--draft"); ap.add_argument("--label")
    ap.add_argument("--status"); ap.add_argument("--court"); ap.add_argument("--within", type=int, default=14)
    a = ap.parse_args(); CASES.mkdir(parents=True, exist_ok=True)
    if a.cmd == "new": return cmd_new(a.draft or a.arg)
    cases = load_all()
    if a.cmd == "check":
        errs = check(cases); print("\n".join(errs) if errs else f"ok: {len(cases)} cases valid"); sys.exit(1 if errs else 0)
    if a.cmd == "index": cmd_index(); print("index rebuilt"); return
    status, cited_by = citator(cases)
    if a.cmd == "search":
        q = (a.arg or "").lower()
        for cid in sorted(cases):
            c = cases[cid]; fm = c["fm"]; blob = (fm["title"] + fm["headnote"] + c["secs"].get("Holding", "")).lower()
            if q and q not in blob: continue
            if a.label and a.label not in fm.get("labels", []): continue
            if a.status and status[cid] != a.status: continue
            if a.court and fm["court"] != a.court: continue
            print(f"{cid} [{status[cid]}] ({fm['court']}; {', '.join(fm.get('labels', []))}) {fm['title']}: {fm['headnote']}")
    elif a.cmd == "show":
        c = cases[a.arg]; fm = c["fm"]
        print(f"{a.arg} · {fm['title']} · {fm['court']} · {fm['date']} · {status[a.arg]}\n\nHeadnote: {fm['headnote']}\n\nHolding:\n{c['secs']['Holding']}\n")
        print("Cited by: " + (", ".join(f"{x} ({t})" for x, t in cited_by[a.arg]) or "none"))
    elif a.cmd == "review":
        limit = (datetime.date.today() + datetime.timedelta(days=a.within)).isoformat()
        for cid in sorted(cases):
            if status[cid] != "overruled" and cases[cid]["fm"]["review_by"] <= limit:
                print(f"{cid} review by {cases[cid]['fm']['review_by']}: {cases[cid]['fm']['title']}")
    elif a.cmd == "stats":
        challenged = [cid for cid in cases if any(t in ("distinguishes", "limits", "overrules") for _, t in cited_by[cid])]
        survived = [cid for cid in challenged if status[cid] != "overruled"]
        n = len(cases); counts = {s: list(status.values()).count(s) for s in ("good_law", "limited", "overruled")}
        rate = f"{100 * len(survived) / len(challenged):.0f}%" if challenged else "n/a (no challenges yet)"
        print(f"cases {n} · good law {counts['good_law']} · limited {counts['limited']} · overruled {counts['overruled']}")
        print(f"precedent survival rate: {rate} ({len(survived)}/{len(challenged)} challenged cases still stand)")

if __name__ == "__main__":
    main()
