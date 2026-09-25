---
id: A-0043
title: Numbers used twice are caught; tests follow live records; the digest in UTC
class: C
status: ratified
proposer: Rex St. John (Steward), edict E-0102 (continue all unfinished work)
proposed: 2026-09-25
charter_version: v6.11.12
log_entry_hash: 4ad4c15e5b2797d8f2126c08798e01e26f8e39fe3b338ccfaea1ff386b7d7788
---

# Amendment 043 · Numbers used twice are caught; tests follow live records; the digest in UTC

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.11.12 (`charter/history/CHARTER-v6.11.12.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.11.12`.

## Reason

Part V: amendment.py sync never marks a file ratified when its title isn't the log's, and check reports it ('a number used twice', the cause of the A-0021 and A-0037 mix-ups); weekly-digest.py defaults --end to the UTC date, like every event; tests/test_amendments_projects.py keeps open proposals when regenerating and counts projects instead of assuming two; tests/test_blog.py starts from an empty sprints/; agents/config.example.env and herdr/projects/collective.toml gain the members ratified just before this.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0043.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.11.12 on 2026-09-25.
Amendment log entry hash: `4ad4c15e5b2797d8f2126c08798e01e26f8e39fe3b338ccfaea1ff386b7d7788` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.11.12). File generated from the verified amendment log.
