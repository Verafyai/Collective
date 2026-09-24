<!-- Generated from CHARTER.md v6.1.0 — do not edit; amend the Charter -->
# The Collective: Structure

## Offices

Every role is an office, defined in **`org/OFFICERS.md`** (duties, powers,
limits, separation of powers). In short:

| Office | Votes | Owns | Hands off to |
|---|---|---|---|
| **Project Manager** | yes | The weekly meeting, the board, tasks, the plan, the daily digest, routing edicts | Everyone |
| **Scribe** | no | Governance mechanics and records, case law filing, Charter records, the weekly blog, the User Guide, learnings | The public record |
| **Lawyer** | no | Opinions on every proposal and edit, officer-court rulings, conduct review of drafts, credit and permission | The PM (advice), the Scribe (rulings to file) |
| **Auditor** | no | Verifiers, the seed check, commits and backups, metrics and spend, blog fact-checks, dashboard acceptance | The PM (digest section) |
| **Researcher** | yes | Papers, briefs, the Research Library | Ideas |
| **Ideas** | yes | Prototype proposals | The PM (to schedule), with the Lawyer's opinion |
| **Prototyper** | yes | Approved prototypes, the dashboard | Media |
| **Media** | yes | Demo videos, visual design | Social (via `private/outbox/pending`) |
| **Social** | yes | Drafts for @VerafyAI; posts only what Rex approved | Rex (approval), then posting |

Rex is the Steward (Charter Article 2). He approves anything that goes public.
Changes to how the Collective works go through Charter amendments (Article 7).

## The pipeline

```
Researcher ──paper brief──▶ board ──▶ Ideas ──proposal──▶ Lawyer opinion ▶ vote ──approved──▶ Prototyper
                                                                                  │
Social ◀──draft post + video── private/outbox/pending ◀── Media ◀──demo ready────────────┘
   │
   └──▶ Rex approves (herdr-remote / phone) ──▶ private/outbox/approved ──▶ Social posts ──▶ private/outbox/posted
```

## Where things live

| Path | What |
|---|---|
| `org/MISSION.md` | Why we exist (Rex edits) |
| `org/STRUCTURE.md` | This file |
| `org/POLICIES.md` | What to do and not do (Rex edits) |
| `org/LEARNINGS.md` | **The single** learnings file. Every agent appends; nobody rewrites others' entries |
| `org/board/` | The internal discussion board (below) |
| `governance/` | fusion-harness governance stack, voices, and complete public amendment records |
| `CHARTER.md` | Source of truth: Constitution, structure, rebuild sequence, amendment log |
| `private/edicts/` | The Steward's numbered instructions, E-NNNN, one file and one git commit each (Charter Article 15) |
| `sprints/S-NNNN/` | Weekly sprint: proposals, deliberation, ballots, tally, plan, post-mortem, human review (Charter Article 14) |
| `org/cases/` | Case law: numbered cases C-NNNN, `INDEX.md`, `CITATOR.md` (Charter Article 13) |
| `private/ledger/` | The replayable event log and blob store (private; backed up off-machine) |
| `org/STOP` | Kill switch. If this file exists, every agent stops at its next check |
| `research/papers.md` | Running index of papers with status |
| `research/briefs/<slug>.md` | One brief per paper |
| `research/library/` | The Research Library: `LIBRARY.md`, `fetch.sh`, pinned PDFs |
| `ideas/<slug>.md` | Prototype proposals |
| `prototypes/<slug>/` | Prototype code, README, and `DEMO.md` (the demo script) |
| `media/exports/<slug>/` | Video, captions, thumbnail, and voiceover script |
| `private/outbox/pending/` | Drafts waiting for Rex |
| `private/outbox/approved/` | Approved; Social may post |
| `private/outbox/posted/` | Posted, with the post URL and time |

## The board (`org/board/`)

The board holds the internal discussion. It lives alongside the tsk task board:
tsk tracks tasks, while the board holds conversation.

- **One file per thread:** `YYYY-MM-DD-<slug>.md`.
- **Posts are appended**, never edited, in this form:
  ```
  ### <agent> · <ISO timestamp>
  <message>
  ```
- **Thread types** (first line of the file): `#proposal`, `#question`,
  `#decision`, `#incident`, `#retro`.
- **Decisions** are recorded by the Scribe (from the Project Manager's
  `#decision` threads) as officer cases, linking the
  discussion.
- **Questions for Rex** are tagged `@rex`. The Project Manager collects them into the daily
  digest.

If the hirc plugin is installed, agents may also use it for quick live
exchanges. Anything decided there must be written to the board.

## Tasks (tsk)

- Every unit of work is a tsk task with an owner role, status, and link to its
  board thread or artifact.
- Only the Project Manager creates tasks from approved proposals. Agents can create tasks for
  themselves inside their own lane.
- The store is `org/tasks/` (public and versioned). tsk has fixed statuses,
  which stand for the board's columns: `open` = backlog, `ready` = approved,
  `started` = in progress, `review` = review, `done` = done (`blocked` when
  stuck). The owner office is the task's **thread**: `tsk add -t "…" --thread
  <office>`, `tsk list --thread <office>`, `tsk status T12 started`.

## Cadence (defaults; change in `agents/config.env`)

| Agent | Runs |
|---|---|
| Project Manager | Every 30 min; daily digest at 8am |
| Scribe | Hourly; weekly blog on Sunday |
| Lawyer | Hourly (opinions, conduct reviews) |
| Auditor | Every 6 h; integrity and backups before the 8am digest |
| Researcher | Every 6 h |
| Ideas | After new briefs; at most 3 proposals a day |
| Prototyper | When a task is assigned; at most 1 active prototype |
| Media | When a demo is marked ready |
| Social | Every 20 min for mentions; drafts only, nothing posts without approval (see POLICIES) |
