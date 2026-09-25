#!/usr/bin/env python3
"""Supervision within a rank's group (Charter Article 3.9).

  supervise.py pause KEY --by SUPERVISOR [--reason "..."]
  supervise.py unpause KEY --by SUPERVISOR

A supervisor may pause and unpause only the agents in its group (perms.py show SUPERVISOR). It can
never touch the neutral officers, itself, a pause the Steward set, or a retirement; `org/STOP` stays
the Steward's alone (Article 4.9). Every action is recorded as an event.
"""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/bin"))
import perms

MARK = "paused by supervisor "

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["pause", "unpause"]); ap.add_argument("key")
    ap.add_argument("--by", required=True); ap.add_argument("--reason", default="")
    a = ap.parse_args()
    d = perms.load(); boss = perms.find(d, a.by)
    if not boss or boss["status"] != "active": sys.exit(f"REFUSED: no active agent '{a.by}'")
    if a.key not in perms.scope(d, boss): sys.exit(f"REFUSED: {a.key} isn't in {a.by}'s group")
    f = ROOT / "org" / f"PAUSE-{a.key}"
    if a.cmd == "pause":
        if f.exists(): print(f"{a.key} is already paused"); return
        f.write_text(f"{MARK}{a.by}: {a.reason}\n")
    else:
        if not f.exists(): print(f"{a.key} isn't paused"); return
        if not f.read_text().startswith(MARK): sys.exit("REFUSED: this pause was set by the Steward or a retirement; only the Steward removes it")
        f.unlink()
    subprocess.run([sys.executable, str(ROOT / "agents/bin/eventlog.py"), "record", "--actor", a.by, "--type", f"agent.{a.cmd}d",
                    "--data", json.dumps({"summary": f"{a.by} {a.cmd}d {a.key}" + (f": {a.reason}" if a.reason else ""), "agent": a.key})],
                   capture_output=True)
    print(f"{a.cmd}d {a.key}")

if __name__ == "__main__":
    main()
