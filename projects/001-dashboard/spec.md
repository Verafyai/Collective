# The Collective Dashboard: spec (project P-001, task T-0001)

**Mandate:** edicts E-0031 and E-0035, steward case C-0006, Charter Articles
18 and 21. The dashboard is the Collective's **first project** (P-001); this
file is its spec, and each iteration is a numbered version in
`projects/001-dashboard/versions/`.
**Owner:** Prototyper (build). Media reviews the design; the Auditor accepts
it against this spec. The setup session may build v1 during setup (setup plan,
Step 4).

The Steward's window into the Collective: a **local web app** in the browser
showing what the Collective is, what it's doing, how well it's doing, and why
it decided what it decided. Live, and rewindable to any point in its history.

---

## 1. Principles

1. **Everything shown comes from versioned records:** git-tracked files in
   the two repos, plus the event log. The dashboard has **no database of its
   own**; delete it and nothing is lost.
2. **Every panel says what it's showing** ("as of commit `abc123`, event
   #4211").
3. **Time travel:** pick any past commit, date, or event number, and the
   whole dashboard renders the Collective as it was then (using
   `agents/bin/replay.py build` into a scratch folder).
4. **Read-only, with one exception: comments.** The dashboard never changes
   the Collective's records, and actions such as approving a draft or
   signing off a sprint stay in their commands (the dashboard shows each
   command to copy). The one thing it writes is **human input on projects**:
   a comment or suggestion is appended to that project's `discussion.md`
   (as `human:<name>`), exactly as `projects.py comment` would, and recorded
   in the event log (Charter Article 18.7).
5. **Local by default.** Bound to `127.0.0.1` only. A **public mode** hides
   everything from the private repo (edicts, transcripts, drafts, incidents),
   for screenshots or future publishing.
6. **The dashboard itself is versioned:** code in the public repo, changes by
   sprint item or `#decision`, and a daily metrics snapshot committed so KPIs
   have history.

## 2. Run it

```
agents/bin/dashboard.sh              # http://127.0.0.1:4848
agents/bin/dashboard.sh --public     # public mode (no private data)
```

Python 3 standard library only on the server (no framework, no build step).
The front end is static HTML, CSS, and JS in `dashboard/`, and may load one
charting library from a CDN. Live updates use Server-Sent Events.

## 3. Panels

