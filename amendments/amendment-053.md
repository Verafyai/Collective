---
id: A-0053
title: One writer at a time; the repaired log; Court seats; credits
class: C
status: ratified
proposer: Rex St. John (Steward), edicts E-0119, E-0121; the Auditor's fork incident and the Lawyer's opinion on P-006 v001
proposed: 2026-09-25
charter_version: v6.13.5
log_entry_hash: ed7ea26d34cbd45f5f4d0435d5c385bd73a22791dcaa79253f7665e57fce6f3a
---

# Amendment 053 · One writer at a time; the repaired log; Court seats; credits

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.13.5 (`charter/history/CHARTER-v6.13.5.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.13.5`.

## Reason

Part V: agents/bin/eventlog.py takes an exclusive lock for every command and loads HEAD only inside it, so concurrent runs can never append the same seq (the 2026-09-25 fork, repaired by E-0121: re-chained from line 11,682, original archived as a blob, ledger.repair #12036); new tests/test_eventlog.py races twenty writers; the bridge files Court turns under their seats (court-<seat>), never the offices; tests/test_court.py checks that the evidence fetcher refuses every private-path and local-address spelling; CREDITS.md credits pi, W&B Inference, and the open models the Court seats, with the Llama attribution caveat.

## Discussion

Board thread: org/board/2026-09-25-amendment-a-0053.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.13.5 on 2026-09-25.
Amendment log entry hash: `ed7ea26d34cbd45f5f4d0435d5c385bd73a22791dcaa79253f7665e57fce6f3a` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-25: ratified (Charter v6.13.5). File generated from the verified amendment log.
