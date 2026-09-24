"""Tests for agents/bin/case.py (Charter Article 13). Run: python3 tests/test_case_law.py
Works on a scratch copy of org/cases so the real case law is untouched."""
import pathlib, shutil, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(ROOT / "agents", tmp / "agents"); (tmp / "org").mkdir()
shutil.copytree(ROOT / "org" / "cases", tmp / "org" / "cases")
CASE = [sys.executable, str(tmp / "agents/bin/case.py")]
def run(*a): return subprocess.run(CASE + list(a), capture_output=True, text=True)
def draft(title, court, cites="", holding="A rule."):
    p = tmp / "d.md"
    c = "".join(f"\n  - {{case: {x}, treatment: {t}}}" for x, t in cites) if cites else ""
    p.write_text(f"---\ntitle: {title}\ncourt: {court}\nlabels: [operations]\nheadnote: h\nsource: test\n"
                 f"{'cites:' + c if c else ''}\n---\n## Question\nq\n## Facts\nf\n## Holding\n{holding}\n"
                 "## Reasoning\nr\n## Dissent\nNone.\n## Scope\ns\n")
    return run("new", "--draft", str(p))
n0 = len(list((tmp / "org/cases").glob("C-*.md")))
import re as _re
def survival():
    m = _re.search(r"\((\d+)/(\d+) challenged", run("stats").stdout)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
base_survived, base_challenged = survival()   # the live case law may already contain challenges
# 1. a chief case may not overrule a steward case
r = draft("Officer tries to overrule steward", "officer", [("C-0001", "overrules")])
assert "REFUSED" in r.stdout and "cannot overrule" in r.stdout, r.stdout
# 2. chief cases can be overruled by later chief cases; status derives from the citator
assert "filed" in draft("Officer rule A", "officer").stdout
a = f"C-{n0+1:04d}"
assert "filed" in draft("Legacy chief-court rule B distinguishes A", "chief", [(a, "distinguishes")]).stdout   # legacy court name still accepted
assert "filed" in draft("Officer rule C overrules A", "officer", [(a, "overrules")]).stdout
cit = (tmp / "org/cases/CITATOR.md").read_text()
assert f"**{a}** · overruled" in cit, cit
# 3. an assembly case may limit a chief case
assert "filed" in draft("Assembly limits B", "assembly", [(f"C-{n0+2:04d}", "limits")]).stdout
assert f"**C-{n0+2:04d}** · limited" in (tmp / "org/cases/CITATOR.md").read_text()
# 4. citing an unknown case is refused
assert "REFUSED" in draft("Cites the future", "chief", [("C-9999", "follows")]).stdout
# 5. editing a filed holding is detected; appending to History is fine
f = sorted((tmp / "org/cases").glob(f"{a}-*.md"))[0]
t = f.read_text(); f.write_text(t + "- later note.\n"); assert run("check").returncode == 0
f.write_text(t.replace("A rule.", "A quietly different rule.")); r = run("check")
assert r.returncode == 1 and "frozen text changed" in r.stdout, r.stdout
f.write_text(t)
# 6. search, show, and survival stats
assert a in run("search", "rule", "--status", "overruled").stdout
assert "Cited by" in run("show", a).stdout
sv, ch = survival()
assert (sv - base_survived, ch - base_challenged) == (1, 2), (sv, ch, base_survived, base_challenged)   # A overruled, B limited
print("case law tests passed")
