# The Collective Dashboard: guide (project P-001)

A local window onto the whole Collective, computed live from its records.

```
agents/bin/dashboard.sh            # http://127.0.0.1:4848, private view
agents/bin/dashboard.sh --public   # public view: nothing from the private repo, and no writes
```

## The floor

- **Rooms are projects.** An isometric office where every agent works in a
  project room with a codename (Project Valkyrie is this dashboard) around the
  glowing Record, Central Command. Click a room's name to rename it. **＋ New
  project** takes a codename, a spec, and toggles for agent types to spawn
  with it, and the project gets its own room.
- **The agents:** each has its own color, class hat, and emblem. Drag one to
  another room to move it (into a project room, it gets a task there). Icons
  over heads say what it's waiting on: ⚙️ busy, ⏰ its next run, ✋ your
  approval, ❓ instructions, ⛔ blocked; hover for details. An agent with no
  task lies down asleep. A proposed agent is a translucent ghost until it's
  approved.
- **Room chats:** one chat bubble per room, counting what the agents there
  have said. Open it to read the conversation and comment; the room's agents
  answer you at once. When someone speaks, a faint summary rises above the
  bubble. The whole Collective shares one chat only during a huddle.
- **Telephones:** every room's phone is wired to Central Command; click one to
  open that room's chat, and watch a spark run down its cord on a new line.
- **Whiteboards** open a kanban of everyone's tasks. The **coffee machine**
  (or ☕ Huddle) calls everyone together; ↺ Reset floor sends them back.
- **The camera:** ＋/− or the wheel to zoom, drag empty floor to pan, ⟲/⟳ to
  turn the floor, ⌂ to reset.
- **Profiles:** click an agent for its bio, activity, Permissions tab, **⌨ Open
  terminal** (a talk in the terminal drawer, where it greets you first), and
  **View in Weave**.
- **The side panel:** your queue, proposed agents, the pipeline, and the live,
  numbered feed of events.

## The top bar

- **Status, checks, sprint, and the week** as a clock with a needle at now.
- **⌨ Terminal:** a drawer of real terminals on this Mac (a shell, herdr, or a
  talk with an agent), recorded (Article 18.7(h)). See the section below.
- **⚖️ Decisions:** the Court (P-006). An isometric courtroom where advocates
  on different model families argue a case from admitted exhibits, a Judge
  rules, a jury casts sealed ballots, and the scales above the bench tilt
  with the certainty score. The docket, case detail, replay, and **File a
  case** are in the side panel; the courthouse on the floor opens it too.
  Provisional until amendment A-0051 passes.
- **Weave:** recent traced runs, every agent, and the eval scoreboard, with
  links to W&B Weave (P-005). Private view only; the key never reaches the
  browser.
- **Scope** (`/scope`): the control plane: who's working, what's waiting on
  you, the pipeline, the last hour, and the event stream.
- **Records** (`/records`): projects (with a comment box), case law,
  amendments, the Charter with its history, sprints and OKRs, edicts (private
  view), and live verification of every integrity check.
- **History** (`/history`): the Collective as it stood at any past moment.

Python standard library only (the Weave queries run in `agents/.venv`); binds
to 127.0.0.1 only. Spec: `projects/001-dashboard/spec.md`.

## The web terminal (P-001 version 004; Charter Article 18.7(h))

- **⌨ Terminal** in the top bar opens a drawer of real terminals on this Mac, in
  the Collective folder. **+ shell** opens your login shell; **+ herdr** opens the
  full herdr UI (it may take over your own herdr window). **⌨ Open terminal** on
  an agent's profile opens a talk with that agent.
- Resize by dragging the drawer's top edge (or ▴ for taller); the shell is told
  its new size. Selecting text copies it.
- Everything is recorded: each session's start and end, every typed line, and the
  output (up to 5 MB), all redacted for secrets. Lines typed while the terminal
  doesn't echo (a password prompt) are counted, never recorded.
- A closed session says so; **Reconnect** starts a new one and never resumes the
  old one. At most 4 terminals; each ends after 30 minutes idle.
- Refused in public view, from any other origin, and without a fresh one-time token.
