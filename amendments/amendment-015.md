---
id: A-0015
title: launch.sh: fixes from the first real launch
class: C
status: ratified
proposer: Rex St. John (Steward), at the Steward's report of the launch error
proposed: 2026-09-24
charter_version: v6.2.1
log_entry_hash: 58626e82a316bc75dbb5ed98b17acd226b55b689f91e3f8aa292b00a34fd3e02
---

# Amendment 015 · launch.sh: fixes from the first real launch

## Proposed text

Recorded before amendment files existed; the full text is Charter v6.2.1 (`charter/history/CHARTER-v6.2.1.md`). Compare with the version before it:
`agents/bin/charter.py diff <previous> v6.2.1`.

## Reason

Fixes launch.sh after the Steward's first launch on his Mac. The script now detects the installed herdr-plus plugin by its config folder instead of the plugin list (no more repeat install prompts); finds the herdr-plus program inside herdr's plugin folders, since installing the plugin doesn't put it on PATH, or gives the documented Homebrew install; and, when herdr isn't running, says plainly to run 'herdr' and then './launch.sh' in its first pane. Tested with stand-ins for each case. Lesson recorded in LEARNINGS.

## Discussion

Board thread: org/board/2026-09-25-amendment-launch-fix.md

## Vote

Steward action
Ratified by: Rex St. John

## Outcome

Ratified and applied to the Charter as v6.2.1 on 2026-09-24.
Amendment log entry hash: `58626e82a316bc75dbb5ed98b17acd226b55b689f91e3f8aa292b00a34fd3e02` (verify: `agents/bin/charter-verify.py`).

## History

- 2026-09-24: ratified (Charter v6.2.1). File generated from the verified amendment log.
