---
id: A-0034
title: A-0030 follow-up: tests independent of live state
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0097 (ratifying all of A-0030's open work)
proposed: 2026-09-25
charter_version: v6.11.4
log_entry_hash: 26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a
---

# Amendment 034 · A-0030 follow-up: tests independent of live state

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.11.4 (`charter/history/CHARTER-v6.11.4.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.11.4`.

## Reason

Part V: tests/test_shell.py and tests/test_dashboard.py simulate an unratified A-0030 by removing its log entry in their scratch copy (the gate reads the ratified log entry, not a marker), and check room chats against whatever rooms the roster seats agents in.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0034.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.11.4 on 2026-09-25.
Amendment log entry hash: `26b44e1edec563d091dfae910d503e72e9b2cd3b247f8a3741b95ecc9700923a` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.11.4). File generated from the verified amendment log.
