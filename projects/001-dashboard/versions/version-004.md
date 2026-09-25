---
project: P-001
version: 004
title: A real terminal in the browser; projects, rooms, and the camera
status: building
date: 2026-09-24
---

# The Collective Dashboard · version 004 · A real terminal in the browser; projects, rooms, and the camera

## Plan

Everything the Steward asked for after version 003 (edicts E-0083, E-0087 to E-0095), under
Charter Articles 18.7(h)–(j), 18.8, and 21.2 (A-0028, A-0029, A-0030):
- a real terminal in the browser: a shell, herdr, or a talk with one agent;
- the camera: zoom, pan, and turn the floor;
- rooms are projects with codenames; **＋ New project** from a spec, with toggles for agent
  types to propose for it (E-0096); agents dragged into a
  project room get a task and start talking there;
- one chat per room, its pill over the room, no dotted lines (E-0098); the Collective-wide chat only in a
  huddle; ghosted summaries above the chat icon instead of standing speech bubbles;
- a telephone in each room wired to central command;
- idle agents with no task sleep on the floor;
- the bio keeps its scroll position and open sections when the floor updates;
- the floor's subtitle, "Return to Office".

## Changes

- `dashboard/shell_bridge.py` (new, Part V): the WebSocket terminal; the `agent` command.
- `dashboard/static/terminal-drawer.js` (new), `dashboard/vendor/xterm/` (vendored,
  SHA256SUMS), `dashboard/static/camera.js` (new).
- `dashboard/static/floor-extras.js`: sleepers, room names and new rooms, phones, per-room
  chats and whispers, the New project form, the side panel keeping its place.
- `dashboard/server.py`: `/ws/shell`, `/api/shell/token`; `/api/conversations?by=room`
  and `room-<room>` chats; `asleep` and `open_tasks` on each office; `rooms` in `/api/live`;
  `/api/projects/new` and `/api/rooms/<room>/rename` (on A-0030's ratification); a move into a
  project room assigns work (on A-0030's ratification).
- `dashboard/floor.html`: a rotatable projection; frames every room; the subtitle.
- `agents/bin/rooms.py` (new), `agents/bin/spawn.py` (rooms from `org/rooms.json`);
  tests extended (`tests/test_shell.py`, `tests/test_dashboard.py`).

## Release notes

The floor becomes a set of projects. Each room carries a codename and has its own chat
and a telephone to central command; you can start a new project from a spec and drag
agents into it. Idle agents nap. You can zoom, pan, and turn the floor, and open real
terminals, including a talk with any agent, without leaving the page.

**Known limits:**
- Agents with `Bash(python3:*)` (Prototyper, Media) can run any Python, so no in-process check
  (`perms.py --steward`, `rooms.py`) can stop them. It waits on your decision on governance keys
  or narrower grants (v003 item 1, still open).
- In a terminal talk with an agent, your messages are filed as one edict per session, not
  one per direction (v003 item 2, partly open).
- Agents start on a project at their next scheduled run, not the moment you drop them.
- A room chat shows the posts of the agents seated there now; if you move an agent, its
  old posts move with it.
- Turning the floor keeps the meeting seats laid out for the first view, so a sprint
  meeting may look crowded when the floor is turned.
- New rooms have no whiteboard yet.

## Links

- Edicts E-0083, E-0087 to E-0095; amendments A-0028, A-0029, A-0030 (ratified by E-0097). Supersedes version 003, which was never accepted: its fixes are in this version.

