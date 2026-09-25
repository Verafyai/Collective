#!/usr/bin/env python3
"""The Collective Dashboard, v1 (project P-001; Charter Articles 18 and 21).

A local window onto the whole Collective, computed live from its records:
the Charter, amendments, case law, projects, sprints, offices, edicts, the
event log, and verification. Python standard library only.

  python3 dashboard/server.py [--port 4848] [--public]

- Binds to 127.0.0.1 only.
- Read-only, except one thing (Article 18.7): a human comment or suggestion on
  a project, appended to its discussion.md through projects.py.
- --public hides everything from the private repo (edicts, event details).
"""
import argparse, calendar, glob, json, pathlib, re, subprocess, sys, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
PUBLIC = False
_verify_cache = {"t": 0, "data": None}

# ---------- helpers ----------
def read(p):
    try: return pathlib.Path(p).read_text()
    except Exception: return ""

def frontmatter(text):
    if not text.startswith("---\n") or "\n---\n" not in text[4:]: return {}, text
    raw, body = text[4:].split("\n---\n", 1)
    fm = {}
    for line in raw.splitlines():
        if ": " in line and not line.startswith("  "):
            k, v = line.split(": ", 1); fm[k.strip()] = v.strip()
    return fm, body

def sections(body):
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m: cur = m.group(1); out[cur] = []; continue
        if cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def git(*args, cwd=ROOT):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception: return ""

def run(*cmd, timeout=60):
    try:
        r = subprocess.run(list(cmd), capture_output=True, text=True, cwd=ROOT, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)

def event_count():
    """Number of recorded events (a count is public; the events themselves are not)."""
    try: return int(json.loads(read(ROOT / "private" / "ledger" / "HEAD.json") or "{}").get("seq", 0))
    except Exception: return 0

def events(after=0, limit=300):
    if PUBLIC: return []          # the event log is private (Charter 17.2): public mode never reads it
    p = ROOT / "private" / "ledger" / "events.ndjson"
    if not p.exists(): return []
    out = []
    for line in p.read_text().splitlines()[-5000:]:
        try: e = json.loads(line)
        except Exception: continue
        if e["seq"] > after: out.append(e)
    return out[-limit:]

def edict_state(fm, history):
    """An edict's real state. edict.py's `note` appends outcomes to History without changing the
    status field, so an 'issued' edict with an outcome note has in fact been acted on."""
    notes = [l for l in history.splitlines() if l.startswith("- ") and not re.search(r": (issued|superseded by)", l)
             and "reconstructed into this record" not in l]
    if fm.get("status") == "issued" and notes: return "implemented"
    return fm.get("status", "")

def roster():
    try: return json.loads(read(ROOT / "agents/roster.json"))["agents"]
    except Exception:
        return [{"key": k, "name": k, "class": "", "room": "", "votes": False, "status": "active"} for k in
                ["pm", "scribe", "lawyer", "auditor", "researcher", "ideas", "prototyper", "media", "social"]]

MODULES = [  # how raw tool grants read as "installed modules" in an agent's bio
    ("Reads files", r"^(Read|Glob|Grep)$"), ("Writes files", r"^(Write|Edit)$"), ("Writes to the board", r"^(Write|Edit)\(org/board"),
    ("Writes to its own folder", r"^(Write|Edit)\((research|ideas|media|private/outbox)"),
    ("Web search", r"^WebSearch$"), ("Web pages", r"^WebFetch$"), ("Git", r"^Bash\(git"), ("Code runtimes", r"^Bash\((node|npm|npx|python3|uv|make):"),
    ("Media tools", r"^Bash\((ffmpeg|ffprobe|agents/bin/tts)"), ("Case law", r"case\.py"), ("Sprints", r"sprint\.py"),
    ("Projects", r"projects\.py"), ("Amendments", r"amendment\.py"), ("Governance records", r"(gov-tally|gov-publish|charter)"),
    ("Edicts", r"edict\.py"), ("Integrity checks", r"(verify|seed-check|check:)"), ("Repositories and backups", r"(repos\.sh|ledger-backup)"),
    ("Tasks", r"^Bash\(tsk"), ("Metrics", r"metrics\.py"), ("Blog", r"(weekly-digest|blog-publish)"),
]
def split_tools(t):
    out, depth, cur = [], 0, ""
    for ch in (t or ""):
        if ch == "(": depth += 1
        if ch == ")": depth -= 1
        if ch == "," and depth == 0: out.append(cur.strip()); cur = ""
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out
def modules(tools):
    got = []
    for name, rx in MODULES:
        if any(re.search(rx, t) for t in split_tools(tools)) and name not in got: got.append(name)
    return got

def bio(key):
    code, out = run(PY, "agents/bin/spawn.py", "bio", key)
    if code != 0: return 404, {"error": out}
    b = json.loads(out); cls = json.loads(read(ROOT / "agents/classes.json") or "{}").get("classes", {}).get(b.get("class"), {})
    iv = int(b["interval"]) if (b.get("interval") or "").isdigit() else None
    last = next((e for e in reversed(events(limit=5000)) if e["actor"] == key and e["type"] == "run.start"), None)
    nxt = None
    if iv and last:
        t0 = calendar.timegm(time.strptime(last["ts"][:19], "%Y-%m-%dT%H:%M:%S"))   # event times are UTC
        nxt = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0 + iv))
    duties = ""
    offs = read(ROOT / "org/OFFICERS.md")
    m = re.search(rf"^## [^\n]*\(`{re.escape(key)}`\)\n(.*?)(?=^## |\Z)", offs, re.S | re.M)
    if m: duties = m.group(1).strip()[:1600]
    return 200, {**b, "class_name": cls.get("name", ""), "class_about": cls.get("about", ""), "modules": modules(b.get("tools")),
                 "requested_modules": modules(cls.get("requested", "")) if b.get("class") != "officer" else [],
                 "schedule": {"every_minutes": iv // 60 if iv else None, "daily_cap": b.get("cap"), "next_run": nxt,
                              "last_run": last["ts"] if last else None}, "duties": duties,
                 "prompt": b.get("prompt", "") if not PUBLIC else "(hidden in public view)"}

