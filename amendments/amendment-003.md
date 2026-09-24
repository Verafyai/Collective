---
id: A-0003
title: Replayability
class: A
status: ratified
proposer: Rex St. John (Steward)
proposed: 2026-09-24
charter_version: v3.0.0
log_entry_hash: 0e61d8e7d61e239121f6544da5e8b7ace6ac85f2e39e504e328d9222c7c95066
---

# Amendment 003 · Replayability

## Proposed text

Recorded before amendment files existed; the full text is Charter v3.0.0 (`charter/history/CHARTER-v3.0.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v3.0.0`.

## Reason

New entrenched Article 12, Replayability. Every state change is an event in an append-only, hash-chained log with a content-addressed blob store. Runs record the prompt, full transcript, file changes, and tree hash; Steward approvals, manual edits, effects, governance, backups, incidents, and rewinds are recorded. Secrets are redacted. Replay rebuilds from recorded outputs and never re-executes effects; counterfactual re-runs happen only in scratch copies. Rewind is Steward-only, requires STOP, and never deletes history. Out-of-band changes are flagged. Daily verified off-machine backups. Recording can only be disabled by the Steward. Added eventlog.py, replay.py, playback.py, rec.sh, and ledger-backup.sh; runner, approvals, posting, and publishing now emit events; bootstrap initializes the log; R8c, the R9 restore path, and the digest and quarterly checks updated. Article 4.11 entrenchment list extended.

## Discussion

Board thread: org/board/2026-09-24-amendment-replayability.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v3.0.0 on 2026-09-24.
Amendment log entry hash: `0e61d8e7d61e239121f6544da5e8b7ace6ac85f2e39e504e328d9222c7c95066` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v3.0.0). File generated from the verified amendment log.
