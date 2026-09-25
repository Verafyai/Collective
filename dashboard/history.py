#!/usr/bin/env python3
"""The Collective Dashboard server (project P-001; Charter Articles 18 and 21).

Python standard library only. Read-only: every panel is computed on request from
versioned records (the public repo, the private repo, and the event log) and says
which commit and event it reflects. It keeps no data of its own; past views are
rebuilt into a temporary folder that's deleted on exit.

  python3 dashboard/server.py [--public] [--port 4848]

Binds 127.0.0.1 only and answers only Host 127.0.0.1 / localhost (no DNS rebinding).
Time travel: /api/state?at=live | commit:<sha> | event:<n> | date:<YYYY-MM-DD[THH:MM]>
"""
import argparse, atexit, datetime, hashlib, http.server, json, pathlib, re, shutil, socketserver
import subprocess, sys, tempfile, threading, time, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATIC = ROOT / "dashboard" / "static"
HOST = "127.0.0.1"
PUBLIC = False
CACHE = pathlib.Path(tempfile.mkdtemp(prefix="collective-dashboard-"))
atexit.register(shutil.rmtree, CACHE, True)
LOCK = threading.Lock()
MEMO = {}          # (key) -> (expires, value)

PANELS = [  # the spec's thirteen panels, in rail order; "v" = the version that brings it
    ("mission", "Mission", 1), ("charter", "Charter", 1), ("versioning", "Versioning", 1),
    ("progress", "Progress", 3), ("kpis", "KPIs + OKRs", 3), ("sprint", "Current sprint", 2),
    ("sprints", "Last sprints", 2), ("decisions", "Decisions", 2), ("calendar", "Calendar", 4),
    ("live", "Live stream", 5), ("blog", "Blog and User Guide", 4), ("discussion", "Discussion", 5),
    ("projects", "Projects", 2),
]

# ---------- helpers ----------

def run(args, cwd=ROOT, timeout=60):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, str(e)

def git(*args, repo=ROOT):
    code, out = run(["git", "-C", str(repo), *args])
    return out if code == 0 else ""

def memo(key, ttl, fn):
    now = time.time()
    with LOCK:
        hit = MEMO.get(key)
        if hit and hit[0] > now:
            return hit[1]
    val = fn()
    with LOCK:
        MEMO[key] = (now + ttl, val)
    return val

def read(root, rel):
    p = root / rel
    try:
        return p.read_text()
    except (OSError, UnicodeDecodeError):
        return None

def events():
    p = ROOT / "private" / "ledger" / "events.ndjson"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            e = json.loads(line)
            out.append({"seq": e["seq"], "ts": e["ts"], "type": e["type"], "actor": e["actor"],
                        "summary": (e.get("data") or {}).get("summary", "") if isinstance(e.get("data"), dict) else ""})
        except (ValueError, KeyError):
            continue
    return out

def epoch(ts):
    """Seconds since 1970 for an ISO timestamp with offset or Z (naive = UTC)."""
    d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.timestamp()

# ---------- views (time travel) ----------

class View:
    """A folder holding the Collective's files as of some point, plus what it reflects."""
    def __init__(self, root, label, commit, event, kind):
        self.root, self.label, self.commit, self.event, self.kind = root, label, commit, event, kind

def live_view():
    head = git("rev-parse", "HEAD")
    ev = events()
    return View(ROOT, "live", head, ev[-1] if ev else None, "live")

def commit_view(sha):
    full = git("rev-parse", "--verify", f"{sha}^{{commit}}")
    if not full:
        raise ValueError(f"unknown commit {sha}")
    d = CACHE / f"commit-{full}"
    if not d.exists():
        tmp = CACHE / f"tmp-{full}"; tmp.mkdir(parents=True, exist_ok=True)
        a = subprocess.run(["git", "-C", str(ROOT), "archive", full], capture_output=True)
        if a.returncode != 0:
            raise ValueError("git archive failed")
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=a.stdout, check=True)
        tmp.rename(d)
    ts = epoch(git("show", "-s", "--format=%cI", full))
    ev = [e for e in events() if epoch(e["ts"]) <= ts]
    return View(d, f"commit {full[:7]}", full, ev[-1] if ev else None, "commit")