# ---------- conversations: board threads as group chats ----------
POST_RE = re.compile(r"^### (\S+) · (\S+)\n(.*?)(?=^### |\Z)", re.S | re.M)
def _author(k):
    k = k.lower()
    return "steward" if k in ("rex", "steward") else k
def summary(text, n=160):
    """The post's summary: its first line when that line is short (the COMMON.md convention), else its first sentence."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines: return ""
    first = re.sub(r"^[-*] +|^#+ +", "", lines[0])
    if len(first) <= n and (len(lines) == 1 or len(first) >= 20): out = first
    else:
        flat = " ".join(lines); m = re.match(r"(.{20,%d}?[.!?])(\s|$)" % n, flat); out = m.group(1) if m else flat[:n].rstrip() + "…"
    return re.sub(r"\*\*|`", "", out)

def thread(path):
    text = read(path); lines = text.splitlines()
    tag = lines[0].strip() if lines and lines[0].startswith("#") and not lines[0].startswith("##") else ""
    posts = [{"who": _author(m.group(1)), "ts": m.group(2), "text": m.group(3).strip(), "summary": summary(m.group(3))} for m in POST_RE.finditer(text)]
    name = pathlib.Path(path).stem
    title = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name).replace("-", " ").strip().capitalize()
    return {"id": name, "title": title or name, "tag": tag.lstrip("#").split()[0] if tag else "", "posts": posts}
def conversations(hours=48, limit=8):
    out = []
    for p in glob.glob(str(ROOT / "org/board/*.md")):
        if pathlib.Path(p).name == "README.md": continue
        t = thread(p)
        if not t["posts"]: continue
        who = []
        for x in t["posts"]:
            if x["who"] not in who: who.append(x["who"])
        if len(who) < 2: continue            # a conversation needs at least two participants
        last = t["posts"][-1]
        out.append({"id": t["id"], "title": t["title"], "tag": t["tag"], "participants": who, "count": len(t["posts"]),
                    "last_ts": last["ts"], "last_who": last["who"], "last_text": last["text"][:140], "last_summary": last["summary"]})
    out.sort(key=lambda c: c["last_ts"], reverse=True)
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - hours * 3600))
    recent = [c for c in out if c["last_ts"][:19] >= cutoff]
    return (recent or out)[:limit]
def conversation(cid):
    if not re.match(r"^[\w.-]+$", cid): return 400, {"error": "bad conversation id"}
    p = ROOT / "org/board" / f"{cid}.md"
    if not p.exists(): return 404, {"error": "no such conversation"}
    t = thread(p)
    who = []
    for x in t["posts"]:
        if x["who"] not in who: who.append(x["who"])
    doing = []
    if not PUBLIC and t["posts"]:
        since = t["posts"][0]["ts"][:19]
        skip = {"run.start", "run.end", "agent.prompt", "agent.transcript", "state.checkpoint", "org.genesis", "org.launch"}
        for e in events(limit=5000):
            if e["actor"] in who and e["type"] not in skip and e["ts"][:19] >= since:
                d = e.get("data", {})
                if d.get("reason") == "genesis snapshot": continue                              # bookkeeping, not activity
                if e["type"].startswith("file.") and d.get("path", "").startswith("org/board/"): continue   # the posts themselves
                if e["type"].startswith("file."):
                    last = doing[-1] if doing else None                                        # collapse runs of edits
                    if last and last["who"] == e["actor"] and last.get("files") is not None:
                        last["files"].append(d.get("path", "")); last["ts"] = e["ts"]
                        n = len(last["files"]); last["what"] = f"edited {n} files: " + ", ".join(pathlib.Path(x).name for x in last["files"][-3:]) + (" and more" if n > 3 else "")
                        continue
                    doing.append({"who": e["actor"], "ts": e["ts"], "type": e["type"], "files": [d.get("path", "")],
                                  "what": ("edited " if e["type"] == "file.put" else "removed ") + d.get("path", "")})
                    continue
                doing.append({"who": e["actor"], "ts": e["ts"], "what": (d.get("summary") or e["type"].replace(".", " "))[:140], "type": e["type"]})
    for x in doing: x.pop("files", None)
    return 200, {**t, "participants": who, "doing": doing[-60:]}

def charter_version():
    m = re.search(r"Charter version: ([\d.]+)", read(ROOT / "CHARTER.md"))
    return m.group(1) if m else "?"

# ---------- data ----------
def overview():
    ev = events(limit=5000)
    offices = [a["key"] for a in roster() if a["status"] == "active"]
    last_run = {}
    for e in ev:
        if e["type"] in ("run.start", "run.end"): last_run[e["actor"]] = {"ts": e["ts"], "type": e["type"]}
    sprint = None
    sj = sorted(glob.glob(str(ROOT / "sprints/S-*/sprint.json")))
    if sj:
        s = json.loads(read(sj[-1])); sprint = {"id": s["id"], "phase": s["phase"], "theme": s.get("theme", ""), "items": len(s.get("items", {}))}
    pauses = sorted(p.name.replace("PAUSE-", "") for p in (ROOT / "org").glob("PAUSE-*"))
    waiting = []
    if not PUBLIC:
        drafts = sorted(p.name for p in (ROOT / "private/outbox/pending").glob("*.md") if not p.name.endswith(".REVIEW.md"))
        if drafts: waiting.append({"what": f"{len(drafts)} draft{'s' if len(drafts) != 1 else ''} to approve or reject",
                                   "how": "agents/bin/approve.sh private/outbox/pending/<file>", "detail": drafts[:5]})
        issued = []
        for p in sorted((ROOT / "private/edicts").glob("E-*.md")):
            fm, body = frontmatter(read(p))
            if edict_state(fm, sections(body).get("History", "")) == "issued": issued.append(f"{fm.get('id')}: {fm.get('title')}")
        if issued: waiting.append({"what": f"{len(issued)} edict{'s' if len(issued) != 1 else ''} not yet implemented",
                                   "how": "The Project Manager routes these; ask Claude to finish them.", "detail": issued[-5:]})
    if sj:
        s = json.loads(read(sj[-1]))
        if s["phase"] == "steward": waiting.append({"what": f"Sprint {s['id']} is waiting for your sign-off", "how": "python3 agents/bin/sprint.py steward --approve", "detail": []})
        if s["phase"] == "review": waiting.append({"what": f"Sprint {s['id']} is waiting for your review", "how": "python3 agents/bin/sprint.py review --file review.md", "detail": []})
    if (ROOT / "org" / "STOP").exists(): waiting.append({"what": "The Collective is stopped", "how": "rm org/STOP when you're ready (Steward only)", "detail": []})
    latest_cases = []
    for p in sorted((ROOT / "org/cases").glob("C-*.md"))[-3:][::-1]:
        fm, _ = frontmatter(read(p)); latest_cases.append({"id": fm.get("id"), "title": fm.get("title"), "court": fm.get("court"), "date": fm.get("date")})
    proj = []
    for d in sorted(x for x in (ROOT / "projects").glob("[0-9][0-9][0-9]-*") if x.is_dir()):
        fm, _ = frontmatter(read(d / "PROJECT.md"))
        proj.append({"id": fm.get("id"), "name": fm.get("name"), "status": fm.get("status"), "current": fm.get("current_version", ""),
                     "versions": len(list((d / "versions").glob("version-*.md")))})
    return {
        "charter_version": charter_version(),
        "stopped": (ROOT / "org" / "STOP").exists(),
        "paused": pauses,
        "setup_complete": (ROOT / "private" / ".setup-complete").exists(),
        "public_head": git("rev-parse", "--short", "HEAD"),
        "private_head": "" if PUBLIC else git("rev-parse", "--short", "HEAD", cwd=ROOT / "private"),
        "last_event": event_count(),
        "counts": {
            "amendments": len(list((ROOT / "amendments").glob("amendment-*.md"))),
            "cases": len(list((ROOT / "org/cases").glob("C-*.md"))),
            "projects": len([d for d in (ROOT / "projects").glob("[0-9][0-9][0-9]-*") if d.is_dir()]),
            "edicts": len(list((ROOT / "private/edicts").glob("E-*.md"))),
            "sprints": len(sj),
            "events": event_count(),
            "library": len(re.findall(r"\.pdf  (?:https|private)", read(ROOT / "research/library/LIBRARY.md"))),
        },
        "sprint": sprint,
        "waiting": waiting,
        "latest_cases": latest_cases,
        "projects": proj,
        "offices": [{"key": o, "last": last_run.get(o)} for o in offices],
        "mode": "public" if PUBLIC else "private",
        "as_of": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

def charter():
    text = read(ROOT / "CHARTER.md")
    i = [m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", text)]
    body = text[:i[-1]] if i else text
    p1 = re.search(r"# PART I — CONSTITUTION(.*?)\n# PART II — ", body, re.S)
    arts = []
    if p1:
        for m in re.finditer(r"^## (Article [0-9]+ — [^\n]+)\n(.*?)(?=^## Article |\Z)", p1.group(1), re.S | re.M):
            arts.append({"title": m.group(1), "text": m.group(2).strip()})
    timeline = []
    for line in read(ROOT / "charter/TIMELINE.md").splitlines():
        if line.startswith("| v"):
            c = [x.strip() for x in line.strip("|").split("|")]
            if len(c) >= 9:
                timeline.append({"version": c[0], "date": c[1], "amendment": c[2], "class": c[3], "title": c[4],
                                 "articles": c[5], "members": c[6], "plugins": c[7], "files": c[8]})
    return {"version": charter_version(), "articles": arts, "timeline": timeline,
            "mission": read(ROOT / "org/MISSION.md"), "officers": read(ROOT / "org/OFFICERS.md"),
            "permissions": read(ROOT / "org/AGENT-PERMISSIONS.md")}

def amendments():
    out = []
    for p in sorted((ROOT / "amendments").glob("amendment-*.md")):
        fm, body = frontmatter(read(p)); s = sections(body)
        out.append({"file": p.name, **{k: fm.get(k, "") for k in ("id", "title", "class", "status", "charter_version", "proposer", "proposed")},
                    "reason": s.get("Reason", ""), "vote": s.get("Vote", ""), "outcome": s.get("Outcome", ""), "discussion": s.get("Discussion", "")})
    return out

def cases():
    status = {}
    for line in read(ROOT / "org/cases/CITATOR.md").splitlines():
        m = re.match(r"- \*\*(C-\d{4})\*\* · (\w+) · cited by: (.*)$", line)
        if m: status[m.group(1)] = {"status": m.group(2), "cited_by": m.group(3)}
    out = []
    for p in sorted((ROOT / "org/cases").glob("C-*.md")):
        fm, body = frontmatter(read(p)); s = sections(body)
        cites = re.findall(r"\{case: (C-\d{4}), treatment: (\w+)\}", read(p))
        out.append({"id": fm.get("id", p.name[:6]), "title": fm.get("title", ""), "court": fm.get("court", ""),
                    "date": fm.get("date", ""), "labels": fm.get("labels", "").strip("[]"), "headnote": fm.get("headnote", ""),
                    "source": fm.get("source", ""), "holding": s.get("Holding", ""), "question": s.get("Question", ""),
                    "reasoning": s.get("Reasoning", ""), "facts": s.get("Facts", ""), "dissent": s.get("Dissent", ""),
                    "history": s.get("History", ""), "cites": cites, **status.get(fm.get("id", ""), {"status": "good_law", "cited_by": ""})})
    return out

def projects():
    out = []
    for d in sorted(p for p in (ROOT / "projects").glob("[0-9][0-9][0-9]-*") if p.is_dir()):
        fm, body = frontmatter(read(d / "PROJECT.md"))
        vs = []
        for vp in sorted((d / "versions").glob("version-*.md")):
            vfm, vbody = frontmatter(read(vp)); vs.append({**vfm, "body": vbody})
        out.append({"folder": d.name, **fm, "body": body, "spec": read(d / "spec.md"), "versions": vs,
                    "discussion": read(d / "discussion.md")})
    return {"projects": out, "proposed": read(ROOT / "projects/PROPOSED.md")}

def sprints():
    out = []
    for sj in sorted(glob.glob(str(ROOT / "sprints/S-*/sprint.json"))):
        s = json.loads(read(sj)); d = pathlib.Path(sj).parent
        out.append({**s, "plan": read(d / "plan.md"), "report": read(d / "postmortem/report.md"),
                    "review": read(d / "postmortem/human-review.md"),
                    "proposals": {p.stem: read(p) for p in sorted((d / "proposals").glob("*.md"))}})
    return {"sprints": out, "okrs": read(ROOT / "org/OKRS.md"), "kpis": read(ROOT / "org/KPIS.md")}

def edicts():
    if PUBLIC: return {"hidden": True, "count": len(list((ROOT / "private/edicts").glob("E-*.md")))}
    out = []
    for p in sorted((ROOT / "private/edicts").glob("E-*.md")):
        fm, body = frontmatter(read(p)); s = sections(body)
        out.append({**{k: fm.get(k, "") for k in ("id", "title", "issued", "implemented_by")},
                    "status": edict_state(fm, s.get("History", "")),
                    "words": s.get("Original words", ""), "edict": s.get("Edict", ""), "outcome": s.get("Outcome", ""),
                    "history": s.get("History", "")})
    return {"edicts": out}

def verify():
    if time.time() - _verify_cache["t"] < 60 and _verify_cache["data"]: return _verify_cache["data"]
    checks = [("Charter log", [PY, "agents/bin/charter-verify.py"]),
              ("Amendments", [PY, "agents/bin/amendment.py", "check"]),
              ("Case law", [PY, "agents/bin/case.py", "check"]),
              ("Projects", [PY, "agents/bin/projects.py", "check"]),
              ("Seed", ["bash", "agents/bin/seed-check.sh"]),
              ("Generated files", [PY, "agents/bin/charter.py", "materialize", "--dry-run"])]
    if not PUBLIC:
        checks += [("Edicts", [PY, "agents/bin/edict.py", "check"]), ("Event log", [PY, "agents/bin/eventlog.py", "verify"])]
    out = []
    for name, cmd in checks:
        code, text = run(*cmd, timeout=120)
        ok = code == 0 and "FAIL" not in text and not (name == "Generated files" and "would change 0 files" not in text)
        out.append({"name": name, "ok": ok, "output": text[-1500:]})
    _verify_cache.update(t=time.time(), data=out)
    return out

def tasks():
    """Every task on the tsk board (org/tasks, public): its number, title, owner office (thread), and state."""
    try: d = json.loads(read(ROOT / "org/tasks/tsk.json") or "{}")
    except ValueError: d = {}
    return [{"n": t.get("number"), "title": t.get("title", ""), "office": t.get("thread") or "", "state": t.get("status", "open"),
             "notes": (t.get("notes") or "")[:300]} for t in d.get("tasks", []) if not t.get("deleted") and not t.get("archived")]

def qint(q, k, default, lo, hi):
    """A query number, clamped; anything that isn't a number falls back to the default."""
    try: return max(lo, min(hi, int(q.get(k, [default])[0] or default)))
    except (TypeError, ValueError): return default

