"""Tests for the Collective Dashboard, P-001 (Charter Articles 18 and 21).
Run: python3 tests/test_dashboard.py

Works on a scratch copy of the repo and starts the server on a free port.
Checks: every page and API endpoint, the floor's live feed, board posts showing
as speech, and the one allowed write (project comments) with its refusals.
"""
import json, pathlib, re, shutil, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
t = pathlib.Path(tempfile.mkdtemp()) / "c"
import atexit, os
atexit.register(shutil.rmtree, t.parent, True)   # leave nothing behind
os.environ["GIT_CONFIG_GLOBAL"] = str(t.parent / "gitconfig")   # never touch the Steward's ~/.gitconfig
shutil.copytree(ROOT, t, ignore=shutil.ignore_patterns(".git", "ledger", "logs", "pdfs", "__pycache__", "node_modules", ".env", "secrets", "*.key"))
if not (t / "agents/config.env").exists() and (t / "agents/config.example.env").exists():
    shutil.copy(t / "agents/config.example.env", t / "agents/config.env")
subprocess.run([sys.executable, "agents/bin/eventlog.py", "init", "--actor", "steward"], cwd=t, capture_output=True)
rid = subprocess.run([sys.executable, "agents/bin/eventlog.py", "run-start", "--actor", "researcher"], cwd=t, capture_output=True, text=True).stdout.strip()
(t / "org/board").mkdir(parents=True, exist_ok=True)
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
(t / "org/board" / f"{now[:10]}-standup.md").write_text(f"### researcher · {now}\nBriefing library paper 07 on weak judges.\n")
(t / "org/board" / f"{now[:10]}-selective-debate.md").write_text(
    f"#proposal\n### ideas · {now}\nDebate only where judges disagree.\n\n### lawyer · {now}\nCompliant; name the cheap baseline.\n\n### rex · {now}\nKeep the first run small.\n")
(t / "org/board" / f"{now[:10]}-note-to-self.md").write_text(f"### scribe · {now}\nA one-person thread is not a conversation.\n")

with socket.socket() as s:
    s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
