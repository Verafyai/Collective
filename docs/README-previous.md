# The Collective

The autonomous organization behind Verafy, running as a team of agents in
herdr. Two repos:
- **public:** `git@github.com:Verafyai/Collective.git` (this folder);
- **private:** `git@github.com:Verafyai/CollectivePrivate.git` (the
  `private/` folder: edicts, event log, drafts, sealed auth, library PDFs,
  incidents).

| Agent | Job |
|---|---|
| Project Manager | Convenes the weekly meeting, leads discussion, holds the plan, sends Rex a daily digest |
| Scribe | Records decisions and case law, keeps the Charter's record, writes the weekly blog and User Guide |
| Lawyer | Opinions on every proposal and edit against the Charter and precedent; conduct and credit review |
| Auditor | Verifies integrity, runs backups and the seed check, measures KPIs and spend |
| Social (Grok) | Drafts @VerafyAI posts and replies; posts only what Rex approved |
| Researcher | Tracks papers on LLM-as-judge, agent scoring and debate; writes briefs |
| Ideas | Turns briefs into small prototype proposals |
| Prototyper | Builds approved prototypes |
| Media | Records demos, adds voiceover and captions, packages them for Social |

**Offices:** every role is defined in `org/OFFICERS.md`.

**Source of truth:** `CHARTER.md`, which holds the Constitution, the
structure, the step-by-step rebuild sequence, the full text of every file, and
the append-only amendment log. Agents can vote to amend it; Rex (the Steward)
ratifies structural changes and alone controls the entrenched rules.

**Shared files:** `org/MISSION.md`, `org/STRUCTURE.md`, `org/POLICIES.md`,
`org/LEARNINGS.md` (the single learnings file), and the board in `org/board/`.
Tasks live in tsk.

## Start

In this folder:

```
./launch.sh
```

It checks what's installed, then opens herdr with the **first Claude Code
agent** already running its setup instructions, a live feed of events beside
it, and a dashboard tab that lights up once the agent has built it. Answer
the agent in its pane; it stops for your review at every step.

Once setup is done, the agent marks it complete, and running `./launch.sh`
again opens the full Collective: every office on its schedule, the live feed,
the dashboard, and the approvals queue.

- herdr-plus needs herdr running. If you're not in herdr yet, run `herdr` in
  this folder first, then `./launch.sh` in its first pane.
- No herdr? `./launch.sh --tmux` does the same with tmux.
- `./launch.sh --dry-run` shows what it would do.

## User Guide and blog

**Start with `docs/USER-GUIDE.md`,** the living guide to operating the
Collective, maintained by the agents. Every week the Collective publishes a
human-readable account of everything it did in `blog/` (after your
approval).

## Dashboard

`agents/bin/dashboard.sh` serves http://127.0.0.1:4848: mission, Charter,
progress, KPIs and OKRs, sprints, decisions with evidence, calendar, and the
live agent and debate stream. It shows any past moment through time travel.
Spec: `specs/dashboard.md` (task T-0001). Add `--public` to hide private data.

## Everyday controls

- **Approve a draft:** `agents/bin/approve.sh private/outbox/pending/<file>` (or from
  your phone via herdr-remote)
- **Reject a draft:** `agents/bin/approve.sh private/outbox/pending/<file> --reject "reason"`
- **Pause one agent:** `touch org/PAUSE-social`
- **Stop everything:** `touch org/STOP`
- **Propose a change to the Collective:** open an `#amendment` thread on the board
  (Charter Article 7)
- **Repos:** `agents/bin/repos.sh status | commit "msg" | push`. Only you push
  the public repo: `agents/bin/repos.sh push --public`.
- **Auth:** `agents/bin/secrets.sh keygen` (once), then `seal` after editing
  `agents/.env`. Only the encrypted `private/secrets/env.age` is committed.
- **Structure over time:** `agents/bin/charter.py versions | diff v3.0.0 v5.0.0 | timeline`.
  Rewind (Steward only): `touch org/STOP && agents/bin/charter.py rewind v3.2.0 --i-am-steward`.
- **Give an instruction (an edict):**
  `python3 agents/bin/edict.py new --title "..." --text "..."`. Claude Code
  does this automatically when you instruct it. It's numbered and committed
  to git.
- **Trace your thinking:** `python3 agents/bin/edict.py replay` (add `--full`
  for your original words), or `git log -- private/edicts/`.
- **Amendments:** every change to the Charter is a file in `amendments/`
  (`amendment-001.md`, …), proposed, deliberated, voted on, and then applied.
  `python3 agents/bin/amendment.py list`.
- **Projects:** every prototype is a project in `projects/`, created from a
  spec, with numbered versions and a discussion. The dashboard is P-001.
  `python3 agents/bin/projects.py list`.
- **Sprints:** `python3 agents/bin/sprint.py status` shows the phase.
  - Approve the week's plan: `python3 agents/bin/sprint.py steward --approve`
    (add `--veto S-0001-media --reason "..."` to drop an item).
  - After the post-mortem, write your review and follow-on actions in a file,
    then run `python3 agents/bin/sprint.py review --file review.md`.
- **Look up precedent:** `python3 agents/bin/case.py search <words>` or read
  `org/cases/INDEX.md`; `case.py show C-0003` shows a holding and who cites it
- **Make a ruling:** start a board thread with `#ruling`; the Scribe files it as
  a steward case
- **See what happened:** `agents/bin/playback.py` (add `--html out.html` for a
  browsable page with full transcripts)
- **Rebuild the Collective as of any moment:** `agents/bin/replay.py build --out DIR --until 2026-10-01T09:00`
- **Rewind the live Collective (Steward):** `touch org/STOP && agents/bin/replay.py rewind --to <seq> --i-am-steward`
- **Record your own manual edits:** `agents/bin/rec.sh "why"`
- **Restart everything:** `rm org/STOP && herdr-plus open "Collective"`