def huddle():
    """The open huddle, if any: the newest org/board/*-huddle-*.md, open until the Steward closes it (Article 18.7(f))."""
    files = sorted(glob.glob(str(ROOT / "org/board/*-huddle-*.md")))
    if not files: return None
    t = thread(files[-1])
    if not t["posts"]: return None
    start, last = t["posts"][0], t["posts"][-1]
    closed = last["who"] == "steward" and last["text"].startswith("Huddle closed")
    return {"id": t["id"], "topic": summary(start["text"], 120), "started": start["ts"], "open": not closed,
            "replies": len(t["posts"]) - 1}

def huddle_write(h, action):
    """/api/huddle (start) and /api/huddle/close: the Steward calls everyone to the coffee machine (Article 18.7(f))."""
    if "Huddles." not in read(ROOT / "CHARTER.md"):   # a write the Charter doesn't allow yet (Article 18.7(f), A-0024)
        return h.send(403, {"error": "Huddles are waiting for the Steward's approval of amendment A-0024."})
    p = guarded(h, "huddle", 3)
    if p is None: return
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cur = huddle()
    if action == "close":
        if not cur or not cur["open"]: return h.send(400, {"error": "no huddle is open"})
        with (ROOT / "org/board" / f"{cur['id']}.md").open("a") as f: f.write(f"\n### rex · {ts}\nHuddle closed. Back to work.\n")
        run(PY, "agents/bin/eventlog.py", "record", "--actor", "steward", "--type", "huddle.closed", "--data", json.dumps({"summary": "huddle closed", "path": f"org/board/{cur['id']}.md"}))
        return h.send(200, {"ok": True, "message": "Huddle closed."})
    if cur and cur["open"]: return h.send(400, {"error": "a huddle is already open"})
    topic = str(p.get("topic", "")).strip() or "Quick huddle: where do things stand?"
    if len(topic) > 1000: return h.send(400, {"error": "keep the topic under 1000 characters"})
    name = f"{time.strftime('%Y-%m-%d', time.gmtime())}-huddle-{time.strftime('%H%M', time.gmtime())}"
    (ROOT / "org/board" / f"{name}.md").write_text(f"#huddle\n### rex · {ts}\n{topic}\n\n@all: huddle at the coffee machine. On your next run, answer here first, in one or two sentences, before any other work.\n")
    run(PY, "agents/bin/eventlog.py", "record", "--actor", "steward", "--type", "huddle.called", "--data", json.dumps({"summary": f"huddle called: {summary(topic, 80)}", "path": f"org/board/{name}.md"}))
    h.send(200, {"ok": True, "message": "Huddle called: everyone answers on their next run.", "id": name})

