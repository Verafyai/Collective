---
project: P-001
version: 003
title: Rooms, terminals, cleaner chats, permissions, huddles, whiteboards, and a demo mode
status: building
date: 2026-09-24
---

# The Collective Dashboard · version 003 · Rooms, terminals, cleaner chats, permissions, huddles, whiteboards, and a demo mode

## Plan

Everything the Steward asked for after version 002 (edicts E-0064, E-0066–E-0077), under Charter
Articles 3.9, 18.7(c)–(f), and 18.8 (A-0021 to A-0024, Charter v6.8.0):
- idle motion: agents bob gently and blink now and then;
- status icons over heads (Blocked, Awaiting approval, Needs instructions, Awaiting its
  next run, Busy), explained on hover, derived from the records;
- drag an agent to another room (the roster's room, through `spawn.py move`);
- **Open terminal** on every bio: a recorded conversation with that agent, in a herdr tab
  or a standalone Terminal window;
- chats: each agent's own figure as its avatar, a one-line summary with **Advanced** for
  the full text, and the Steward's comment box (a direction can be recorded as an edict);
- floating speech bubbles over the speaker while no chat is open;
- a **Permissions** tab on every bio: capability checkboxes (ratified by the click) and
  ranks, with the Charter's locks shown;
- a whiteboard in every room that opens a kanban of the tsk tasks (states × offices);
- the coffee machine and the **Huddle** button;
- `?demo=1`: labeled, browser-only simulated activity.

## Changes

- `dashboard/static/floor-extras.js` (new): all of the above on the floor.
- `dashboard/server.py`: post summaries; status flags; `/api/tasks`; `/api/agents/<key>/permissions`;
  guarded writes for move, terminal, permissions, chat comments, and huddles (private view,
  same origin, rate-limited); queue ignores review notes.
- `dashboard/floor.html`: loads the module; `api` is replaceable for the demo mode.
- `agents/bin/spawn.py` (`move`), `run-role.sh` (`--interactive`), new `terminal.sh`,
  `perms.py`, `supervise.py`; tests extended (Part V via A-0021 to A-0024).

## Release notes

The floor comes alive: agents bob and blink, show what they're waiting on, and can be
dragged to another room. Click an agent to talk with it in a terminal, or to set its
permissions and rank. Chats read cleanly, with summaries, avatars, and your own comments,
and new messages float over the speaker's head. Each room's whiteboard opens the task
board, the coffee machine calls a huddle, and `?demo=1` shows simulated activity under a
SIMULATED banner.

**Known limits:**
- The terminal hasn't been used for a real conversation yet: it was built and its guards
  tested, but opening a session costs a model call, so the first one is yours. For Social
  (Grok) the transcript is recorded, but your messages aren't copied to the board.
- Tasks can't be dragged on the kanban; it shows the board read-only.
- "Reassign tasks" for supervisors has no command yet (tsk has no reassignment); pausing
  and unpausing do.
- Permission grants apply to the offices' tools at once; the Scribe then records them in
  Part V (agents/config.example.env), so the Auditor will flag the gap until then.
- Status icons read the records, so "Needs instructions" appears only for `#question`
  threads with `@rex`.

## Links

- Edicts E-0064, E-0066–E-0077; amendments A-0021–A-0024 (Charter v6.8.0).
