#!/usr/bin/env python3
"""Agent permissions and ranks (Charter Article 3.9; the dashboard's Permissions tab, Article 18.7(e)).

A permission is granted or revoked only by the Steward: a checked box on the dashboard *is* the
Steward's ratification of that grant (Article 7.6). Each change is recorded as an edict and an
event, applied to the office's tools in agents/config.env, and flagged on the board for the
Scribe to record in the Charter (Part V, agents/config.example.env). The entrenched limits stay:
every public post still needs the Steward's approval (4.3), the public repo stays the Steward's
to push (17.4), the neutral officers never vote or supervise (3.7), and no rank adds a vote.

  perms.py show KEY                          what the agent may do, as JSON
  perms.py set KEY CAPABILITY on|off --steward
  perms.py rank KEY RANK [--group a,b,c] --steward
"""
import argparse, datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROSTER, CONFIG = ROOT / "agents/roster.json", ROOT / "agents/config.env"
NEUTRAL = {"scribe", "lawyer", "auditor"}          # Article 3.7: they record, advise, and audit; they never vote or supervise
RANKS = {"ic": "I.C.", "manager": "Manager", "gm": "General Manager", "bigboss": "Big Boss"}
CAPS = {  # capability: (label, tool it adds to the office's *_TOOLS, or None, limit shown to the Steward, available)
    "post_x":      ("Post to X", "Bash(agents/bin/x-post.sh:*)", "Posts only drafts you approved (Article 4.3).", True),
    "post_github": ("Post to GitHub", None, "Drafts issues and comments into the outbox; they go out only after your approval (4.3). The public repo stays yours to push (17.4).", True),
    "notify":      ("Send notifications", "Bash(agents/bin/notify.sh:*)", "Local notifications to you.", True),
    "vote":        ("Vote", None, "A vote in sprints and amendments (Articles 3.8, 14).", True),
    "email":       ("Send email", None, "Not available: no email tool exists. Agents never get your Gmail.", False),
    "telegram":    ("Post to Telegram", None, "Not available yet: Telegram is deferred (E-0039).", False),
    "sms":         ("Send text messages", None, "Not available: no messaging tool exists.", False),
}
SUPERVISE_TOOL = "Bash(python3 agents/bin/supervise.py:*)"

def load(): return json.loads(ROSTER.read_text())
def save(d): ROSTER.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
def find(d, key): return next((a for a in d["agents"] if a["key"] == key), None)

def run(*a): return subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True)

def record(key, what, words):
    """The Steward's dashboard action: an edict (his decision, in his words), an event, and a note for the Scribe."""
    r = run("agents/bin/edict.py", "new", "--title", f"Permissions: {what}", "--text", words,
            "--restatement", f"The Steward, on the dashboard's Permissions tab, {what}. A checked box is his ratification "
                             f"of the grant (Article 7.6); applied to agents/config.env and the roster.")
    eid = (re.search(r"issued (E-\d{4})", r.stdout) or [None, "E-?"])[1]
    run("agents/bin/eventlog.py", "record", "--actor", "steward", "--type", "agent.permission",
        "--data", json.dumps({"summary": f"{what} ({eid})", "agent": key}))
    b = ROOT / "org/board" / f"{datetime.date.today().isoformat()}-permissions.md"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with b.open("a") as f:
        f.write(("" if b.exists() and b.stat().st_size else "#decision\n") +
                f"\n### rex · {ts}\n{what[0].upper() + what[1:]} ({eid}, Article 3.9). @scribe please record it in the Charter (Part V, agents/config.example.env and agents/roster.json).\n")
    return eid

def tools_line(role):
    s = CONFIG.read_text(); m = re.search(rf'^{role.upper()}_TOOLS="(.*)"$', s, re.M)
    return s, m

def set_tool(role, tool, on):
    s, m = tools_line(role)
    if not m: return False                                  # Social has no *_TOOLS: its grants are recorded in the roster
    have = [t for t in split(m.group(1)) if t]
    if on and tool not in have: have.append(tool)
    if not on: have = [t for t in have if t != tool]
    CONFIG.write_text(s[:m.start(1)] + ",".join(have) + s[m.end(1):]); return True

def split(t):
    out, depth, cur = [], 0, ""
    for ch in t:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0: out.append(cur.strip()); cur = ""
        else: cur += ch
    return out + ([cur.strip()] if cur.strip() else [])