| # | Panel | Shows | Sources |
|---|---|---|---|
| 1 | **Mission** | The mission, rendered; its sources (F1, F2); when it last changed and why | `org/MISSION.md`, git log |
| 2 | **Charter** | Current version and verification status; Parts I–IV rendered with an article index; amendment log (class, title, ratification); structure timeline; a diff between any two versions | `CHARTER.md`, `charter/history/`, `charter/TIMELINE.md`, `charter.py`, `charter-verify.py` |
| 3 | **Progress** | Pipeline counts over time (papers briefed → proposals → prototypes → demos → posts published); open tasks by role; commits per day per agent; the Steward's queue (drafts pending, sign-offs, reviews, unimplemented edicts) | `research/`, `ideas/`, `prototypes/`, `private/outbox/`, tsk, git log, `private/edicts/` |
| 4 | **KPIs + OKRs** | Each OKR with its key results and progress bars; each KPI's current value, 8-week trend, and target | `org/OKRS.md`, `org/KPIS.md`, `metrics/` |
| 5 | **Current sprint** | Theme, phase, and countdown to the next phase; each item: owner, objective, success criteria, vote tally, case, status; ballots once revealed | `sprints/S-NNNN/` |
| 6 | **Last sprints** | Every past sprint: grades per item (the five dimensions), report, human review and follow-on actions, and grade trends across sprints | `sprints/*/postmortem/` |
| 7 | **Decisions (with evidence)** | Case law, searchable and filterable by court, label, and status. Each case shows its holding, the evidence behind it (proposal, deliberation transcript, ballots, tally, library papers cited, sources), the precedents it cites and cases citing it, and post-mortem grades. Plus governance records and amendments | `org/cases/`, `governance/records/`, `sprints/`, `research/library/LIBRARY.md` |
| 8 | **Calendar** | Upcoming and past scheduled actions: sprint phases, governance sessions, agent run cadences, case reviews due, amendment votes, daily digest, backups (and anchoring, if adopted). Week and month views, with an `.ics` export | `agents/config.env` schedule, `sprints/`, `org/cases/` review dates, event log |
| 9 | **Live stream** | Watch agents work: one column per agent streaming its current run (prompt, tool calls, files changed), plus a debate view that streams fusion-harness sessions as they happen (positions, debate rounds, sealed-ballot status), and a replay control to play any past run or debate from the event log | event log (SSE tail), agent logs, fusion-harness run folders, `playback.py` |
| 11 | **Blog and User Guide** | The weekly blog: latest post, archive, and each post's facts file side by side so every claim can be traced; a draft awaiting approval (private mode only); the User Guide rendered, with its "Matches Charter vX" status and change history | `blog/`, `blog/_facts/`, `docs/USER-GUIDE.md`, `private/outbox/pending/*-blog-*`, git log |
| 12 | **Discussion** | Every board thread, fusion-harness deliberation, sprint debate, and governance debate, searchable by date, participant, and topic, linked to the decisions they led to | `org/board/`, `sprints/*/deliberation/`, `governance/records/` |
| 13 | **Projects (products)** | Every project as a product: its current released version (open it, try it, read its release notes), version history (`version-001`, `version-002`, …), spec, and the full discussion. A comment and suggestion box appends human input to the project's discussion. Proposed projects are listed too | `projects/*/PROJECT.md`, `versions/`, `spec.md`, `discussion.md`, `projects/PROPOSED.md` |
| 10 | **Versioning** | Both repos' HEADs; commits ahead of the remote (with a reminder that the Steward pushes public); verification status of the event log, Charter log, edicts, and cases; the last backup; the time-travel selector | git, `eventlog.py verify`, `charter-verify.py`, `edict.py check`, `case.py check` |

**Header on every page:**
- Charter version;
- sprint and phase;
- a stop-switch indicator (on or off);
- the "as of" commit and event;
- a public or private mode badge.

## 4. KPIs and OKRs

- **`org/OKRS.md`** holds the quarter's objectives and measurable key
  results.
  - The Steward sets them by edict; agents may propose changes through a
    sprint or amendment.
  - Seeded with a draft for the Steward to confirm.
- **`org/KPIS.md`** defines each KPI: name, formula, source, target, and
  owner.
- **`agents/bin/metrics.py`** computes every KPI from records, writes
  `metrics/YYYY-MM-DD.json`, and the Auditor commits it daily. That gives the
  KPIs full, versioned history.

## 5. Design

- A clean, dense operations-console look. Light and dark themes, both
  readable; color never the only signal.
- Navigation: a left rail with the thirteen panels. The header shows current
  state. Every item links to its source file (on GitHub for public files,
  local path for private ones).
- Decisions view: case card, then an evidence drawer, then a citation graph.
  Every claim is clickable back to its source.
- Live stream: an agent grid like fusion-harness's own UI, colored per agent;
  debates show positions side by side, then rounds, then ballots sealed until
  reveal.
- Accessibility: keyboard navigable, sensible headings, and live regions for
  the stream announced politely.

## 6. Privacy and safety

- It binds to 127.0.0.1 only and refuses any other address.
- The comment box is the only write. It accepts plain text only, rate-limits
  itself, and can't touch anything except a project's `discussion.md`.
- It never shows `agents/.env` or anything decrypted from
  `private/secrets/`.
- Public mode hides all private-repo sources and says so on the panels
  affected.
- Page content from records is rendered as text, never as HTML.

## 7. Build order (each step is a sprint item or `#decision`; stop for review)

1. Server skeleton, header, Mission, Charter, and Versioning panels, plus time
   travel. This is **v1, built during setup**.
2. **Projects (products) with comments**; decisions with evidence; current
   sprint; last sprints.
3. `org/KPIS.md`, `metrics.py`, daily snapshots, and the KPIs + OKRs panel;
   Progress.
