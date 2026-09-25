---
id: A-0045
title: The Weave mirror
class: B
status: ratified
proposer: Rex St. John (Steward), edict E-0106; amends entrenched Article 12 (Article 2.2)
proposed: 2026-09-25
charter_version: v6.12.0
log_entry_hash: 497f1e7c59f485c549bacd1feb6652cba7d58659d2f659004fc5d7d70cc89345
---

# Amendment 045 · The Weave mirror

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.12.0 (`charter/history/CHARTER-v6.12.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.12.0`.

## Reason

New Article 12.10: the event log is traced to the Steward's private W&B Weave project by agents/bin/weave_sync.py, each run as one trace with its events, prompt and transcript text, and reported cost, and every other event as its own call; redacted by 12.3's rules before it leaves the machine; never file contents, edict text, or agents/.env; a view, not a record, so an outage never stops recording. The key is WANDB_API_KEY in agents/.env. Part V: new agents/bin/weave_sync.py and tests/test_weave.py; setup/bootstrap.sh installs weave 0.53.10 in agents/.venv; herdr/projects/collective.toml runs the mirror in a 'weave' tab; CREDITS.md lists Weave (Apache-2.0). The dashboard shows a Weave link in private view (P-001).

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0045.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.12.0 on 2026-09-25.
Amendment log entry hash: `497f1e7c59f485c549bacd1feb6652cba7d58659d2f659004fc5d7d70cc89345` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.12.0). File generated from the verified amendment log.
