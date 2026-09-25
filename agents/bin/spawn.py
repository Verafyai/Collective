#!/usr/bin/env python3
"""Spawn, clone, and retire agents (Charter Articles 3.6, 3.8; P11).

An agent is never created directly. Proposing one drafts a membership motion
(an amendment of Class M) carrying its full configuration. The new agent
appears in the roster as "proposed" (a ghost on the floor) until the motion
passes; then `activate` brings it to life. It starts with base tools only;
its class's extra tools wait for the Steward's ratification (Article 7.6),
and it doesn't vote unless a Class B amendment grants it.

  spawn.py classes                              the character classes
  spawn.py propose --class C --name N --focus "..." [--key K] [--room R]
                   [--interval SECONDS] [--cap RUNS] [--model M] [--proposer WHO]
  spawn.py clone SOURCE --name N --focus "..." [...]   same, starting from an existing agent
  spawn.py activate KEY                         after the motion passes: create the agent
  spawn.py retire KEY [--reason "..."]          propose retiring an agent (a membership motion)
  spawn.py retire-apply KEY                     after that motion passes: retire it
  spawn.py move KEY --room ROOM                move an agent to another room (cosmetic; Article 18.7(c))
  spawn.py list | bio KEY
"""
import argparse, datetime, json, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROSTER, CLASSES = ROOT / "agents/roster.json", ROOT / "agents/classes.json"
KEY_RE = re.compile(r"^[a-z][a-z0-9]{1,15}$")
RESERVED = {"steward", "system", "human", "external", "common", "bin", "chief"}
ROOMS = {"council", "lab", "studio", "workshop"}

def load(p): return json.loads(p.read_text())
def save(p, d): p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
def agents(): return load(ROSTER)["agents"]
def find(key): return next((a for a in agents() if a["key"] == key), None)

def event(etype, data, actor="steward"):
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", actor,
                    "--type", etype, "--data", json.dumps(data)], capture_output=True)

def amendment_status(aid):
    p = ROOT / "amendments" / f"amendment-{int(aid.split('-')[1]):03d}.md"
    if not p.exists(): return None
    m = re.search(r"^status: (\w+)", p.read_text(), re.M)
    return m.group(1) if m else None

def config_value(key, var):
    for f in ("agents/config.env", "agents/config.example.env"):
        m = re.search(rf'^{key.upper()}_{var}=["\']?([^"\'\n]*)', (ROOT / f).read_text() if (ROOT / f).exists() else "", re.M)
        if m: return m.group(1)
    return None

def propose(a, clone_of=None):
    cl = load(CLASSES); classes = cl["classes"]
    if clone_of:
        src = find(clone_of) or sys.exit(f"REFUSED: no agent '{clone_of}'")
        a.cls = a.cls or src["class"]; a.room = a.room or src["room"]
    if a.cls not in classes: sys.exit(f"REFUSED: unknown class '{a.cls}'. Classes: {', '.join(classes)}")
    c = classes[a.cls]
    if not c.get("spawnable"): sys.exit(f"REFUSED: {c['name']} can't be spawned. {c['about']}")
    name = (a.name or "").strip()
    if not (2 <= len(name) <= 30) or not re.match(r"^[\w .'-]+$", name): sys.exit("REFUSED: a name of 2 to 30 letters, numbers, spaces, or . ' -")
    key = a.key or re.sub(r"[^a-z0-9]", "", name.lower())[:16]
    if not KEY_RE.match(key) or key in RESERVED: sys.exit(f"REFUSED: '{key}' can't be used as an agent key (2–16 lowercase letters or digits, starting with a letter)")
    if find(key) or (ROOT / "agents" / key).exists(): sys.exit(f"REFUSED: an agent '{key}' already exists or is proposed")
    focus = (a.focus or "").strip()
    if not (10 <= len(focus) <= 300): sys.exit("REFUSED: describe the agent's focus in 10 to 300 characters")
    room = a.room or c["room"]
    if room not in ROOMS: sys.exit(f"REFUSED: room must be one of {', '.join(sorted(ROOMS))}")
    interval = int(a.interval or c["interval"]); cap = int(a.cap or c["cap"])
    if not (600 <= interval <= 86400): sys.exit("REFUSED: interval must be 10 minutes to 24 hours")
    if not (1 <= cap <= 96): sys.exit("REFUSED: daily cap must be 1 to 96 runs")
    same = [x for x in agents() if x["class"] == a.cls]
    color = c["palette"][len(same) % len(c["palette"])]
    role = c["role"].format(name=name, focus=focus, key=key)
    spec = {"key": key, "name": name, "class": a.cls, "room": room, "focus": focus, "interval": interval, "cap": cap,
            "model": a.model or "default", "base_tools": cl["base_tools"], "requested_tools": c.get("requested", ""),
            "votes": False, "clone_of": clone_of, "color": color, "icon": c["icon"]}
    text = (f"Add a new agent, **{name}** (`{key}`), of class **{c['name']}**"
            + (f", cloned from `{clone_of}`" if clone_of else "") + f".\n\n**Focus:** {focus}\n\n"
            f"**Room:** {room}. **Schedule:** a run every {interval // 60} minutes, at most {cap} runs a day.\n\n"
            f"**Tools:** base tools only (read, search case law, post to the board). Its class requests "
            f"`{spec['requested_tools'] or 'nothing more'}`, which applies only if the Steward ratifies it (Article 7.6).\n\n"
            f"**Votes:** no (a vote needs a separate Class B amendment ratified by the Steward).\n\n"
            f"**Prompt (agents/{key}/ROLE.md):**\n\n" + "\n".join("> " + l for l in role.splitlines()) +
            f"\n\n**Full configuration:**\n\n```json\n{json.dumps(spec, indent=1, ensure_ascii=False)}\n```")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f: f.write(text)
    r = subprocess.run([sys.executable, str(ROOT / "agents/bin/amendment.py"), "new", "--title", f"Spawn {name} ({c['name']})",
                        "--class", "M", "--proposer", a.proposer or "steward", "--file", f.name], capture_output=True, text=True)
    m = re.search(r"\(A-(\d{4})", r.stdout)
    if not m: sys.exit(f"REFUSED: couldn't create the membership motion: {r.stdout}{r.stderr}")
    aid = f"A-{m.group(1)}"
    prop = ROOT / "agents" / "_proposed" / key; prop.mkdir(parents=True, exist_ok=True)
    (prop / "ROLE.md").write_text(f"# {name} ({c['name']})\n\n{role}\n"); save(prop / "agent.json", spec)
    roster = load(ROSTER)
    roster["agents"].append({"key": key, "name": name, "class": a.cls, "room": room, "color": color, "icon": c["icon"],
                             "votes": False, "status": "proposed", "motion": aid, "motto": focus[:90], "clone_of": clone_of})
    save(ROSTER, roster)
    event("agent.proposed", {"summary": f"{name} ({c['name']}) proposed as {aid}", "agent": key, "amendment": aid}, a.proposer or "steward")
    print(f"proposed {name} as {aid} (amendment-{int(m.group(1)):03d}.md). It appears as a ghost until the Collective votes.")

