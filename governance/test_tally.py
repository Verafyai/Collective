"""Tests for agents/bin/gov-tally.py. Run: python3 governance/test_tally.py"""
import json, pathlib, subprocess, tempfile, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
def run(cls, votes, members=None, priv=False, badhash=False, extra=None):
    d = pathlib.Path(tempfile.mkdtemp()); (d/"ballots").mkdir()
    members = members or ["social","researcher","ideas","prototyper","media"]
    (d/"amendment.json").write_text(json.dumps({"id":"A-T","class":cls,"frozen_sha256":"abc","members":members,"affects_privileges":priv, **(extra or {})}))
    for m,v in votes.items():
        h = "zzz" if (badhash and m=="media") else "abc"
        (d/"ballots"/f"{m}.md").write_text(f"vote: {v}\nself_interest: no\nfrozen_sha256: {h}\nreason: test\n")
    subprocess.check_output([sys.executable, str(ROOT/"agents/bin/gov-tally.py"), str(d)])
    return json.loads((d/"tally.json").read_text())
Y,N,A="yes","no","abstain"
r=run("C",{"social":Y,"researcher":Y,"ideas":N,"prototyper":A}); assert r["outcome"]=="passed" and not r["steward_ratification_required"], r
r=run("B",{"social":Y,"researcher":Y,"ideas":Y,"prototyper":N}); assert r["outcome"]=="passed" and r["steward_ratification_required"], r
r=run("B",{"social":Y,"researcher":Y,"ideas":N,"prototyper":N}); assert r["outcome"]=="rejected", r
r=run("C",{"social":Y,"researcher":Y,"ideas":Y}); assert r["outcome"]=="failed_quorum", r
r=run("A",{"social":Y,"researcher":Y,"ideas":Y,"prototyper":Y,"media":Y}); assert r["outcome"]=="advisory" and r["steward_ratification_required"], r
r=run("C",{"social":Y,"researcher":Y,"ideas":Y,"prototyper":N},priv=True); assert r["steward_ratification_required"], r
r=run("C",{"social":Y,"researcher":Y,"ideas":N,"prototyper":N,"media":Y},badhash=True); assert r["cast"]==4 and r["outcome"]=="rejected" and r["problems"], r   # voided ballot; 2-2 tie fails
# membership (Article 3.6): simple majority; the subject can't vote on its own removal
r=run("M",{"social":Y,"researcher":Y,"ideas":N,"prototyper":N,"media":Y},extra={"subject":"media"}); assert r["cast"]==4 and r["outcome"]=="rejected", r   # media's own vote excluded → 2-2
r=run("M",{"social":Y,"researcher":Y,"ideas":Y,"prototyper":N},extra={"subject":"media"}); assert r["outcome"]=="passed" and not r["steward_ratification_required"], r
r=run("M",{"social":Y,"researcher":Y,"ideas":Y,"prototyper":Y},extra={"subject":"media","remaining_voters":2}); assert r["outcome"]=="blocked_minimum_membership", r
print("gov-tally tests passed")
