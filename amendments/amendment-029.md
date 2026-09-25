---
id: A-0029
title: Vendored code and the redaction gate
class: C
status: ratified
proposer: Rex St. John (Steward), edicts E-0083 and E-0086, at the test failure found while recording A-0028
proposed: 2026-09-24
charter_version: v6.10.1
log_entry_hash: 52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2
---

# Amendment 029 · Vendored code and the redaction gate

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.10.1 (`charter/history/CHARTER-v6.10.1.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.10.1`.

## Reason

repos.sh (V.22): gitleaks flagged minified vendored xterm.js as a generic API key, which would block every public commit. Vendored third-party files under dashboard/vendor/ now skip gitleaks only while each still matches its committed SHA256SUMS; a changed file is scanned as before, and the grep scan still covers every file.

## Discussion

Board thread: org/board/2026-09-24-amendment-a-0029.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.10.1 on 2026-09-24.
Amendment log entry hash: `52c3c67879ead817257b551191809b8db476ff3f8951b5178e62dad70d7840c2` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.10.1). File generated from the verified amendment log.