4. Calendar, with the `.ics` export, and the Blog and User Guide panel.
5. Live stream: agent columns, the debate view, and replay.
6. Public mode, design review by Media, and acceptance by the Auditor against
   this spec.
7. **Release (Charter P10, Article 18.6):** a static export of public mode,
   published on GitHub Pages from the public repo once the Steward approves.
   It's rebuilt on each push. A static site can't accept writes, so its
   comment box links to the project's thread in GitHub Discussions on the
   public repo, and the Scribe imports those comments into the project's
   `discussion.md` every week.

## 8. Acceptance

- Every panel shows an "as of" commit or event, and time travel re-renders
  the whole dashboard at a past point.
- Deleting `dashboard/` and rebuilding it from git loses nothing.
- Public mode shows no private data.
- Live stream shows a running agent within 2 seconds of its events, and
  replays any past run.
- Opens with one command, runs locally, and needs no external services
  beyond an optional CDN charting library.

---

## Primary view: the floor

(Added 2026-09-24, edicts E-0056 and E-0060; version 002.)

- **The world:** four rooms around a plaza. The **Council** holds the four
  officers around a table; the **Lab** holds Researcher and Ideas; the
  **Studio** holds Media and Social; the **Workshop** holds the Prototyper.
  **The Record** is a glowing monument in the plaza showing the event count.
- **Characters:** each agent has its class's hat, its own color, emblem, and
  motto. Working agents bob and show typing dots; idle ones stand still;
  paused ones fade with "zz"; stuck ones (in a run for more than 2 hours)
  show a red "!"; agents that haven't run yet are translucent.
- **Speech:** each agent "says" its latest board post (`### <key> ·
  <timestamp>`), or else its latest recorded action. One bubble per room,
  from its latest speaker in the last 30 minutes.
- **Motion and meetings:** each recorded action sends a scroll to the Record.
  During `deliberating` and `voting`, everyone meets at the Council table.
- **HUD and side panel:** state, verification seal, sprint and phase, and the
  week as a progress bar; the Steward's queue, the pipeline, and the
  conversation.
- **Other views:** `/scope`, `/records`, and **`/history`** (version 001's
  time travel by commit, event, or date, and the Charter diff), one click
  away from every page.

## Agents: bios and spawning

(Added 2026-09-24, edicts E-0058 and E-0060; Charter Article 3.8.)

- **Bio:** click any agent for its class, vote, room, model, schedule (every
  N minutes, daily cap, last and next run), installed modules (read from its
  tool grants), requested modules, duties, and full prompt (hidden in public
  view).
- **Tray and wizard:** a tray of spawnable classes below the floor; a
  five-step wizard (class, name and focus, room and look, schedule, review)
  that **drafts a membership motion** through `spawn.py`. It creates nothing:
  the proposed agent shows as a translucent **ghost** until the motion passes.
  Private view only (Article 18.7(b)).
- **Clone:** on any maker's bio; officers can't be cloned.

## Conversations

(Added 2026-09-24, edict E-0062.)

- A conversation is a board thread with two or more participants (posts in
  the `### <key> · <timestamp>` format; the Steward posts as `rex`).
- Up to five active ones (last 48 hours) show as pills between their
  participants, color-coded by thread tag, placed where they cover no one,
  and pulsing on new messages.
- Clicking one opens a live chat in the style of iOS Messages: agents in grey
  bubbles with names and class-colored avatars; the Steward in blue on the
  right; time separators after 15-minute gaps; participants' actions as small
  centered notes (runs of file edits collapsed; bookkeeping left out; hidden
  in public view); a typing indicator for anyone working now.
- Read-only: replies go on the board or as a `#ruling`.

## Security (applies to every view)

- Binds 127.0.0.1 and answers only `Host: 127.0.0.1` or `localhost` (no DNS
  rebinding); `Referrer-Policy: no-referrer`; no framing.
- Public mode never reads the private event log (only its count).
- No external requests: fonts are served locally from `dashboard/fonts/`.