def event_view(seq):
    ev = events()
    match = [e for e in ev if e["seq"] == seq]
    if not match:
        raise ValueError(f"no event #{seq} (the log has {len(ev)} events)")
    d = CACHE / f"event-{seq}"
    if not d.exists():
        tmp = CACHE / f"tmp-event-{seq}"
        code, out = run([sys.executable, "agents/bin/replay.py", "build", "--out", str(tmp), "--to", str(seq)])
        if code != 0:
            raise ValueError("replay failed: " + out[-200:])
        tmp.rename(d)
    commit = git("rev-list", "-1", f"--before={int(epoch(match[0]['ts']))}", "HEAD")
    if not (d / "CHARTER.md").exists() and commit:
        # the log hadn't captured the files yet at this event: show that moment's commit
        c = commit_view(commit)
        return View(c.root, f"event #{seq} (files from commit {commit[:7]})", commit, match[0], "event")
    if not (d / "CHARTER.md").exists():
        raise ValueError(f"event #{seq} is earlier than the first recorded files; try a later event or a commit")
    return View(d, f"event #{seq}", commit, match[0], "event")

def date_view(when):
    # the page sends UTC ("...Z"); a bare date means the end of that day, UTC
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?", when):
        raise ValueError("date must be YYYY-MM-DD or an ISO time")
    stamp = when if "T" in when else when + "T23:59:59Z"
    t = epoch(stamp)
    ev = events()
    inside = [e for e in ev if epoch(e["ts"]) <= t]
    if ev and inside:          # the event log covers this moment: replay it exactly
        return event_view(inside[-1]["seq"])
    commit = git("rev-list", "-1", f"--before={int(t)}", "HEAD")
    if not commit:
        raise ValueError(f"nothing recorded before {when}")
    return commit_view(commit)

def resolve(at):
    at = (at or "live").strip()
    if at == "live":
        return live_view()
    kind, _, arg = at.partition(":")
    if kind == "commit" and re.fullmatch(r"[0-9a-fA-F]{4,40}", arg):
        return commit_view(arg)
    if kind == "event" and arg.isdigit():
        if PUBLIC:
            raise ValueError("event time travel reads the private event log; unavailable in public mode")
        return event_view(int(arg))
    if kind == "date":
        return date_view(arg)
    raise ValueError("at must be live, commit:<sha>, event:<n>, or date:<YYYY-MM-DD>")

# ---------- panels ----------

def charter_version(text):
    m = re.search(r"Charter version: ([\d.]+)", text or "")
    return m.group(1) if m else "?"

def header(v):
    ch = read(v.root, "CHARTER.md") or ""
    sprint = {"id": None, "phase": "no sprint yet", "theme": ""}
    metas = sorted((v.root / "sprints").glob("S-*/sprint.json"))
    if metas:
        try:
            m = json.loads(metas[-1].read_text())
            sprint = {"id": m.get("id"), "phase": m.get("phase"), "theme": m.get("theme", "")}
        except ValueError:
            pass
    ev = v.event if not PUBLIC else None
    return {"charter_version": charter_version(ch), "sprint": sprint,
            "stop": (v.root / "org" / "STOP").exists(),
            "paused": sorted(p.name.split("PAUSE-", 1)[1] for p in (v.root / "org").glob("PAUSE-*")),
            "as_of": {"label": v.label, "kind": v.kind, "commit": v.commit,
                      "event": ev["seq"] if ev else None, "event_ts": ev["ts"] if ev else None},
            "mode": "public" if PUBLIC else "private"}

def mission(v):
    text = read(v.root, "org/MISSION.md") or ""
    text = re.sub(r"^<!--.*?-->\n", "", text)
    last = git("log", "-1", "--format=%h|%cI|%s", "--", "org/MISSION.md") if v.kind == "live" else ""
    h, d, s = (last.split("|", 2) + ["", "", ""])[:3] if last else ("", "", "")
    return {"markdown": text, "source": "org/MISSION.md", "sources_note": "Library F1 (ETHDenver 2025 talk) and F2 (March 2025 update deck)",
            "last_change": {"commit": h, "date": d, "subject": s} if h else None}

