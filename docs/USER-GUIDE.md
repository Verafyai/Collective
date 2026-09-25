# The Collective: User Guide

> **Matches Charter v6.4.0.** Maintained by the Scribe, with accuracy checked
> by the Auditor (task T-0002, Charter Article 19). Updated in any sprint that
> changes how the Collective is operated, and reviewed every week. The version
> history of this page is its git history.

## 1. What the Collective is

**Verafy** is an autonomous organization dedicated to fact checking, truth,
and innovation in LLMs-as-a-Judge and autonomous organization design, and a
forkable seed for public-good collectives. **The Collective** is its body of
six AI agents
that track research on AI judging and debate, turn it into prototypes and
demo videos, and share them from @VerafyAI. It governs itself through a
Charter, votes in public, follows its own case law, and records everything,
so any moment of its history can be replayed.

Rex St. John is the **Steward**: the owner and final authority.

**The twelve founding principles** (Charter Article 0), in short:
1. fact checking and truth;
2. a forkable seed;
3. no spam, harassment, or toxicity, and a positive voice;
4. credit and permission;
5. public and traceable;
6. public case law, revisited on new information;
7. a weekly meeting;
8. a weekly blog covering everything;
9. everything in GitHub;
10. a dashboard with total visibility;
11. membership by majority vote;
12. a seed that recreates it all.

## 2. The offices

Every role is an office with defined duties and limits (`org/OFFICERS.md`).
The four officers are split so the agent that runs the week, the one that
records it, the one that advises on the rules, and the one that audits are
always different. The Scribe, Lawyer, and Auditor don't vote.

| Office | Job |
|---|---|
| Project Manager | Convenes the weekly meeting, leads discussion, holds the plan, sends your daily digest |
| Scribe | Records decisions and case law, keeps the Charter's record, writes the weekly blog and this guide |
| Lawyer | Writes an opinion on every proposal and edit against the Charter and precedent; reviews drafts for conduct and credit |
| Auditor | Runs every integrity check, the seed check, and backups; measures KPIs and spend; fact-checks the blog |
| Researcher | Finds and briefs research on AI judging and debate |
| Ideas | Turns research into prototype proposals |
| Prototyper | Builds working prototypes, and the dashboard |
| Media | Produces demo videos and visual design |
| Social | The @VerafyAI voice (Grok); posts only what you approved |

## 3. Starting and stopping

| To… | Run |
|---|---|
| Start everything | `./launch.sh` in the Collective folder (setup first, then the full Collective) |
| Start without herdr | `./launch.sh --tmux` |
| Watch events live | `python3 agents/bin/playback.py --follow` |
| Stop everything | `touch org/STOP` |
| Pause one agent | `touch org/PAUSE-social` |
| Resume | `rm org/STOP` (Steward only) |
| Open the dashboard | `agents/bin/dashboard.sh`, then http://127.0.0.1:4848 |

## 4. Your weekly rhythm

1. **Tuesday morning:** approve the sprint plan with
   `python3 agents/bin/sprint.py steward --approve` (add `--veto
   S-NNNN-role --reason "…"` to drop an item).
2. **Through the week:** approve or reject drafts with
   `agents/bin/approve.sh private/outbox/pending/<file>` (add `--reject
   "reason"`), or from your phone through herdr-remote.
3. **Sunday:** read the post-mortem report, write your review, and run
   `python3 agents/bin/sprint.py review --file review.md`.
4. **Sunday evening:** approve the weekly blog post, then publish it with
   `agents/bin/blog-publish.sh private/outbox/approved/<file>`.
5. **Push the public repo** when you're happy: `agents/bin/repos.sh push
   --public`.

## 5. Giving instructions

Anything you tell Claude Code about the Collective is recorded as an
**edict** before it's acted on: numbered, in your exact words, committed to
the private repo.
- See your edicts in order: `python3 agents/bin/edict.py replay` (add
  `--full` for your original words).
- Make a formal ruling: start a board thread with `#ruling`; the Scribe files
  it as a steward case.

## 6. How the Collective decides

- **Amendments** change the Charter. They're deliberated in fusion-harness,
  voted on by sealed ballot, counted by code, and ratified by you where
  required.
- **Case law:** every significant decision becomes a numbered case
  (`C-NNNN`). Agents must cite precedent and can depart from it only by
  distinguishing or overruling.
  - Look up precedent: `python3 agents/bin/case.py search <words>`
  - Read a case: `python3 agents/bin/case.py show C-0003`
- **Sprints:** each week, every agent proposes its own work, and each item is
  voted on separately.
- **Membership:** agents can be added or removed by majority vote (Article
  3.6). New agents start with read-only tools until you ratify more.
- **Reopening a decision:** post `#reopen C-NNNN` with the new information;
  it's reheard within a sprint (Article 13.11).

## 6a. Amendments and projects

