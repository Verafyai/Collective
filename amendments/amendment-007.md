---
id: A-0007
title: The Collective: two repos, structure over time
class: A
status: ratified
proposer: Rex St. John (Steward), edict E-0029
proposed: 2026-09-24
charter_version: v5.0.0
log_entry_hash: cac8b1a6445b56a3740ae037e7232ebf710233a490d7048780d522319fa7fe71
---

# Amendment 007 · The Collective: two repos, structure over time

## Proposed text

Recorded before amendment files existed; the full text is Charter v5.0.0 (`charter/history/CHARTER-v5.0.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v5.0.0`.

## Reason

The organization is renamed the Collective (Article 1; earlier records' "the Org" is the same entity). New Article 16, Structure over time: versions archived, tagged, and timelined; charter.py lists, shows, diffs, rebuilds files (never overwriting live records), and rewinds (Steward-only, with STOP, as a new major version; the log is never rewound). New Article 17, Repositories: public git@github.com:Verafyai/Collective.git (working folder, governance records) and private git@github.com:Verafyai/CollectivePrivate.git (private/: edicts, event log, drafts, sealed auth, config, library PDFs, incidents); gated public commits with incidents recorded privately; Steward-only public push; the private repo is pushed daily as the ledger backup; auth only encrypted with age, in the private repo (17.3, entrenched). Paths moved: edicts → private/edicts, ledger → private/ledger, outbox → private/outbox, library PDFs → private/library/pdfs. v4.0.0's archive moved to private/charter-history because it embedded edicts; from v5.0.0 no private material is embedded in the Charter. Added repos.sh, secrets.sh, charter.py, and tests; gov-publish now commits into the public repo; workspace template renamed collective.toml.

## Discussion

Board thread: org/board/2026-09-24-amendment-collective.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v5.0.0 on 2026-09-24.
Amendment log entry hash: `cac8b1a6445b56a3740ae037e7232ebf710233a490d7048780d522319fa7fe71` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v5.0.0). File generated from the verified amendment log.
