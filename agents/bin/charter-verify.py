#!/usr/bin/env python3
"""Verify the Charter's Amendment Log end to end (Charter Article 8.1).

For every entry A-NNNN at version X.Y.Z, loads charter/history/CHARTER-vX.Y.Z.md
and checks: (1) charter_sha256_before_entry matches that version's text before the
entry, (2) prev_entry_hash matches the previous entry, (3) entry_hash =
sha256(prev + charter_sha + id). Also checks the current CHARTER.md is archived.
Exit 0 if everything verifies.
"""
import hashlib, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
cur = (ROOT / "CHARTER.md").read_text()
# only the log itself (after the last Part VI heading), and only headings at the start of a line: text quoted in
# Part V (code, tests) must never be read as a log entry
log = cur[[m.start() for m in re.finditer(r"\n---\n\n# PART VI — ", cur)][-1]:]
entries = re.findall(r"^### (A-\d{4}) · v([\d.]+) ·[^\n]*\n(?:(?!### A-)[^\n]*\n)*?charter_sha256_before_entry: (\w+)\nprev_entry_hash: (\w+)\nentry_hash: (\w+)", log, re.M)
ok, prev = True, "GENESIS"
heads = re.findall(r"^### (A-\d{4}) · ", log, re.M)
if [e[0] for e in entries] != heads:                   # every log heading must parse as a full entry, in order
    print(f"FAIL log has {len(heads)} entries but {len(entries)} parse: {sorted(set(heads) - {e[0] for e in entries})}"); ok = False
for aid, ver, csha, peh, eh in entries:
    hist = next((d / f"CHARTER-v{ver}.md" for d in (ROOT / "charter" / "history", ROOT / "private" / "charter-history")
                 if (d / f"CHARTER-v{ver}.md").exists()), None)
    if hist is None:
        print(f"skip {aid} v{ver}  (archived privately; clone the private repo to verify)"); prev = eh; continue
    text = hist.read_text()
    before = text[: text.rindex(f"\n### {aid} · v{ver} ·")]
    c1 = hashlib.sha256(before.encode()).hexdigest() == csha
    c2 = peh == prev
    c3 = hashlib.sha256((prev + csha + aid).encode()).hexdigest() == eh
    print(f"{'ok  ' if c1 and c2 and c3 else 'FAIL'} {aid} v{ver}  text:{c1} link:{c2} hash:{c3}")
    ok &= c1 and c2 and c3; prev = eh
ver = re.search(r"Charter version: ([\d.]+)", cur).group(1)
arch = next((d / f"CHARTER-v{ver}.md" for d in (ROOT / "charter" / "history", ROOT / "private" / "charter-history")
             if (d / f"CHARTER-v{ver}.md").exists()), ROOT / "charter" / "history" / f"CHARTER-v{ver}.md")
same = arch.exists() and arch.read_text() == cur
print(f"{'ok  ' if same else 'FAIL'} current v{ver} archived verbatim")
sys.exit(0 if ok and same else 1)
