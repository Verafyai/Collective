---
id: A-0050
title: The event log ignores the bridge's own state
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0114 (finish all work)
proposed: 2026-09-25
charter_version: v6.13.3
log_entry_hash: 48937ad2663ad2abb0afb8616d559e424c2786353dd4209ffd4e1b143898ff22
---

# Amendment 050 · The event log ignores the bridge's own state

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.13.3 (`charter/history/CHARTER-v6.13.3.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.13.3`.

## Reason

Part V: agents/bin/eventlog.py's default ignore list adds agents/observability/.bridge_state*, .ops_spool.ndjson*, and gitleaks-rules.toml (the bridge's working files, which change on every pass), beside tool environments at any depth; tests/test_blog.py counts incidents from its own log instead of assuming one.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0050.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.13.3 on 2026-09-25.
Amendment log entry hash: `48937ad2663ad2abb0afb8616d559e424c2786353dd4209ffd4e1b143898ff22` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.13.3). File generated from the verified amendment log.
