#!/usr/bin/env python3
"""The Court's certainty score (P-006; court/certainty.json). Deterministic: it reads only the case's events from the
Record, so recomputing it from the log always gives the same number.

  python3 court/certainty.py C-0012        print the breakdown recomputed from the event log
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "court/certainty.json").read_text())

def band(score):
    return next(b for b in CFG["bands"] if b["min"] <= score <= b["max"])

def compute(events, holding=None, judge_confidence=None):
    """events: the case's court events in log order. holding: the position the score is for (default: the Judge's)."""
    exhibits = {e["data"]["exhibit"]: e["data"] for e in events if e["type"] == "exhibit.admitted"}
    struck = {e["data"]["claim"] for e in events if e["type"] == "objection" and e["data"].get("ruling") == "sustained"}
    ruling = next((e["data"] for e in events if e["type"] == "judge.ruling"), {})
    holding = holding or ruling.get("holding")
    rebutted = set(ruling.get("rebutted_claims") or [])
    claims = [c for e in events if e["type"] == "argument" and e["data"].get("position") == holding for c in e["data"].get("claims", [])]
    surviving = [c for c in claims if c["id"] not in struck and c["id"] not in rebutted]
    # evidence strength: the admitted exhibits the prevailing side's surviving claims rest on
    cited = sorted({x for c in surviving for x in c.get("cites", []) if x in exhibits})
    if cited:
        rel = sum(float(exhibits[x].get("reliability", 0)) for x in cited) / len(cited)
        groups = {exhibits[x].get("independence_group") or x for x in cited}
        evidence = rel * (len(groups) / len(cited)) * 100
    else: evidence = 0.0
    counted = next((e["data"] for e in events if e["type"] == "ballot.counted"), {"ballots": []})
    ballots = counted.get("ballots", [])
    fams = {}
    for b in ballots: fams.setdefault(b["family"], []).append(b["vote"] == holding)
    agreement = (sum(1 for v in fams.values() if all(v)) / len(fams) * 100) if fams else 0.0
    survival = (len(surviving) / len(claims) * 100) if claims else 0.0
    n = len(ballots); yes = sum(1 for b in ballots if b["vote"] == holding)
    margin = max(0.0, (yes - (n - yes)) / n * 100) if n else 0.0
    judge = float(judge_confidence if judge_confidence is not None else ruling.get("confidence", 0) or 0)
    w = CFG["weights"]
    weighted = (w["evidence_strength"] * evidence + w["cross_family_agreement"] * agreement + w["argument_survival"] * survival
                + w["jury_margin"] * margin + w["judge_confidence"] * judge)
    score = round(min(weighted, evidence, agreement))
    return {"score": score, "band": band(score)["band"], "for_position": holding, "weighted_mean": round(weighted, 2),
            "cap": round(min(evidence, agreement), 2),
            "inputs": {"evidence_strength": round(evidence, 2), "cross_family_agreement": round(agreement, 2), "argument_survival": round(survival, 2),
                       "jury_margin": round(margin, 2), "judge_confidence": round(judge, 2)},
            "counts": {"exhibits_cited": len(cited), "claims": len(claims), "struck": sum(1 for c in claims if c["id"] in struck),
                       "rebutted": sum(1 for c in claims if c["id"] in rebutted), "ballots": n, "for_holding": yes, "families": len(fams)},
            "weights": w}

def case_events(cid):
    out = []
    with open(ROOT / "private/ledger/events.ndjson") as f:
        for line in f:
            if f'"{cid}"' in line:
                e = json.loads(line)
                if (e.get("data") or {}).get("case") == cid and (e.get("data") or {}).get("court") == "court": out.append(e)
    return out

if __name__ == "__main__":
    print(json.dumps(compute(case_events(sys.argv[1])), indent=1))