OUTBOX_BY = {"social": ("-thread-", "-reply-", "-post-"), "media": ("-media-",), "scribe": ("-blog-", "-announce")}
def flags(offices):
    """Why each agent is waiting, from the records: blocked, awaiting approval, needs instructions, scheduled, busy."""
    T = tasks(); pending = [] if PUBLIC else [p.name for p in (ROOT / "private/outbox/pending").glob("*.md") if not p.name.endswith(".REVIEW.md")]
    asks = {}
    for bp in glob.glob(str(ROOT / "org/board/*.md")):
        t = thread(bp)
        if t["tag"] == "question" and t["posts"] and t["posts"][-1]["who"] != "steward" and "@rex" in read(bp):
            asks.setdefault(t["posts"][-1]["who"], []).append(t["title"])
    for k, o in offices.items():
        f = []
        if o["status"] == "working": f.append({"kind": "busy", "note": "Busy: running now"})
        mine_blocked = [t for t in T if t["office"] == k and t["state"] == "blocked"]
        if o["status"] == "stuck" or mine_blocked:
            f.append({"kind": "blocked", "note": "Blocked: " + ("stuck in a run for over 2 hours" if o["status"] == "stuck" else f"task T{mine_blocked[0]['n']}: {mine_blocked[0]['title']}")})
        drafts = [n for n in pending if any(x in n for x in OUTBOX_BY.get(k, ()))]
        if drafts: f.append({"kind": "approval", "note": f"Awaiting approval: {len(drafts)} draft{'s' if len(drafts) > 1 else ''} in your outbox"})
        if asks.get(k): f.append({"kind": "instructions", "note": "Needs instructions: " + asks[k][0]})
        if not f and o["status"] in ("idle", "never"): f.append({"kind": "scheduled", "note": "Awaiting its next scheduled run"})
        o["flags"] = f