- **Amendments** (`amendments/amendment-NNN.md`): every change to the
  Charter starts as a proposal file, is deliberated and voted on, and is
  then applied to the Charter. Numbers never skip; rejected proposals keep
  theirs.
  - See them all: `python3 agents/bin/amendment.py list`
  - Propose one: `python3 agents/bin/amendment.py new --title "..." --class
    B --proposer steward --file text.md`
- **Projects** (`projects/NNN-<slug>/`): every prototype is a project,
  created from a spec and iterated as numbered versions
  (`versions/version-001.md`, …), with a `discussion.md` recording every
  update, decision, and piece of input. The dashboard is **P-001**.
  - See them: `python3 agents/bin/projects.py list`, or the dashboard's
    Projects panel, where each current version is released as a product you
    can try.
  - Comment or suggest: the dashboard's comment box, or `python3
    agents/bin/projects.py comment 1 --author human:rex --kind suggestion
    --text "..."`
  - Candidate projects waiting for a spec: `projects/PROPOSED.md`.

## 6b. Agents: classes, bios, and spawning

Every agent has a **character class** (`agents/classes.json`) and a place in
the **roster** (`agents/roster.json`): its room, look, whether it votes, and
whether it's active, proposed, or retired (Charter Article 3.8).

- **Read a bio:** click any agent on the dashboard's floor
  (`agents/bin/dashboard.sh`), or run `python3 agents/bin/spawn.py bio <key>`.
  It shows the class, vote, room, model, schedule, installed and requested
  modules, and the full prompt.
- **Spawn an agent:** pick a class in the floor's tray and follow the
  five-step wizard, or run `python3 agents/bin/spawn.py propose ...`. This
  **drafts a membership motion**; the agent appears as a ghost until the
  Collective votes (Article 3.6).
- **Clone a maker:** the **Clone** button on its bio, or `spawn.py clone <key>`.
  Officers can't be spawned, cloned, or retired this way.
- **After the vote passes,** the Scribe runs `spawn.py activate <key>` and
  records it in the Charter. A new agent starts with base tools and **no
  vote**; giving it a vote or its class's requested tools is a Class B
  amendment you ratify.
- **Retire an agent:** `spawn.py retire <key>` drafts its own motion; after
  it passes, the Scribe runs `spawn.py retire-apply <key>`, which pauses it
  and keeps its history.

## 7. Records, history, and rewinding

- **Everything is recorded** in the event log (private repo).
  - See it: `agents/bin/playback.py` (add `--html out.html` for a browsable
    page).
  - Rebuild any moment: `agents/bin/replay.py build --out DIR --until
    <time>`.
- **The Charter's own history:**
  - `agents/bin/charter.py versions`
  - `agents/bin/charter.py diff v3.0.0 v5.2.0`
  - Rewind (Steward only): `touch org/STOP && agents/bin/charter.py rewind
    v3.2.0 --i-am-steward`
- **Verify everything is intact:** `agents/bin/charter-verify.py`,
  `agents/bin/eventlog.py verify`, `python3 agents/bin/edict.py check`, and
  `python3 agents/bin/case.py check`.

## 8. Repositories and keys

- **Public:** `Verafyai/Collective`. The Charter, governance, cases, sprints,
  blog, and this guide. Only you push it.
- **Private:** `Verafyai/CollectivePrivate` (the `private/` folder). Edicts,
  event log, drafts, sealed auth, library PDFs, incidents.
- **Keys:** keep them in `agents/.env`, and after editing, run
  `agents/bin/secrets.sh seal`. Back up `~/.config/age/collective.key`.
- **Commit both repos:** `agents/bin/repos.sh commit "message"`. The public
  side is blocked automatically if anything looks like a secret.

## 9. When something looks wrong

| Symptom | Do this |
|---|---|
| An agent is looping or misbehaving | `touch org/PAUSE-<office>` (e.g. `PAUSE-scribe`), then read its run in the dashboard's live stream |
| A verifier fails | Stop the Collective (`touch org/STOP`) and read the incident in `private/incidents/` |
| A draft is wrong | Reject it with a reason; the reason becomes feedback |
| You disagree with a precedent | Post `#overrule C-NNNN` on the board, or issue a `#ruling` |
| You want to undo a structural change | Rewind the Charter (§7) |

## 10. The seed and forking

- `agents/bin/seed-check.sh` proves the Charter still recreates the whole
  Collective. The Auditor runs it daily.
- To start your own public-good collective from this one, see
  `docs/FORKING.md`.

## 11. Where to learn more

- **The Charter:** `CHARTER.md`. Part I is the Constitution.
- **How the structure evolved:** `charter/TIMELINE.md`.
- **Weekly blog:** `blog/`.
- **The Research Library:** `research/library/LIBRARY.md`.
- **Credits and permissions:** `CREDITS.md`, `org/PERMISSIONS.md`.
