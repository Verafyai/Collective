#!/usr/bin/env python3
"""Project rooms (edicts E-0088, E-0089): every room on the floor is a project, with a codename.

  rooms.py list                                    the rooms, their codenames and projects
  rooms.py new --codename "Project X" --name N --spec FILE --steward
                                                   a new project from the Steward's spec, in a new room
  rooms.py assign KEY ROOM                         an agent seated in a project room works on that project
  rooms.py rename ROOM --codename "Project Y" --steward

`new` creates the project with `projects.py new --spec` (owner: the Project Manager), gives it the next free
room on the floor, and opens its #project board thread addressed to the Project Manager and the Lawyer.
`assign` (run after `spawn.py move`) gives the agent one tsk task for the project, unless it already has an
open one, and posts in the project's thread, so the agent picks it up on its next run and talks there.
Every change is recorded as an event. Rooms live in org/rooms.json (public).
"""
import argparse, datetime, json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROOMS_F, ROSTER = ROOT / "org/rooms.json", ROOT / "agents/roster.json"
BASE = ("council", "lab", "studio", "workshop")          # the four original rooms, drawn by the floor itself
# where new rooms go: a ring outside the first four, each 6x6 with a 6-tile street between
SLOTS = [(24, 0), (24, 12), (0, 24), (12, 24), (24, 24), (36, 0), (36, 12), (36, 24), (0, 36), (12, 36), (24, 36), (36, 36)]
PALETTE = [("#23404A", "#346070"), ("#40302A", "#634A3E"), ("#2C3A26", "#465C3C"), ("#3D2438", "#5E3957"),
           ("#27304A", "#3C4A70"), ("#433A1F", "#665A30")]
CODENAME_RE = re.compile(r"^Project [A-Z][A-Za-z' -]{1,30}$")

def ratified(aid):
    """True only if the Charter's amendment log (Part VI, hash-chained) holds aid with a ratified_by line.
    A gate must read what only ratification writes, never a string the gated code itself contains."""
    try: text = (ROOT / "CHARTER.md").read_text()
    except OSError: return False
    heads = [m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", text)]
    if not heads: return False
    m = re.search(r"^### " + re.escape(aid) + r" · .*?(?=^### |\Z)", text[heads[-1]:], re.S | re.M)
    return bool(m and re.search(r"^ratified_by: \S", m.group(0), re.M))
GATE = "A-0030"                                           # projects on the floor (Charter Article 18.7(i), (j))

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def load():
    try: return json.loads(ROOMS_F.read_text())
    except (OSError, ValueError): return {"rooms": {}}
def save(d): ROOMS_F.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
def event(t, data):
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", data.pop("_actor", "steward"),
                    "--type", t, "--data", json.dumps(data)], capture_output=True)
def room_keys(): return list(BASE) + [k for k in load()["rooms"] if k not in BASE]
def thread_path(room): return ROOT / "org/board" / f"project-{room}.md"

def post(room, who, text):
    p = thread_path(room); d = load()["rooms"].get(room, {})
    if not p.exists(): p.write_text(f"#project\n")
    with p.open("a") as f: f.write(f"\n### {who} · {now()}\n{text}\n")

def tsk(*args):
    env = {**os.environ, "TSK_STATE_DIR": str(ROOT / "org/tasks"), "TSK_NO_UPDATE_CHECK": "1"}
    return subprocess.run(["tsk", *args, "--state-dir", str(ROOT / "org/tasks")], capture_output=True, text=True, env=env, cwd=ROOT)

def cmd_new(a):
    if not a.steward: sys.exit("REFUSED: only the Steward creates projects from the floor (--steward)")
    code = " ".join(a.codename.split())
    if not code.startswith("Project "): code = "Project " + code
    if not CODENAME_RE.match(code): sys.exit("REFUSED: a codename is 'Project ' plus a capitalized word or two (letters, spaces, hyphens)")
    d = load()
    if any(r.get("name", "").lower() == code.lower() for r in d["rooms"].values()): sys.exit(f"REFUSED: {code} already exists")
    used = {(r.get("x"), r.get("y")) for r in d["rooms"].values()}
    slot = next((s for s in SLOTS if s not in used), None)
    if not slot: sys.exit("REFUSED: the floor has no free room left")
    name = " ".join((a.name or code).split())[:80]
    slug = re.sub(r"[^a-z0-9]+", "-", code.lower().replace("project ", "")).strip("-") or "project"
    r = subprocess.run([sys.executable, str(ROOT / "agents/bin/projects.py"), "new", "--name", name, "--slug", slug, "--owner", "pm", "--spec", a.spec],
                       capture_output=True, text=True, cwd=ROOT)
    m = re.search(r"created (P-\d{3})", r.stdout)
    if r.returncode or not m: sys.exit((r.stdout + r.stderr).strip() or "REFUSED: the project couldn't be created")
    pid = m.group(1)
    key = slug.replace("-", "")[:16] or f"room{len(d['rooms']) + 1}"
    if not re.fullmatch(r"[a-z][a-z0-9]{1,15}", key) or key in d["rooms"] or key in BASE: key = f"room{len(d['rooms']) + 1}"
    floor, edge = PALETTE[len([k for k in d["rooms"] if k not in BASE]) % len(PALETTE)]
    about = " ".join(pathlib.Path(a.spec).read_text().split())[:120]
    d["rooms"][key] = {"name": code, "project": pid, "about": about, "x": slot[0], "y": slot[1], "w": 6, "d": 6, "floor": floor, "edge": edge,
                       "created": now()}
    save(d)
    post(key, "rex", f"{code} ({pid}) starts here: {name}. The spec is in projects/ ({pid}/spec.md).\n\n"
                     f"@pm: this is the Steward's own spec (Article 21.2); plan version 001 and assign the work. @lawyer: your opinion on the spec, please.\n"
                     f"Anyone seated in this room works on {code}: take your task, then post progress here.")
    event("project.room", {"summary": f"{code} ({pid}) opened in a new room", "room": key, "project": pid})
    print(json.dumps({"room": key, "project": pid, "codename": code}))