def activate(key):
    ag = find(key) or sys.exit(f"REFUSED: no agent '{key}'")
    if ag["status"] != "proposed": sys.exit(f"REFUSED: {key} is {ag['status']}, not proposed")
    st = amendment_status(ag["motion"])
    if st not in ("passed", "ratified"): sys.exit(f"REFUSED: its membership motion {ag['motion']} is '{st}'. It must pass first (Article 3.6)")
    spec = load(ROOT / "agents/_proposed" / key / "agent.json")
    (ROOT / "agents" / key).mkdir(exist_ok=True)
    (ROOT / "agents" / key / "ROLE.md").write_text((ROOT / "agents/_proposed" / key / "ROLE.md").read_text())
    K = key.upper()
    lines = f"\n# {spec['name']} ({spec['class']}), spawned by {ag['motion']}\n{K}_INTERVAL={spec['interval']}\n{K}_MAX_RUNS={spec['cap']}\n{K}_TOOLS=\"{spec['base_tools']}\"\n# requested, awaiting the Steward's ratification (Article 7.6): {spec['requested_tools']}\n"
    for f in ("agents/config.example.env", "agents/config.env"):
        p = ROOT / f
        if p.exists() and f"{K}_TOOLS=" not in p.read_text(): p.write_text(p.read_text().rstrip() + "\n" + lines)
    t = ROOT / "herdr/projects/collective.toml"
    if t.exists() and f'name = "{key}"' not in t.read_text():
        t.write_text(t.read_text().rstrip() + f'\n\n[[tabs]]\nname = "{key}"\ncommand = "agents/bin/run-role.sh {key} --loop"\n')
    roster = load(ROSTER)
    for x in roster["agents"]:
        if x["key"] == key: x["status"] = "active"; x["activated"] = datetime.date.today().isoformat()
    save(ROSTER, roster)
    event("agent.spawned", {"summary": f"{spec['name']} joined the Collective ({ag['motion']})", "agent": key})
    print(f"{spec['name']} is active: agents/{key}/ROLE.md, config, and a herdr tab created.\n"
          f"Next: the Scribe records the membership change in the Charter (Article 7.7), and the Steward decides on its requested tools.")

