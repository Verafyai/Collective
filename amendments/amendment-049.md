---
id: A-0049
title: The public gate trusts verified Charter archives
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0114 (finish all work)
proposed: 2026-09-25
charter_version: v6.13.2
log_entry_hash: ba11766b6290e15e4e54b6b250b51cbda3054ba2f9fa7f74f7b27a109135be6b
---

# Amendment 049 · The public gate trusts verified Charter archives

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.13.2 (`charter/history/CHARTER-v6.13.2.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.13.2`.

## Reason

Part V: agents/bin/repos.sh's public gate skips an archived Charter version only when the text before its log entry hashes to the logged value and the file ends exactly at that entry (Article 8.1), because archives are immutable: v6.13.0 and v6.13.1 hold a test's stand-in key line that can never be edited out. tests/test_dashboard.py builds that stand-in so the source has no key-shaped assignment.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0049.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.13.2 on 2026-09-25.
Amendment log entry hash: `ba11766b6290e15e4e54b6b250b51cbda3054ba2f9fa7f74f7b27a109135be6b` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.13.2). File generated from the verified amendment log.
