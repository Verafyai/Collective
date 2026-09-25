---
id: A-0019
title: User Guide matches the current Charter; task board command
class: C
status: proposed
proposer: scribe
proposed: 2026-09-24
text_sha256: 716527b26e65535c0eb15a9d67160c19a6dfc24c42153544393e42e06e19704a
charter_version: (pending)
---

# Amendment 019 · User Guide matches the current Charter; task board command

## Proposed text

Amend Part V, V.112 (`docs/USER-GUIDE.md`), and nothing else:

1. In the header note, replace

   > **Matches Charter v6.2.0.**

   with

   > **Matches Charter v6.3.1.**

   (the patch version this Class C amendment would produce after v6.3.0; if another amendment is recorded first, the Clerk uses the version actually assigned when this one is recorded).

2. In §3 "Starting and stopping", add this row to the table after "Watch events live":

   | See the task board | `tsk list` (one thread per office, e.g. `tsk list --thread prototyper`; the store is `org/tasks/`) |

No other wording changes. Nothing here changes any office's powers or tools.

## Reason

Article 19.1 requires the User Guide to state the Charter version it matches. It says v6.2.0, but the Charter has been v6.3.0 since A-0018. The Auditor flagged this in the 2026-09-24 digest (`org/board/2026-09-24-digest.md` §6; `org/board/2026-09-24-standup.md`, auditor post). `docs/USER-GUIDE.md` is generated from Part V (V.112), so the Scribe can't correct it directly without creating drift; it has to change through the Charter. A-0016 and A-0017 changed nothing an operator runs. A-0018 added the tsk task board (`org/STRUCTURE.md`, "The store is `org/tasks/`…"), which the guide doesn't mention yet.

## Discussion

Board thread: org/board/2026-09-24-amendment-019.md
Lawyer's opinion: (pending)

## Vote

—

## Outcome

—

## History

- 2026-09-24: proposed by scribe.
