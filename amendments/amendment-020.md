---
id: A-0020
title: Character classes and spawning; the dashboard's second write
class: B
status: ratified
proposer: Rex St. John (Steward), edicts E-0058, E-0060, E-0061 (ratification), E-0063, from the floor handoff
proposed: 2026-09-24
charter_version: v6.4.0
log_entry_hash: fbe7b2844da750e4e45db22a6ee0ac2d43d869f4475a3fbb1616701cf07888da
---

# Amendment 020 · Character classes and spawning; the dashboard's second write

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.4.0 (`charter/history/CHARTER-v6.4.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.4.0`.

## Reason

New Article 3.8: every agent has a character class (agents/classes.json) and a roster entry (agents/roster.json: class, room, look, vote, status). Spawning, including cloning, is a membership motion drafted by spawn.py (Class M, full configuration attached); the agent is "proposed" until the motion passes, and only then does the Scribe run spawn.py activate. New agents start with base tools and no vote; requested tools and a vote need the Steward (Articles 7.6, Class B). Officers can't be spawned, cloned, or retired this way. Retirement is its own motion (spawn.py retire, then retire-apply), without the subject's vote. Article 18.7 replaced: the dashboard's writes are (a) project comments and (b) in private view only, a membership motion from the Steward's spawn wizard. Tool grants ratified by the Steward under Article 7.6 (V.16): spawn.py propose/clone/retire/list/bio for the PM, Lawyer, Researcher, Ideas, Prototyper, and Media; all of spawn.py for the Scribe; list and bio for the Auditor. OFFICERS (V.2), AGENT-PERMISSIONS (V.3), and the User Guide (V.112, now matching v6.4.0, with section 6b) updated; sprint.py (V.29) reads voters and proposers from the roster; the roster is a live record (charter.py LIVE, V.31; seed-check.sh, V.35); font credits in CREDITS.md (V.114; Barlow, Barlow Semi Condensed, Public Sans, Source Serif 4, SIL OFL, served locally). New Part V files: V.122 agents/classes.json, V.123 agents/roster.json, V.124 agents/bin/spawn.py, V.125 tests/test_spawn.py, V.126 tests/test_dashboard.py. Part II §4 lists the new files. The dashboard code itself (P-001) is versioned by its project, not Part V.

## Discussion

Board thread: org/board/2026-09-24-amendment-classes-and-spawning.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.4.0 on 2026-09-24.
Amendment log entry hash: `fbe7b2844da750e4e45db22a6ee0ac2d43d869f4475a3fbb1616701cf07888da` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.4.0). File generated from the verified amendment log.