def cmd_assign(a):
    d = load(); room = d["rooms"].get(a.room)
    if not room or not room.get("project"): print(f"{a.room} has no project; nothing to assign"); return
    try: ag = next(x for x in json.loads(ROSTER.read_text())["agents"] if x["key"] == a.key)
    except (StopIteration, OSError, ValueError): sys.exit(f"REFUSED: no agent '{a.key}'")
    if ag["status"] != "active": sys.exit(f"REFUSED: {a.key} is {ag['status']}")
    pid, code = room["project"], room["name"]
    listing = tsk("list", "--json", "--thread", a.key, "--all")
    try: mine = json.loads(listing.stdout or "[]")
    except ValueError: mine = []
    if isinstance(mine, dict): mine = mine.get("tasks", [])
    have = [t for t in mine if pid in (t.get("title") or "") and t.get("status") != "done"]
    if have: print(f"{a.key} already has T{have[0].get('number')} for {pid}")
    else:
        r = tsk("add", "-t", f"{pid} {code}: your part", "-n", f"Seated in {code} by the Steward. Read projects/*/spec.md for {pid}, "
                f"agree your part with the Project Manager in org/board/project-{a.room}.md, then do it and post progress there.",
                "--thread", a.key, "--json")
        if r.returncode: sys.exit("REFUSED: the task couldn't be created: " + (r.stderr or r.stdout)[-200:])
        print(f"gave {a.key} a task for {pid}")
    post(a.room, "rex", f"@{a.key}: you're on {code} ({pid}) now. Pick up your task, say here what you'll do first, and keep the room posted.")
    event("project.assigned", {"summary": f"{ag['name']} assigned to {code} ({pid})", "agent": a.key, "room": a.room, "project": pid})

def cmd_rename(a):
    if not a.steward: sys.exit("REFUSED: only the Steward renames rooms (--steward)")
    code = " ".join(a.codename.split())
    if not code.startswith("Project "): code = "Project " + code
    if not CODENAME_RE.match(code): sys.exit("REFUSED: a codename is 'Project ' plus a capitalized word or two")
    d = load()
    if a.room not in d["rooms"]: sys.exit(f"REFUSED: no room '{a.room}'")
    old = d["rooms"][a.room].get("name", a.room); d["rooms"][a.room]["name"] = code; save(d)
    event("project.renamed", {"summary": f"{old} renamed {code}", "room": a.room})
    print(f"{old} -> {code}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["list", "new", "assign", "rename"]); ap.add_argument("args", nargs="*")
    for o in ("codename", "name", "spec"): ap.add_argument(f"--{o}")
    ap.add_argument("--steward", action="store_true")
    a = ap.parse_args()
    if a.cmd != "list" and not ratified(GATE): sys.exit(f"REFUSED: project rooms wait for the Steward's ratification of {GATE}")
    if a.cmd == "list":
        for k in room_keys():
            r = load()["rooms"].get(k, {}); print(f"{k:<12} {r.get('name', '-'):<24} {r.get('project', '')}")
    elif a.cmd == "new":
        if not (a.codename and a.spec): sys.exit("REFUSED: --codename and --spec are required")
        cmd_new(a)
    elif a.cmd == "assign":
        if len(a.args) != 2: sys.exit("usage: rooms.py assign KEY ROOM")
        a.key, a.room = a.args; cmd_assign(a)
    else:
        if len(a.args) != 1 or not a.codename: sys.exit("usage: rooms.py rename ROOM --codename 'Project Y' --steward")
        a.room = a.args[0]; cmd_rename(a)

if __name__ == "__main__":
    main()
