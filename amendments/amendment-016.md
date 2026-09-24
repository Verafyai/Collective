---
id: A-0016
title: Public-commit gate scoped to committed files; test and timestamp hygiene
class: C
status: ratified
proposer: Rex St. John (Steward), edicts E-0042 and E-0043, at the setup agent's board question
proposed: 2026-09-24
charter_version: v6.2.2
log_entry_hash: 9bb841caed0540d48737c3a2e816c68626049712409e1ca3854d10c1f96f1ff0
---

# Amendment 016 · Public-commit gate scoped to committed files; test and timestamp hygiene

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.2.2 (`charter/history/CHARTER-v6.2.2.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.2.2`.

## Reason

Fixes found in setup Step 1c. (1) repos.sh (V.22): gitleaks now scans only the files the public commit would include (never git-ignored ones such as agents/.env, which blocked every public commit once real keys were filled in); a gitleaks refusal records a private incident like the grep scan (Article 17.4); a failed scan blocks (fail closed). (2) repos.sh and gov-publish.sh (V.40) report file:line only, never the matched text; grep -H so a single-file scan can't record the secret as its "location". (3) The invalid gitleaks flag -q is removed from V.22 and V.40, matching the files on disk, which had drifted from Part V. (4) date -Is → date -Iseconds in repos.sh, gov-publish.sh, approve.sh (V.19), ledger-backup.sh (V.27), and run-role.sh (V.18): macOS date rejects -Is, which left approval stamps and log times blank. (5) Tests (V.51–V.56): scratch copies never include .env, secrets/, or *.key, are deleted on exit, and git config goes to a sandbox file instead of the Steward's ~/.gitconfig; test_repos_charter gains checks that an ignored agents/.env doesn't block a public commit, that gitleaks catches what grep misses and records an incident, and that a refusal never prints the secret.

## Discussion

Board thread: org/board/2026-09-24-amendment-public-commit-gate.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.2.2 on 2026-09-24.
Amendment log entry hash: `9bb841caed0540d48737c3a2e816c68626049712409e1ca3854d10c1f96f1ff0` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.2.2). File generated from the verified amendment log.