def live():
    """The control plane's single live feed: every office's state right now, activity, pipeline, schedule."""
    ev = events(limit=5000)
    now = time.time()
    def ts(e):
        try: return calendar.timegm(time.strptime(e["ts"][:19], "%Y-%m-%dT%H:%M:%S"))   # UTC, correct in daylight saving time too
        except Exception: return 0
    today = time.strftime("%Y-%m-%d", time.gmtime())
    R = roster()
    offices = {a["key"]: {"key": a["key"], "status": "never", "since": None, "runs_today": 0, "last": None, "last_ts": None}
               for a in R if a["status"] == "active"}
    open_runs = {}
    for e in ev:
        a = e["actor"]
        if a not in offices: continue
        o = offices[a]
        if e["type"] == "run.start":
            open_runs[a] = e
            if e["ts"][:10] == today: o["runs_today"] += 1
        elif e["type"] == "run.end":
            open_runs.pop(a, None)
        if e["type"] not in ("run.start", "run.end", "agent.prompt", "agent.transcript"):
            d = e.get("data", {})
            o["last"] = (e["type"].replace(".", " ") + (": " + (d.get("summary") or d.get("path") or "") if (d.get("summary") or d.get("path")) else ""))[:140]
        o["last_ts"] = e["ts"]
    # what each agent is actually saying: its latest post on the board ("### <office> · <timestamp>\n<message>")
    for bp in glob.glob(str(ROOT / "org/board/*.md")):
        for m in re.finditer(r"^### (\w+) · (\S+)\n(.+?)(?=\n### |\Z)", read(bp), re.S | re.M):
            k, t, msg = m.group(1), m.group(2), " ".join(m.group(3).split())
            if k in offices and (not offices[k]["last_ts"] or t > offices[k]["last_ts"]):
                offices[k]["last"], offices[k]["last_ts"] = msg[:160], t
    for k, o in offices.items():
        if (ROOT / "org" / f"PAUSE-{k}").exists(): o["status"] = "paused"
        elif k in open_runs:
            age = now - ts(open_runs[k]); o["since"] = open_runs[k]["ts"]
            o["status"] = "stuck" if age > 7200 else "working"
        elif o["last_ts"]:
            o["status"] = "idle"
    # activity: events per minute over the last 60 minutes
    buckets = [0] * 60
    for e in ev:
        m = int((now - ts(e)) // 60)
        if 0 <= m < 60: buckets[59 - m] += 1
    incidents_24h = sum(1 for e in ev if e["type"] == "incident" and now - ts(e) < 86400)
    count = lambda pattern: len([p for p in glob.glob(str(ROOT / pattern)) if not p.endswith(".gitkeep")])
    pipeline = [
        {"stage": "Papers", "n": count("research/briefs/*.md"), "hint": "briefed"},
        {"stage": "Proposals", "n": count("ideas/*.md"), "hint": "proposed"},
        {"stage": "Projects", "n": count("projects/[0-9][0-9][0-9]-*/versions/version-*.md"), "hint": "versions"},
        {"stage": "Demos", "n": len([d for d in glob.glob(str(ROOT / "media/exports/*")) if pathlib.Path(d).is_dir()]), "hint": "exported"},
        {"stage": "Posts", "n": count("private/outbox/posted/*.md") + count("blog/2*.md"), "hint": "published"},
    ]
    cfg = read(ROOT / "agents/config.env") or read(ROOT / "agents/config.example.env")
    sched = dict(re.findall(r"^(SPRINT_[A-Z]+)='([^']*)'", cfg, re.M))
    ov = overview()
    flags(offices)
    return {"offices": list(offices.values()), "roster": R, "huddle": huddle(), "activity": buckets, "incidents_24h": incidents_24h, "pipeline": pipeline,
            "schedule": sched, "waiting": ov["waiting"], "sprint": ov["sprint"], "stopped": ov["stopped"],
            "setup_complete": ov["setup_complete"], "charter_version": ov["charter_version"], "last_event": ov["last_event"],
            "public_head": ov["public_head"], "mode": ov["mode"], "counts": ov["counts"]}

SAFE_KINDS = {"input", "suggestion"}

def comment(n, payload):
    author = re.sub(r"[^A-Za-z0-9 ._-]", "", str(payload.get("author", "")).strip())[:40] or "anonymous"
    kind = payload.get("kind", "suggestion"); text = str(payload.get("text", "")).strip()
    if kind not in SAFE_KINDS: return 400, {"error": "kind must be input or suggestion"}
    if not (3 <= len(text) <= 4000): return 400, {"error": "comment must be 3 to 4000 characters"}
    code, out = run(PY, "agents/bin/projects.py", "comment", str(int(n)), "--author", f"human:{author}", "--kind", kind, "--text", text)
    return (200, {"ok": True, "message": out}) if code == 0 else (400, {"error": out})

# ---------- history: version 001's time travel (dashboard/history.py) ----------
import history as HIST
import shell_bridge as SHELL
FONT_RE = re.compile(r"^[\w.-]+\.(woff2|css|txt)$")

def history_route(h):
    """/history (time travel by commit, event, or date; Charter diff) and the fonts served locally."""
    u = urllib.parse.urlparse(h.path); q = dict(urllib.parse.parse_qsl(u.query))
    try:
        if u.path == "/history": h.send(200, (ROOT / "dashboard/static/index.html").read_bytes(), "text/html"); return True
        if u.path.startswith("/static/"):
            name = u.path[len("/static/"):]
            f = ROOT / "dashboard/static" / name
            if not re.fullmatch(r"[\w.-]+", name) or name.startswith(".") or not f.is_file(): h.send(404, {"error": "not found"}); return True
            h.send(200, f.read_bytes(), {".js": "text/javascript", ".css": "text/css", ".html": "text/html"}.get(f.suffix, "application/octet-stream")); return True
        if u.path.startswith("/fonts/"):
            name = u.path[len("/fonts/"):]
            f = ROOT / "dashboard/fonts" / name
            if not FONT_RE.fullmatch(name) or not f.is_file(): h.send(404, {"error": "not found"}); return True
            h.send(200, f.read_bytes(), {".woff2": "font/woff2", ".css": "text/css", ".txt": "text/plain"}[f.suffix]); return True
        if u.path == "/api/state": h.send(200, HIST.state(q.get("at"))); return True
        if u.path == "/api/charter-diff": h.send(200, HIST.charter_diff(HIST.resolve(q.get("at")), q.get("from"), q.get("to"))); return True
        if u.path == "/api/stream":
            h.send_response(200); h.send_header("Content-Type", "text/event-stream"); h.send_header("Cache-Control", "no-store"); h.end_headers()
            last = None
            try:
                while True:
                    fp = HIST.fingerprint()
                    h.wfile.write((f"event: changed\ndata: {fp}\n\n" if fp != last else ": keepalive\n\n").encode()); h.wfile.flush()
                    last = fp; time.sleep(1)
            except (BrokenPipeError, ConnectionResetError):
                return True
    except ValueError as e:
        h.send(400, {"error": str(e)}); return True
    return False

# ---------- http ----------
LAST_COMMENT = {"t": 0}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer"); self.send_header("X-Frame-Options", "DENY")
        self.end_headers(); self.wfile.write(data)
    def host_ok(self):
        """Only requests addressed to this machine: a web page elsewhere can't read the dashboard by DNS rebinding."""
        return (self.headers.get("Host") or "").rsplit(":", 1)[0] in ("127.0.0.1", "localhost")
    def do_GET(self):
        if not self.host_ok(): return self.send(403, {"error": "the dashboard answers only on 127.0.0.1"})
        path = urllib.parse.urlparse(self.path).path
        if path == "/ws/shell": return SHELL.handle(self, PUBLIC, self.server.server_port)       # Article 18.7(c)(iii)
        if path == "/api/shell/token":
            if PUBLIC: return self.send(403, {"error": "the terminal is off in public view"})
            return self.send(200, {"token": SHELL.new_token(), "valid_seconds": SHELL.TOKEN_SECS})
        if path.startswith("/vendor/xterm/"):
            name = path[len("/vendor/xterm/"):]; f = ROOT / "dashboard/vendor/xterm" / name
            if not re.fullmatch(r"[\w.-]+\.(js|css)", name) or not f.is_file(): return self.send(404, {"error": "not found"})
            return self.send(200, f.read_bytes(), "text/javascript" if name.endswith(".js") else "text/css")
        if history_route(self): return
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        m = re.match(r"^/api/agents/([a-z][a-z0-9]{1,15})/permissions$", u.path)
        if m:
            code, out = run(PY, "agents/bin/perms.py", "show", m.group(1))
            return self.send(200, json.loads(out)) if code == 0 else self.send(404, {"error": out})
        if u.path == "/api/tasks": return self.send(200, tasks())
        routes = {"/api/overview": overview, "/api/charter": charter, "/api/amendments": amendments, "/api/cases": cases,
                  "/api/projects": projects, "/api/sprints": sprints, "/api/edicts": edicts, "/api/verify": verify, "/api/live": live}
        if u.path in ("/", "/floor"):
            return self.send(200, read(ROOT / "dashboard/floor.html").encode(), "text/html")
        if u.path in ("/scope", "/control"):
            return self.send(200, read(ROOT / "dashboard/control.html").encode(), "text/html")
        if u.path in ("/records", "/index.html"):
            return self.send(200, read(ROOT / "dashboard/index.html").encode(), "text/html")
        if u.path == "/api/events":
            if PUBLIC: return self.send(200, {"hidden": True})
            return self.send(200, events(after=qint(q, "after", 0, 0, 10**9), limit=qint(q, "limit", 300, 1, 5000)))
        if u.path == "/api/conversations":
            return self.send(200, conversations(hours=qint(q, "hours", 48, 1, 24 * 60)))
        m = re.match(r"^/api/conversations/([\w.-]+)$", u.path)
        if m:
            code, body = conversation(m.group(1)); return self.send(code, body)
        if u.path == "/api/classes":
            return self.send(200, json.loads(read(ROOT / "agents/classes.json") or "{}"))
        m = re.match(r"^/api/agents/([a-z][a-z0-9]{1,15})/bio$", u.path)
        if m:
            code, body = bio(m.group(1)); return self.send(code, body)
        if u.path in routes:
            try: return self.send(200, routes[u.path]())
            except Exception as e: return self.send(500, {"error": str(e)})
        self.send(404, {"error": "not found"})
    def do_POST(self):
        if not self.host_ok(): return self.send(403, {"error": "the dashboard answers only on 127.0.0.1"})
        if self.path == "/api/agents/propose": return self.propose_agent()
        m = re.match(r"^/api/agents/([a-z][a-z0-9]{1,15})/(move|terminal|permissions|fire)$", self.path)
        if m: return agent_write(self, m.group(1), m.group(2))
        if self.path in ("/api/huddle", "/api/huddle/close"): return huddle_write(self, "close" if self.path.endswith("close") else "start")
        m = re.match(r"^/api/conversations/([\w.-]+)/comment$", self.path)
        if m: return chat_comment(self, m.group(1))
        m = re.match(r"^/api/projects/(\d+)/comment$", self.path)
        if not m: return self.send(404, {"error": "not found"})
        if self.headers.get("Origin") not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"):
            return self.send(403, {"error": "cross-origin comments refused"})
        if time.time() - LAST_COMMENT["t"] < 5: return self.send(429, {"error": "one comment every 5 seconds"})
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n > 20000: return self.send(413, {"error": "too long"})
        try: payload = json.loads(self.rfile.read(n) or b"{}")
        except Exception: return self.send(400, {"error": "bad JSON"})
        code, body = comment(m.group(1), payload); LAST_COMMENT["t"] = time.time()
        self.send(code, body)

LAST_WRITE = {}
def guarded(h, kind, gap):
    """Shared guard for the dashboard's writes: private view only, same origin, rate-limited, small JSON body."""
    if PUBLIC: h.send(403, {"error": "this is off in public view"}); return None
    if h.headers.get("Origin") not in (f"http://127.0.0.1:{h.server.server_port}", f"http://localhost:{h.server.server_port}"):
        h.send(403, {"error": "cross-origin requests refused"}); return None
    if time.time() - LAST_WRITE.get(kind, 0) < gap: h.send(429, {"error": f"one {kind} every {gap} seconds"}); return None
    n = int(h.headers.get("Content-Length", "0") or 0)
    if n > 8000: h.send(413, {"error": "too long"}); return None
    try: p = json.loads(h.rfile.read(n) or b"{}")
    except Exception: h.send(400, {"error": "bad JSON"}); return None
    LAST_WRITE[kind] = time.time(); return p if isinstance(p, dict) else {}

def agent_write(h, key, action):
    """/api/agents/<key>/move | terminal | permissions (Articles 18.7(c), 18.8, 18.7(e))."""
    if action == "move":
        p = guarded(h, "move", 1)
        if p is None: return
        code, out = run(PY, "agents/bin/spawn.py", "move", key, "--room", str(p.get("room", "")))
    elif action == "terminal":
        p = guarded(h, "terminal", 3)
        if p is None: return
        code, out = run("bash", "agents/bin/terminal.sh", key, "--standalone" if p.get("standalone") else "auto")
    elif action == "permissions":
        p = guarded(h, "permission change", 1)
        if p is None: return
        if "rank" in p:
            group = ",".join(k for k in p.get("group", []) if re.fullmatch(r"[a-z][a-z0-9]{1,15}", str(k)))
            code, out = run(PY, "agents/bin/perms.py", "rank", key, str(p["rank"]), "--group", group, "--steward")
        else:
            code, out = run(PY, "agents/bin/perms.py", "set", key, str(p.get("capability", "")), "on" if p.get("on") else "off", "--steward")
    elif action == "fire":
        # Article 18.7(g): pause the agent now (the Steward's pause) and draft its retirement motion (Articles 3.6, 3.8)
        if "**Firing.**" not in read(ROOT / "CHARTER.md"):
            return h.send(403, {"error": "Firing is waiting for the Steward's approval of amendment A-0026."})
        p = guarded(h, "fire", 3)
        if p is None: return
        reason = str(p.get("reason", "")).strip()[:500] or "The Steward fired this agent from the dashboard."
        code, out = run(PY, "agents/bin/spawn.py", "retire", key, "--reason", reason, "--proposer", "steward")
        if code == 0:
            m = re.search(r"(A-\d{4})", out)
            (ROOT / "org" / f"PAUSE-{key}").write_text(f"paused by the Steward: fired, pending retirement motion {m.group(1) if m else ''}\n")
            run(PY, "agents/bin/eventlog.py", "record", "--actor", "steward", "--type", "agent.fired",
                "--data", json.dumps({"summary": f"fired {key}: paused; retirement motion {m.group(1) if m else ''}", "agent": key}))
            out = f"{out.strip()}. {key} is paused now; the retirement takes effect when the motion passes."
    else:
        return h.send(404, {"error": "not found"})
    h.send(200 if code == 0 else 400, {"ok": code == 0, "message": out.replace("REFUSED: ", "")})

def chat_comment(h, cid):
    """/api/conversations/<id>/comment: the Steward's comment in a floor chat (Article 18.7(d))."""
    p = guarded(h, "comment", 2)
    if p is None: return
    text = str(p.get("text", "")).strip()
    if not (1 <= len(text) <= 4000): return h.send(400, {"error": "a comment is 1 to 4000 characters"})
    b = ROOT / "org/board" / f"{cid}.md"
    if not re.fullmatch(r"[\w.-]+", cid) or not b.exists(): return h.send(404, {"error": "no such conversation"})
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with b.open("a") as f: f.write(f"\n### rex · {ts}\n{text}\n")
    run(PY, "agents/bin/eventlog.py", "record", "--actor", "steward", "--type", "board.comment",
        "--data", json.dumps({"summary": f"comment in {cid}: {summary(text, 100)}", "path": f"org/board/{cid}.md"}))
    msg = "Comment added to the chat."
    if p.get("direction"):   # a direction from the Steward is an edict (Article 15)
        code, out = run(PY, "agents/bin/edict.py", "new", "--title", f"Chat direction: {summary(text, 60)}", "--text", text,
                        "--restatement", f"A direction the Steward gave in the floor chat for {cid} (org/board/{cid}.md).")
        m = re.search(r"issued (E-\d{4})", out); msg += f" Recorded as {m.group(1)}." if m else " (The edict couldn't be recorded: " + out[-200:] + ")"
    h.send(200, {"ok": True, "message": msg})

def _propose(self):
    """The wizard's one action: draft a membership motion for a new agent (Article 3.6). It creates no agent."""
    if PUBLIC: return self.send(403, {"error": "proposing agents is off in public view"})
    if self.headers.get("Origin") not in (f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"):
        return self.send(403, {"error": "cross-origin requests refused"})
    if time.time() - LAST_COMMENT["t"] < 5: return self.send(429, {"error": "one action every 5 seconds"})
    n = int(self.headers.get("Content-Length", "0") or 0)
    if n > 20000: return self.send(413, {"error": "too long"})
    try: p = json.loads(self.rfile.read(n) or b"{}")
    except Exception: return self.send(400, {"error": "bad JSON"})
    LAST_COMMENT["t"] = time.time()
    args = [PY, "agents/bin/spawn.py"] + (["clone", str(p.get("clone_of"))] if p.get("clone_of") else ["propose"])
    for flag, k in [("--class", "class"), ("--name", "name"), ("--focus", "focus"), ("--key", "key"), ("--room", "room"),
                    ("--interval", "interval"), ("--cap", "cap"), ("--model", "model")]:
        if p.get(k) not in (None, ""): args += [flag, str(p[k])]
    args += ["--proposer", "steward"]
    code, out = run(*args)
    return self.send(200, {"ok": True, "message": out}) if code == 0 else self.send(400, {"error": out.replace("REFUSED: ", "")})
H.propose_agent = _propose

def main():
    global PUBLIC
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=4848); ap.add_argument("--public", action="store_true")
    a = ap.parse_args(); PUBLIC = a.public; HIST.PUBLIC = PUBLIC
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    print(f"The Collective Dashboard ({'public' if PUBLIC else 'private'} mode): http://127.0.0.1:{a.port}  (Ctrl-C to stop)", flush=True)
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()