def retire(key, reason, proposer):
    ag = find(key) or sys.exit(f"REFUSED: no agent '{key}'")
    if ag["class"] == "officer": sys.exit("REFUSED: officers can't be retired this way; an office changes only by Charter amendment (Article 3.7)")
    if ag["status"] != "active": sys.exit(f"REFUSED: {key} is {ag['status']}")
    voters_after = sum(1 for x in agents() if x["status"] == "active" and x["votes"] and x["key"] != key)
    if ag["votes"] and voters_after < 3: sys.exit("REFUSED: the Collective must keep at least three voting members (Article 3.6)")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(f"Retire **{ag['name']}** (`{key}`). Reason: {reason or '(the proposer gives a reason)'}\n\nIts files and history are kept; it stops running.\n\n"
                f"The subject doesn't vote on its own retirement (Article 3.6); tally with gov-tally.py class M and subject `{key}`.")
    r = subprocess.run([sys.executable, str(ROOT / "agents/bin/amendment.py"), "new", "--title", f"Retire {ag['name']}", "--class", "M",
                        "--proposer", proposer or "steward", "--file", f.name], capture_output=True, text=True)
    m = re.search(r"\(A-(\d{4})", r.stdout) or sys.exit(f"REFUSED: {r.stdout}{r.stderr}")
    roster = load(ROSTER)
    for x in roster["agents"]:
        if x["key"] == key: x["retire_motion"] = f"A-{m.group(1)}"
    save(ROSTER, roster)
    event("agent.retire_proposed", {"summary": f"Retiring {ag['name']} proposed as A-{m.group(1)}", "agent": key})
    print(f"proposed retiring {ag['name']} as A-{m.group(1)}")

def retire_apply(key):
    ag = find(key) or sys.exit(f"REFUSED: no agent '{key}'")
    st = amendment_status(ag.get("retire_motion", "A-9999"))
    if st not in ("passed", "ratified"): sys.exit(f"REFUSED: the retirement motion is '{st}'")
    (ROOT / "org" / f"PAUSE-{key}").write_text(f"retired by {ag['retire_motion']}\n")
    roster = load(ROSTER)
    for x in roster["agents"]:
        if x["key"] == key: x["status"] = "retired"
    save(ROSTER, roster)
    event("agent.retired", {"summary": f"{ag['name']} retired ({ag['retire_motion']})", "agent": key})
    print(f"{ag['name']} retired; its history is kept.")

def move(key, room):
    """Seat an agent in another room. Cosmetic: no powers, vote, tools, or schedule change (Article 18.7(c))."""
    if room not in ROOMS: sys.exit(f"REFUSED: room must be one of {', '.join(sorted(ROOMS))}")
    ag = find(key) or sys.exit(f"REFUSED: no agent '{key}'")
    if ag["status"] == "retired": sys.exit(f"REFUSED: {key} is retired")
    if ag.get("room") == room: print(f"{key} is already in the {room}"); return
    roster = load(ROSTER); old = ag.get("room", "")
    for x in roster["agents"]:
        if x["key"] == key: x["room"] = room
    save(ROSTER, roster)
    event("agent.moved", {"summary": f"{ag['name']} moved from the {old or '?'} to the {room}", "agent": key, "from": old, "to": room})
    print(f"moved {key}: {old or '?'} -> {room}")

def bio(key):
    ag = find(key) or sys.exit(f"no agent '{key}'")
    role = ROOT / "agents" / key / "ROLE.md"
    if not role.exists(): role = ROOT / "agents/_proposed" / key / "ROLE.md"
    return {**ag, "interval": config_value(key, "INTERVAL"), "cap": config_value(key, "MAX_RUNS"),
            "tools": config_value(key, "TOOLS"), "model": config_value(key, "MODEL") or "default",
            "prompt": role.read_text() if role.exists() else ""}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["classes", "propose", "clone", "activate", "retire", "retire-apply", "move", "list", "bio"])
    ap.add_argument("arg", nargs="?"); ap.add_argument("--class", dest="cls"); ap.add_argument("--name"); ap.add_argument("--focus")
    ap.add_argument("--key"); ap.add_argument("--room"); ap.add_argument("--interval"); ap.add_argument("--cap"); ap.add_argument("--model")
    ap.add_argument("--proposer"); ap.add_argument("--reason")
    a = ap.parse_args()
    if a.cmd == "classes":
        for k, c in load(CLASSES)["classes"].items(): print(f"{k:<9} {'spawnable' if c.get('spawnable') else 'office   '}  {c['name']}: {c['about']}")
    elif a.cmd == "propose": propose(a)
    elif a.cmd == "clone": propose(a, clone_of=a.arg)
    elif a.cmd == "activate": activate(a.arg)
    elif a.cmd == "retire": retire(a.arg, a.reason, a.proposer)
    elif a.cmd == "retire-apply": retire_apply(a.arg)
    elif a.cmd == "move": move(a.arg, a.room)
    elif a.cmd == "list":
        for x in agents(): print(f"{x['key']:<12} {x['status']:<9} {x['class']:<9} {'votes' if x['votes'] else '     '}  {x['name']}")
    elif a.cmd == "bio": print(json.dumps(bio(a.arg), indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
