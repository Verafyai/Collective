#!/usr/bin/env python3
"""Deterministic amendment tally (Charter Article 7.5, 7.6, 11). No model involved.

Usage: gov-tally.py governance/records/A-NNNN
Reads  <dir>/amendment.json  {"id","class":"A|B|C|M","frozen_sha256","members":[...],
                             "affects_privileges": bool, "subject": role (class M only)}
       Class M = membership (Article 3.6, P11): add or remove an agent or worker by simple
       majority; the agent being removed ("subject") doesn't vote on itself.
       <dir>/ballots/<member>.md  first lines:  vote: yes|no|abstain
                                                self_interest: yes|no
                                                reason: <text, <=100 words>
Writes <dir>/tally.json and <dir>/tally.md, prints the result.
"""
import json, re, sys, pathlib

def parse_ballot(text):
    f = {}
    for line in text.splitlines():
        m = re.match(r"^(vote|self_interest|reason|frozen_sha256)\s*:\s*(.*)$", line.strip(), re.I)
        if m: f[m.group(1).lower()] = m.group(2).strip()
    return f

def tally(d):
    d = pathlib.Path(d)
    meta = json.loads((d / "amendment.json").read_text())
    cls, members = meta["class"].upper(), [m for m in meta["members"] if not (meta["class"].upper() == "M" and m == meta.get("subject"))]
    votes, problems = {}, []
    for m in members:
        p = d / "ballots" / f"{m}.md"
        if not p.exists():
            continue
        b = parse_ballot(p.read_text())
        v = b.get("vote", "").lower()
        if v not in ("yes", "no", "abstain"):
            problems.append(f"{m}: invalid vote '{v}' (ballot void)"); continue
        if b.get("frozen_sha256") and b["frozen_sha256"] != meta["frozen_sha256"]:
            problems.append(f"{m}: ballot is for different text (void)"); continue
        if len(b.get("reason", "").split()) > 100:
            problems.append(f"{m}: reason over 100 words (counted, flagged)")
        votes[m] = {"vote": v, "self_interest": b.get("self_interest", "no").lower() == "yes"}
    cast = len(votes)
    yes = sum(1 for v in votes.values() if v["vote"] == "yes")
    no = sum(1 for v in votes.values() if v["vote"] == "no")
    abstain = cast - yes - no
    quorum = cast * 3 >= len(members) * 2          # two-thirds of unpaused members
    decided = yes + no
    if cls == "A":
        outcome, needs_steward = "advisory", True
    elif not quorum:
        outcome, needs_steward = "failed_quorum", False
    elif cls == "B":
        outcome = "passed" if decided and yes * 3 >= decided * 2 else "rejected"
        needs_steward = outcome == "passed"
    else:  # C, and M (membership, Article 3.6): simple majority of votes cast
        outcome = "passed" if yes > no else "rejected"
        needs_steward = False
    if cls == "M" and outcome == "passed" and meta.get("remaining_voters", 99) < 3:
        outcome, needs_steward = "blocked_minimum_membership", False   # always keep the Clerk + 3 voters
    if outcome == "passed" and meta.get("affects_privileges"):
        needs_steward = True                        # Article 7.6, any class
    res = {"id": meta["id"], "class": cls, "frozen_sha256": meta["frozen_sha256"],
           "members": members, "cast": cast, "yes": yes, "no": no, "abstain": abstain,
           "quorum_met": quorum, "outcome": outcome,
           "steward_ratification_required": needs_steward,
           "steward_veto_window_hours": 72 if (cls == "C" and outcome == "passed" and not needs_steward) else 0,
           "votes": votes, "problems": problems}
    (d / "tally.json").write_text(json.dumps(res, indent=2))
    lines = [f"# Tally {res['id']} (Class {cls})", "",
             f"- Text hash: `{res['frozen_sha256']}`",
             f"- Ballots: {cast}/{len(members)} · yes {yes} · no {no} · abstain {abstain}",
             f"- Quorum (2/3): {'met' if quorum else 'NOT met'}",
             f"- Outcome: **{outcome}**",
             f"- Steward ratification required: {'yes' if needs_steward else 'no'}", ""]
    lines += [f"| {m} | {v['vote']} | {'yes' if v['self_interest'] else ''} |" for m, v in sorted(votes.items())]
    if votes: lines[len(lines)-len(votes):len(lines)-len(votes)] = ["| Member | Vote | Self-interest |", "|---|---|---|"]
    if problems: lines += ["", "Problems:"] + [f"- {p}" for p in problems]
    (d / "tally.md").write_text("\n".join(lines) + "\n")
    return res

if __name__ == "__main__":
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "observability")); from ops import op   # Weave ops, best effort (P-005)
    tally = op("governance.count_votes")(tally)
    r = tally(sys.argv[1]); print(json.dumps({k: r[k] for k in ("id","outcome","yes","no","abstain","quorum_met","steward_ratification_required")}))