def show(key):
    d = load(); a = find(d, key) or sys.exit(f"REFUSED: no agent '{key}'")
    grants, rank = set(a.get("grants", [])), a.get("rank", "ic")
    caps = {}
    for c, (label, tool, limit, avail) in CAPS.items():
        on = a.get("votes", False) if c == "vote" else c in grants
        locked = (not avail) or (c == "vote" and key in NEUTRAL)
        why = limit if avail else limit
        if c == "vote" and key in NEUTRAL: why = "Locked: the Scribe, Lawyer, and Auditor stay neutral and never vote (Article 3.7)."
        caps[c] = {"label": label, "on": bool(on), "locked": locked, "available": avail, "note": why}
    sup = rank != "ic"
    caps["override"] = {"label": "Override agents", "on": sup, "locked": True, "available": True,
                        "note": "Comes with rank: pause, unpause, and reassign the tasks of agents it supervises. Never the neutral officers' work."}
    caps["supervise"] = {"label": "Supervise an agent group", "on": sup, "locked": True, "available": True,
                         "note": "Comes with rank: Manager (a group you pick), General Manager (every maker), Big Boss (every agent except the neutral officers)."}
    return {"key": key, "rank": rank, "rank_label": RANKS.get(rank, rank), "rank_locked": key in NEUTRAL,
            "supervises": scope(d, a), "group": a.get("supervises", []), "capabilities": caps, "ranks": RANKS}

def scope(d, a):
    rank = a.get("rank", "ic")
    active = [x for x in d["agents"] if x["status"] == "active" and x["key"] != a["key"]]
    if rank == "manager": return [k for k in a.get("supervises", []) if k not in NEUTRAL]
    if rank == "gm": return [x["key"] for x in active if x.get("class") != "officer"]
    if rank == "bigboss": return [x["key"] for x in active if x["key"] not in NEUTRAL]
    return []

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["show", "set", "rank"]); ap.add_argument("key")
    ap.add_argument("value", nargs="?"); ap.add_argument("state", nargs="?"); ap.add_argument("--group", default="")
    ap.add_argument("--steward", action="store_true")
    a = ap.parse_args()
    if a.cmd == "show": print(json.dumps(show(a.key), indent=1)); return
    if not a.steward: sys.exit("REFUSED: only the Steward grants or revokes permissions (Articles 4.6, 7.6)")
    d = load(); ag = find(d, a.key) or sys.exit(f"REFUSED: no agent '{a.key}'")
    if ag["status"] != "active": sys.exit(f"REFUSED: {a.key} is {ag['status']}")
    if a.cmd == "set":
        cap, on = a.value, a.state == "on"
        if cap not in CAPS or a.state not in ("on", "off"): sys.exit(f"REFUSED: usage: set KEY {{{','.join(CAPS)}}} on|off")
        label, tool, _, avail = CAPS[cap]
        if not avail: sys.exit(f"REFUSED: {label} isn't available: {CAPS[cap][2]}")
        if cap == "vote":
            if a.key in NEUTRAL: sys.exit("REFUSED: the neutral officers never vote (Article 3.7)")
            if not on and sum(1 for x in d["agents"] if x["status"] == "active" and x.get("votes")) - (1 if ag.get("votes") else 0) < 3:
                sys.exit("REFUSED: the Collective must keep at least three voting members (Article 3.6)")
            ag["votes"] = on
        else:
            g = set(ag.get("grants", [])); (g.add if on else g.discard)(cap); ag["grants"] = sorted(g)
            if tool: set_tool(a.key, tool, on)
        save(d)
        what = f"{'granted' if on else 'revoked'} {label.lower()} {'to' if on else 'from'} {ag['name']}"
        print(f"{what} ({record(a.key, what, f'[dashboard] {label}: {a.state} for {a.key}')})"); return
    if a.cmd == "rank":
        rank = a.value
        if rank not in RANKS: sys.exit(f"REFUSED: rank must be one of {', '.join(RANKS)}")
        if a.key in NEUTRAL and rank != "ic": sys.exit("REFUSED: the neutral officers don't supervise anyone (Article 3.7)")
        group = [k for k in a.group.split(",") if k]
        if rank == "manager":
            for k in group:
                t = find(d, k)
                if not t or t["status"] != "active" or k == a.key or k in NEUTRAL:
                    sys.exit(f"REFUSED: '{k}' can't be in {ag['name']}'s group (unknown, inactive, itself, or a neutral officer)")
        ag["rank"], ag["supervises"] = rank, (group if rank == "manager" else [])
        set_tool(a.key, SUPERVISE_TOOL, rank != "ic"); save(d)
        what = f"set {ag['name']}'s rank to {RANKS[rank]}" + (f", supervising {', '.join(group)}" if group else "")
        print(f"{what} ({record(a.key, what, f'[dashboard] rank: {rank} for {a.key}' + (f' (group: {a.group})' if group else ''))})")

if __name__ == "__main__":
    import pathlib, sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "observability")); from ops import run_cli   # Weave ops, best effort (P-005)
    run_cli(main, 'perms', only=('set', 'rank'))