ARTICLE = re.compile(r"^## (Article [\d.]+ — .+)$", re.M)
ENTRY = re.compile(r"^### (A-\d{4}) · v([\d.]+) · ([\d-]+) · Class (\w) · (.+)$", re.M)

def split_parts(text):
    i6 = [m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", text)]
    body = text[: i6[-1]] if i6 else text
    i5 = re.search(r"^# PART V — ", body, re.M)
    return body[: i5.start()] if i5 else body, text[i6[-1]:] if i6 else ""

def charter(v):
    text = read(v.root, "CHARTER.md") or ""
    parts, log = split_parts(text)
    entries = []
    for m in ENTRY.finditer(log):
        nxt = log.find("\n### ", m.end())
        seg = log[m.end(): nxt if nxt != -1 else len(log)]
        rat = re.search(r"^ratified_by: (.+)$", seg, re.M)
        vote = re.search(r"^vote: (.+)$", seg, re.M)
        entries.append({"id": m.group(1), "version": m.group(2), "date": m.group(3), "class": m.group(4),
                        "title": m.group(5), "ratified_by": rat.group(1) if rat else "",
                        "vote": vote.group(1) if vote else ""})
    timeline = []
    for line in (read(v.root, "charter/TIMELINE.md") or "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 9 and cells[0].startswith("v"):
            timeline.append(dict(zip(["version", "date", "amendment", "class", "change", "articles",
                                      "members", "plugins", "files"], cells)))
    versions = sorted((p.stem.split("-v", 1)[1] for p in (v.root / "charter" / "history").glob("CHARTER-v*.md")),
                      key=lambda s: tuple(int(x) for x in s.split(".")))
    verify = memo(("verify", str(v.root), v.commit), 15 if v.kind == "live" else 3600,
                  lambda: run([sys.executable, "agents/bin/charter-verify.py"], cwd=v.root))
    return {"version": charter_version(text), "parts_markdown": parts,
            "articles": ARTICLE.findall(parts), "amendments": entries, "timeline": timeline,
            "versions": versions,
            "verify": {"ok": verify[0] == 0, "summary": verify[1].splitlines()[-1] if verify[1] else ""}}

def charter_diff(v, a, b):
    if not all(re.fullmatch(r"v?\d+\.\d+\.\d+", x or "") for x in (a, b)):
        raise ValueError("versions look like 6.2.1")
    code, out = run([sys.executable, "agents/bin/charter.py", "diff", a.lstrip("v"), b.lstrip("v")], cwd=v.root)
    if code != 0:
        raise ValueError(out[-300:])
    return {"from": a, "to": b, "diff": out}

def check(name, args, cwd, private=False):
    if private and PUBLIC:
        return {"name": name, "status": "hidden", "detail": "private record (public mode)"}
    code, out = run(args, cwd=cwd)
    last = out.splitlines()[-1] if out else ""
    return {"name": name, "status": "ok" if code == 0 else "fail", "detail": last[:200]}

def versioning(v):
    live = v.kind == "live"
    priv = ROOT / "private"
    def repo(path, name, private):
        if private and PUBLIC:
            return {"name": name, "hidden": True}
        head = git("log", "-1", "--format=%h|%cI|%s", repo=path)
        h, d, s = (head.split("|", 2) + ["", "", ""])[:3]
        ahead = git("rev-list", "--count", "@{u}..HEAD", repo=path)
        return {"name": name, "head": h, "date": d, "subject": s,
                "ahead": int(ahead) if ahead.isdigit() else None, "hidden": False}
    repos = [repo(ROOT, "public · Verafyai/Collective", False), repo(priv, "private · Verafyai/CollectivePrivate", True)]
    if live:
        checks = memo(("checks",), 20, lambda: [
            check("Charter log (charter-verify.py)", [sys.executable, "agents/bin/charter-verify.py"], ROOT),
            check("Event log (eventlog.py verify)", [sys.executable, "agents/bin/eventlog.py", "verify"], ROOT, private=True),
            check("Edicts (edict.py check)", [sys.executable, "agents/bin/edict.py", "check"], ROOT, private=True),
            check("Case law (case.py check)", [sys.executable, "agents/bin/case.py", "check"], ROOT),
            check("Amendments (amendment.py check)", [sys.executable, "agents/bin/amendment.py", "check"], ROOT),
        ])
    else:
        checks = [check("Charter log (charter-verify.py), as of this point", [sys.executable, "agents/bin/charter-verify.py"], v.root),
                  {"name": "Event log, edicts, cases", "status": "n/a",
                   "detail": "verified on the live Collective; a past view is itself a verified replay"}]
    ev = [] if PUBLIC else events()
    backups = [e for e in ev if e["type"] == "ledger.backup"]
    commits = [dict(zip(["sha", "short", "date", "subject"], l.split("|", 3)))
               for l in git("log", "-60", "--format=%H|%h|%cI|%s").splitlines() if l.count("|") >= 3]
    return {"repos": repos, "checks": checks,
            "last_backup": backups[-1] if backups else None,
            "push_reminder": "Only the Steward pushes the public repo: agents/bin/repos.sh push --public",
            "travel": {"commits": commits,
                       "events": None if PUBLIC else {"count": len(ev), "first": ev[0] if ev else None,
                                                     "last": ev[-1] if ev else None}}}

def state(at):
    v = resolve(at)
    return {"header": header(v), "panels": [{"id": i, "title": t, "version": n} for i, t, n in PANELS],
            "mission": mission(v), "charter": charter(v), "versioning": versioning(v),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

def fingerprint():
    """Changes whenever the Collective's records change: public HEAD, private HEAD, last event, STOP."""
    parts = [git("rev-parse", "HEAD"), git("status", "--porcelain")]
    if not PUBLIC:
        parts += [git("rev-parse", "HEAD", repo=ROOT / "private"), read(ROOT, "private/ledger/HEAD.json") or ""]
    parts.append(str((ROOT / "org" / "STOP").exists()))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16]

# ---------- HTTP ----------

TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml"}

class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "CollectiveDashboard/1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def host_ok(self):
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return host in ("127.0.0.1", "localhost")

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                         "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.host_ok():
            return self.send(403, {"error": "the dashboard answers only on 127.0.0.1"})
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        try:
            if url.path == "/api/state":
                return self.send(200, state(q.get("at")))
            if url.path == "/api/charter-diff":
                return self.send(200, charter_diff(resolve(q.get("at")), q.get("from"), q.get("to")))
            if url.path == "/api/stream":
                return self.stream()
        except ValueError as e:
            return self.send(400, {"error": str(e)})
        if url.path in ("/", "/index.html"):
            return self.static("index.html")
        if url.path.startswith("/static/"):
            return self.static(url.path[len("/static/"):])
        return self.send(404, {"error": "not found"})

    def static(self, name):
        # only files that exist directly in dashboard/static, by exact name
        if "/" in name or name.startswith(".") or not re.fullmatch(r"[\w.-]+", name):
            return self.send(404, {"error": "not found"})
        p = STATIC / name
        if not p.is_file():
            return self.send(404, {"error": "not found"})
        return self.send(200, p.read_bytes(), TYPES.get(p.suffix, "application/octet-stream"))

    def stream(self):
        """Server-Sent Events: a 'changed' message whenever the records change (polled each second)."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        last = None
        try:
            while True:
                fp = fingerprint()
                if fp != last:
                    self.wfile.write(f"event: changed\ndata: {fp}\n\n".encode()); self.wfile.flush()
                    last = fp
                else:
                    self.wfile.write(b": keepalive\n\n"); self.wfile.flush()
                time.sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            return

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    global PUBLIC
    ap = argparse.ArgumentParser(description="The Collective Dashboard (local, read-only)")
    ap.add_argument("--public", action="store_true", help="hide everything from the private repo")
    ap.add_argument("--port", type=int, default=4848)
    ap.add_argument("--host", default=HOST)
    a = ap.parse_args()
    if a.host != HOST:
        sys.exit(f"REFUSED: the dashboard binds {HOST} only (Charter Article 18.5)")
    PUBLIC = a.public
    srv = Server((HOST, a.port), Handler)
    print(f"The Collective Dashboard · http://{HOST}:{a.port} · {'public' if PUBLIC else 'private'} mode · Ctrl-C to stop",
          flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
