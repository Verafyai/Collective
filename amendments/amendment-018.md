---
id: A-0018
title: Plugins pinned to reviewed code; the task board configured
class: B
status: ratified
proposer: Rex St. John (Steward), edicts E-0046 and E-0047, at setup Step 3
proposed: 2026-09-24
charter_version: v6.3.0
log_entry_hash: 90fa7f72c9bd0e20d03cb5e106d95f5848098189b449c1dcc59cc3f1edba256e
---

# Amendment 018 · Plugins pinned to reviewed code; the task board configured

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.3.0 (`charter/history/CHARTER-v6.3.0.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.3.0`.

## Reason

Part II §5: memex held, not installed (E-0045); herdr-radar core (E-0046). Part III R6: plugins install only at the reviewed commit pinned in setup/plugins.txt; notes record everything that leaves the machine. R7: tsk has fixed statuses and no custom columns or labels, so statuses stand for the columns (open = backlog, ready = approved, started = in progress, review, done) and the owner office is the task's thread; the store is org/tasks (public, versioned) with update checks off; herdr-projects installed but not configured (its agents would bypass run-role.sh's gates); herdr-remote deferred (E-0039). Part V: setup/plugins.txt (V.66) pins owner/repo@commit with a held tier; setup/bootstrap.sh (V.60) installs pinned commits only, builds herdr-projects from source, skips held and unpinned plugins, links tsk onto PATH, and creates org/tasks; agents/config.example.env (V.16) exports TSK_STATE_DIR and TSK_NO_UPDATE_CHECK; .gitignore (V.68) ignores tsk lock and backup files; collective.toml (V.67) board tab runs tsk on the Collective's store; org/STRUCTURE.md (V.4), agents/COMMON.md (V.6), specs/setup-plan.md (V.119), and docs/plugin-notes.md (V.121) updated to match.

## Discussion

Board thread: org/board/2026-09-24-amendment-plugins-and-task-board.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.3.0 on 2026-09-24.
Amendment log entry hash: `90fa7f72c9bd0e20d03cb5e106d95f5848098189b449c1dcc59cc3f1edba256e` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.3.0). File generated from the verified amendment log.
