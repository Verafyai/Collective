---
id: A-0044
title: charter-verify reads only the log
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0102 (continue all unfinished work)
proposed: 2026-09-25
charter_version: v6.11.13
log_entry_hash: f9e17816ca21ebc5933cae6df6e39c1fd1a9d6929913eb75a02428191df95ec2
---

# Amendment 044 · charter-verify reads only the log

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.11.13 (`charter/history/CHARTER-v6.11.13.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.11.13`.

## Reason

Part V: agents/bin/charter-verify.py parses entries only from the amendment log (after the last Part VI heading), headings at line starts only, and fails if any log heading doesn't parse. Since v6.11.0 a test's stand-in string in Part V had matched as an entry and swallowed A-0000's hashes, so A-0000 was skipped instead of verified (the exit code stayed 0). tests/test_dashboard.py checks the offices against the roster and allows new rooms below the floor.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0044.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.11.13 on 2026-09-25.
Amendment log entry hash: `f9e17816ca21ebc5933cae6df6e39c1fd1a9d6929913eb75a02428191df95ec2` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.11.13). File generated from the verified amendment log.
