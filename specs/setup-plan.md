# Setup plan (for Claude Code)

Stop for Rex's review after each step marked ⏸.

## Step 1: Environment check ⏸
- Run `setup/bootstrap.sh --dry-run` and report what's missing.
- For herdr itself, follow the current install docs at herdr.dev (don't guess
  the command).
- Confirm the Claude Code headless flags used in `agents/bin/run-role.sh`
  (`-p`, `--allowedTools`, `--max-turns`) against `claude --help`. Fix the
  script if they differ.
- Find out how Rex's Grok agent is run (a CLI name and headless flag). Set
  `SOCIAL_AGENT_CMD`, or ask Rex.

## Step 1b: Repositories and auth ⏸
- Confirm Rex's SSH key can reach both `git@github.com:Verafyai/Collective.git`
  and `git@github.com:Verafyai/CollectivePrivate.git`
  (`git ls-remote <url>`). Both must exist on GitHub, and **CollectivePrivate
  must be private**; ask Rex to confirm on github.com.
- `brew install age`, then `agents/bin/secrets.sh keygen`. Remind Rex to back
  up `~/.config/age/collective.key` somewhere safe.
- After Rex fills `agents/.env`: `agents/bin/secrets.sh seal`.

## Step 1c: Link GitHub and push ⏸
1. `ssh -T git@github.com`: confirm GitHub recognizes Rex's key.
2. `git ls-remote git@github.com:Verafyai/Collective.git` and the same for
   `CollectivePrivate`: both must exist, and ask Rex to confirm on github.com
   that **CollectivePrivate is private**.
3. `agents/bin/repos.sh init`, then `setup/commit-edicts.sh` (one commit per
   edict, in the private repo), then
   `agents/bin/repos.sh commit "The Collective at Charter v$(sed -n 's/^Charter version: //p' CHARTER.md | head -1)"`.
4. `agents/bin/repos.sh push` pushes the **private** repo.
5. Show Rex what the public repo will contain (`git ls-files | head -50` and
   a count), then ask him to run `agents/bin/repos.sh push --public`
   himself. Never push the public repo yourself.
6. Tag the Charter: `python3 agents/bin/charter.py tag`.

## Step 1d: Credits
- For every plugin and tool installed, confirm its license and fill in the
  "see repo" entries in `CREDITS.md` (Charter P4).

## Step 2: Install ⏸
- Run `setup/bootstrap.sh` (add `--with-optional` only if Rex says so).
- For each installed plugin:
  - read its README;
  - write `docs/plugin-notes.md` covering what it does, its commands, config
    location, and anything that sends data off the machine.
- Confirm the workspace template landed in herdr-plus's `projects/` folder.

## Step 3: Configure plugins ⏸
- **tsk** (fixed statuses, no custom columns or labels; see org/STRUCTURE.md):
  - the store is `org/tasks/` (`TSK_STATE_DIR`, exported with
    `TSK_NO_UPDATE_CHECK=1` by `agents/config.env`);
  - statuses stand for the columns (open = backlog, ready = approved,
    started = in progress, review, done); the owner office is the task's
    thread;
  - document the agent CLI commands in plugin-notes;
  - the "board" tab of the template runs the TUI on that store.
- **herdr-projects:** configure a coordinator thread for the Project Manager
  and a worker
  thread per role, if it supports that. Otherwise note how it could be used
  later.
- **herdr-remote:** Telegram is deferred by the Steward (E-0039); approvals
  stay with `agents/bin/approve.sh`. If the relay is set up later, follow the
  safeguards in plugin-notes (token set, no tunnel, no shell panes).
- **agent-progress:** installed but not configured (its Configure action
  hooks the Steward's global Claude settings). **herdr-radar:** default
  config (E-0046). **memex:** held, not installed (E-0045).

## Step 3b: Dashboard, project P-001 version-001 ⏸
- Build version-001 of the dashboard (`projects/001-dashboard/`: read its
  spec.md, versions/version-001.md, and discussion.md first):
  - server skeleton (`agents/bin/dashboard.sh`, Python standard library,
    127.0.0.1:4848);
  - header, Mission, Charter, and Versioning panels;
  - time travel.
- Fill in version-001's Changes and Release notes, run the Auditor's checks,
  then `python3 agents/bin/projects.py release 1 1`.
- Commit it, then open http://127.0.0.1:4848 for Rex to review. The later
  versions (see the project's roadmap) become sprint items.

## Step 4: Build the missing glue ⏸
- `agents/bin/x_post.py`: posts one approved file to X using the official API
  with credentials from `agents/.env`. It reads the post text and optional
  media path from the file, prints the resulting URL, and appends it to the
  file. Include `--dry-run`. Test **only** in dry-run.
- `agents/bin/tts.sh`: generate a voiceover from a script using the provider
  in `.env`. Default to a local open-source TTS (e.g. Piper) with a stock
  voice.
- `agents/bin/notify.sh`: send a short message to Rex (Telegram, via
  herdr-remote if it supports that). Wire it to `NOTIFY_CMD`.
- A launchd plist (macOS) or cron entry that runs
  `herdr-plus open "Collective"` at login, so the org restarts after a reboot.
  Install it only after Rex approves.

## Step 5: Smoke test ⏸
- Run each role **once** (`agents/bin/run-role.sh <role>`), not looping, and
  check:
  - Researcher briefs one seed paper;
  - Ideas writes one proposal;
  - the Lawyer writes an opinion, the Auditor runs every verifier, and the
    Project Manager makes a digest;
  - Social drafts an intro thread into `private/outbox/pending/` (nothing posted);
  - Prototyper and Media wait for real tasks, so only confirm they start and
    exit cleanly.
- Verify these safety paths:
  - `touch org/STOP` halts every role;
  - `x-post.sh` refuses unapproved files;
  - daily caps stop runs.
- Summarize results for Rex, with the paths of everything produced.

## Step 6: Sprint 0 dry run ⏸
- Run a full sprint in simulation mode (`python3 tests/test_sprint.py`), then
  one real planning round with the theme **"What is the best course of action
  for Verafy right now?"**:
  1. `python3 agents/bin/sprint.py open --theme "..."`;
  2. each role writes its proposal (one run each);
  3. a fusion-harness deliberation session;
  4. freeze;
  5. a ballot session;
  6. tally.
- Stop before `steward --approve`, and show Rex the tally, the plan preview,
  and the deliberation transcript.

## Step 7: Go live ⏸
- With Rex's OK, run `touch private/.setup-complete`, then ask Rex to re-run
  `./launch.sh`, which switches to the operating workspace with every office
  running.
- With Rex's OK, open the workspace: `herdr-plus open "Collective"`.
- Watch the first full cycle. Write the first `org/LEARNINGS.md` entry about
  the setup.
- Remind Rex:
  - label @VerafyAI as automated on X, and put "AI-run, operated by Rex St.
    John" in the bio;
  - approvals are required for all posts for the first 30 days.