srv = subprocess.Popen([sys.executable, "dashboard/server.py", "--port", str(port)], cwd=t, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = f"http://127.0.0.1:{port}"
def get(path):
    with urllib.request.urlopen(base + path, timeout=90) as r: return r.status, r.read().decode()
def post(path, body, headers=None):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode(), method="POST",   # as the browser sends it
                                 headers={"Content-Type": "application/json", "Origin": base, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())
try:
    for _ in range(50):
        try: get("/api/overview"); break
        except Exception: time.sleep(0.2)
    # pages: the floor is the primary view
    code, html = get("/"); assert code == 200 and "The Collective's floor" in html, "the floor must be the home page"
    assert "The Collective" in get("/scope")[1] and "control plane" in get("/scope")[1].lower()
    assert "Case law" in get("/records")[1]
    # every API endpoint answers with JSON
    for ep in ["overview", "live", "charter", "amendments", "cases", "projects", "sprints", "edicts", "events?after=0"]:
        code, body = get("/api/" + ep); assert code == 200, ep; json.loads(body)
    live = json.loads(get("/api/live")[1])
    assert {o["key"] for o in live["offices"]} == {"pm","scribe","lawyer","auditor","researcher","ideas","prototyper","media","social"}
    r = next(o for o in live["offices"] if o["key"] == "researcher")
    assert r["status"] == "working", r
    assert r["last"].startswith("Briefing library paper 07"), "the latest board post is what the agent 'says'"
    assert [s["stage"] for s in live["pipeline"]] == ["Papers", "Proposals", "Projects", "Demos", "Posts"]
    # the one write: a human comment on a project
    code, body = post("/api/projects/1/comment", {"author": "Test", "kind": "shout", "text": "hello there"})
    assert code == 400 and "kind" in body["error"], body
    code, body = post("/api/projects/1/comment", {"author": "Test", "kind": "input", "text": "hello there"}, {"Origin": "http://evil.example"})
    assert code == 403, body
    time.sleep(5.2)   # every attempt counts toward the one-per-5-seconds limit, refused ones included
    code, body = post("/api/projects/1/comment", {"author": "Test", "kind": "suggestion", "text": "Make the Record glow brighter."})
    assert code == 200 and body.get("ok"), body
    assert "### human:Test" in next((t / "projects").glob("001-*/discussion.md")).read_text()
    code, body = post("/api/projects/1/comment", {"author": "Test", "kind": "input", "text": "a second one, too fast"})
    assert code == 429, body
    # conversations: board threads with two or more participants, as group chats
    convs = json.loads(get("/api/conversations")[1])
    sd = next(c for c in convs if c["title"] == "Selective debate")
    assert sd["participants"] == ["ideas", "lawyer", "steward"] and sd["tag"] == "proposal" and sd["count"] == 3, sd
    assert not any(c["title"] == "Note to self" for c in convs), "one-person threads aren't conversations"
    chat = json.loads(get(f"/api/conversations/{sd['id']}")[1])
    assert [p["who"] for p in chat["posts"]] == ["ideas", "lawyer", "steward"]
    assert not any("genesis" in d["what"] for d in chat["doing"]), "bookkeeping stays out of chats"
    # one chat per project room (E-0091): only the agents in that room; the Collective-wide chat only in a huddle
    rooms = {c["room"]: c for c in json.loads(get("/api/conversations?by=room")[1])}
    seated = {}
    for a in json.loads((t / "agents/roster.json").read_text())["agents"]:
        if a["status"] == "active": seated.setdefault(a["room"], []).append(a["key"])
    for r, keys in seated.items():
        c = json.loads(get(f"/api/conversations/room-{r}")[1])
        assert sorted(c["members"]) == sorted(keys) and all(x["who"] in keys for x in c["posts"]), c
    assert all(c["id"] == f"room-{r}" for r, c in rooms.items()) and not any(c["tag"] == "huddle" for c in rooms.values())
    live0 = json.loads(get("/api/live")[1])
    assert live0["rooms"]["council"]["name"].startswith("Project "), "rooms carry project codenames (E-0088)"
    assert all("asleep" in o and "open_tasks" in o for o in live0["offices"]), "idle agents with no task sleep (E-0090)"
    try: get("/api/conversations/room-..%2Fx"); raise AssertionError("expected refusal")
    except urllib.error.HTTPError as e: assert e.code in (400, 404)
    try: get("/api/conversations/..%2Fsecrets"); raise AssertionError("expected refusal")
    except urllib.error.HTTPError as e: assert e.code in (400, 404)
    # agent bios, and the wizard's one action: drafting a membership motion
    code, body = get("/api/agents/lawyer/bio"); b = json.loads(body)
    assert code == 200 and b["class"] == "officer" and "Reads files" in b["modules"] and b["schedule"]["every_minutes"], b
    assert json.loads(get("/api/classes")[1])["classes"]["verifier"]["spawnable"] is True
    time.sleep(5.2)
    code, body = post("/api/agents/propose", {"class": "officer", "name": "Lawyer Two", "focus": "a second legal opinion"})
    assert code == 400 and "can't be spawned" in body["error"], body
    time.sleep(5.2)
    code, body = post("/api/agents/propose", {"class": "sentinel", "name": "Watch", "focus": "Re-check sources behind published verdicts daily"})
    assert code == 200 and "proposed Watch as A-" in body["message"], body
    ghost = next(a for a in json.loads(get("/api/live")[1])["roster"] if a["key"] == "watch")
    assert ghost["status"] == "proposed" and ghost["votes"] is False
    # unknown paths and writes are refused
    try: get("/api/nothing-here"); raise AssertionError("expected 404")
    except urllib.error.HTTPError as e: assert e.code == 404
    # fold-ins: local only (no DNS rebinding), the History view, and fonts served locally
    req = urllib.request.Request(base + "/api/live", headers={"Host": "evil.example"})
    try: urllib.request.urlopen(req, timeout=10); raise AssertionError("expected 403 for a foreign Host")
    except urllib.error.HTTPError as e: assert e.code == 403
    assert get("/history")[0] == 200 and get("/api/state?at=live")[0] == 200
    for page in ("/", "/scope", "/records"):
        assert "googleapis" not in get(page)[1], page + " must not load fonts from Google"
    assert get("/fonts/fonts.css")[0] == 200
    # version 003 writes (Articles 18.7(c)-(f), 18.8): allowed in private view, from this origin only
    time.sleep(1.1); code, body = post("/api/agents/media/move", {"room": "workshop"}); assert code == 200 and body["ok"], body
    code, body = post("/api/agents/media/move", {"room": "lab"}, {"Origin": "http://evil.example"}); assert code == 403, body
    conv = json.loads(get("/api/conversations")[1]); assert conv, "the standup thread is a conversation"
    code, body = post(f"/api/conversations/{conv[0]['id']}/comment", {"text": "Looks good."}); assert code == 200 and body["ok"], body
    assert "### rex ·" in (t / "org/board" / f"{conv[0]['id']}.md").read_text()
    perms = json.loads(get("/api/agents/lawyer/permissions")[1]); assert perms["capabilities"]["vote"]["locked"], perms
    code, body = post("/api/huddle", {"topic": "test"})
    assert (code == 403 and "A-0024" in body["error"]) or code == 200, body          # gated until the Charter allows huddles
    assert "summary" in json.loads(get(f"/api/conversations/{conv[0]['id']}")[1])["posts"][0]
    # new projects from the floor (E-0089): refused until A-0030, then a spec makes a project, a room, and a thread
    SPEC = "What is it? A tracker of claims we've checked. Who is it for? Readers. Version 001 lists ten checked claims with sources. " * 3
    ch = t / "CHARTER.md"; full = ch.read_text()
    if "\n### A-0030 · " not in full: full += "\n### A-0030 · v9.9.9 · test\nratified_by: test\n"
    ch.write_text(re.sub(r"\n### A-0030 · .*?(?=\n### |\Z)", "", full, flags=re.S))           # as if A-0030 weren't ratified yet
    code, body = post("/api/projects/new", {"codename": "Project Test", "spec": SPEC}); assert code == 403 and "A-0030" in body["error"], body
    assert subprocess.run([sys.executable, "agents/bin/rooms.py", "new", "--codename", "Project Early", "--spec", "x", "--steward"], cwd=t, capture_output=True).returncode, "rooms.py waits for A-0030 too"
    ch.write_text(full)                                                                     # A-0030 ratified again
    time.sleep(5.2); code, body = post("/api/projects/new", {"codename": "Project Test", "spec": "too short"}); assert code == 400, body
    time.sleep(5.2); code, body = post("/api/projects/new", {"codename": "Project Test", "name": "Claims tracker", "spec": SPEC, "spawn": ["scholar", "officer"]})
    assert code == 200 and body["ok"] and body["project"].startswith("P-"), body
    assert body["spawned"] == ["Test Scholar"] and body["spawn_failed"], body                  # agent types proposed with it (E-0096); offices aren't
    assert next(a for a in json.loads(get("/api/live")[1])["roster"] if a["key"] == "testscholar")["status"] == "proposed"
    room = body["room"]; rj = json.loads((t / "org/rooms.json").read_text())["rooms"][room]
    assert rj["name"] == "Project Test" and rj["project"] == body["project"] and rj["x"] >= 18, rj
    assert (t / "org/board" / f"project-{room}.md").exists() and "@pm" in (t / "org/board" / f"project-{room}.md").read_text()
    assert list((t / "projects").glob("*-test/spec.md")), "the project was created from the spec"
    time.sleep(1.1); code, body = post("/api/agents/researcher/move", {"room": room}); assert code == 200 and body["ok"], body
    assert "task" in body["message"], body
    assert "@researcher" in (t / "org/board" / f"project-{room}.md").read_text(), "the agent is told in the project's thread"
    assert any(x["office"] == "researcher" and body_p in x["title"] for x in json.loads(get("/api/tasks")[1]) for body_p in [rj["project"]]), "a task for the project"
    time.sleep(2.1); code, body = post(f"/api/rooms/{room}/rename", {"codename": "Project Lantern"}); assert code == 200, body
    assert json.loads(get("/api/live")[1])["rooms"][room]["name"] == "Project Lantern"
    time.sleep(2.1); code, body = post(f"/api/rooms/{room}/rename", {"codename": "lowercase <b>"}); assert code == 400, body
    # a write with no Origin (not from a page this server served) is refused
    req = urllib.request.Request(base + "/api/agents/media/move", data=b'{"room":"lab"}', method="POST", headers={"Content-Type": "application/json"})
    try: urllib.request.urlopen(req, timeout=10); raise AssertionError("expected 403 without an Origin")
    except urllib.error.HTTPError as e: assert e.code == 403
    print("dashboard tests passed")
finally:
    srv.terminate(); srv.wait(timeout=5)
