---
project: P-001
version: 001
title: Skeleton, header, Mission, Charter, Versioning, time travel
status: released
date: 2026-09-24
---

# The Collective Dashboard · version 001 · Skeleton, header, Mission, Charter, Versioning, time travel

## Plan

Spec §7, step 1, built by the setup session (setup plan Step 3b):
- `agents/bin/dashboard.sh`: Python standard-library server on 127.0.0.1:4848;
- the header on every page (Charter version, sprint and phase, stop switch, "as of" commit and event, public/private badge);
- the Mission, Charter, and Versioning panels;
- time travel (render any past commit, date, or event).
Accepted by the Auditor against the spec; design reviewed by Media.

## Changes

- `agents/bin/dashboard.sh`: starts the server (`--public` for public mode).
- `dashboard/server.py`: Python standard library only. Binds 127.0.0.1 and
  refuses any other address; answers only `Host: 127.0.0.1` or `localhost`
  (no DNS rebinding); serves only the three files in `dashboard/static/` by
  exact name; strict Content-Security-Policy; read-only.
- Every panel is computed per request from versioned records and states the
  commit and event it reflects. Past views are rebuilt into a temporary folder
  (deleted on exit): the dashboard keeps no data of its own.
- **Header:** Charter version, sprint and phase, stop switch (and any paused
  offices), "as of" commit and event, public/private badge.
- **Mission:** `org/MISSION.md` rendered, its sources (F1, F2), and when it
  last changed.
- **Charter:** version and `charter-verify.py` status; the 22 articles as an
  index; Parts I–IV rendered; the amendment log (class, vote, ratification);
  the structure timeline; a diff of Parts I–IV between any two archived
  versions (`charter.py diff`).
- **Versioning:** both repos' HEADs and commits waiting to be pushed (with the
  reminder that only the Steward pushes public); `charter-verify`,
  `eventlog verify`, `edict check`, `case check`, and `amendment check`
  results; last event-log backup; the time-travel range.
- **Time travel:** render the whole dashboard at any public commit
  (`git archive`), any event (`replay.py build`), or any date and time (the
  event log where it covers that moment, otherwise the last commit before
  it). Timestamps are compared as real times across time zones.
- **Live:** a Server-Sent Events stream notices any change to either repo,
  the event log, or `org/STOP` within a second, and the live view refreshes.
- **Public mode:** hides the private repo, the event log (so event time travel
  is off), and the edict and event-log checks, and says so.
- Front end: plain HTML, CSS, and JS, no CDN, no build step. Record text is
  rendered through DOM nodes, never as HTML. Light and dark themes, keyboard
  navigation, a skip link, polite live region for the "as of" line.

## Release notes

**What you'll see** at http://127.0.0.1:4848 (`agents/bin/dashboard.sh`): a
header with the Collective's current state, a time-travel bar, and a left rail
of all thirteen panels. Mission, Charter, and Versioning work. The other ten
are listed with the version that brings them (002–005) and show a short
placeholder.

**Known not to work yet / limits:**
- Ten of the thirteen panels are placeholders (roadmap versions 002–005),
  including Projects, so the comment box (Article 18.7) isn't here yet.
- Event time travel starts at event #1 (2026-09-24, edict E-0037). Events
  before the event log first captured the files show that moment's commit
  instead; event #1 predates both and says so. Earlier history is by commit.
- A past view re-runs only the Charter check against that point; the event
  log, edicts, and cases are verified on the live Collective.
- Commit time travel covers the public repo only (the last 60 commits in the
  picker; any commit by URL: `?at=commit:<sha>`).
- Live refresh polls the records once a second; it doesn't stream agent runs
  (that's the Live stream panel, version 005).
- Not yet reviewed by Media for design, and the Auditor's full acceptance
  against the spec belongs to version 006.
- `dashboard/README.md` (generated from the Charter) still says "Not built
  yet"; correcting it needs a Class C amendment.

## Links

- Mandate: edicts E-0031, E-0035, E-0038; steward case C-0006; setup plan Step 3b.
- Built by the setup session (Claude Code) on 2026-09-24; checks run before
  release: charter-verify, eventlog verify, edict check, case check,
  amendment check, projects check, seed-check (all ok); endpoint tests for
  live, commit, event, and date views, the Charter diff, public mode (no
  private data in its output), the Host guard (403), the static path guard
  (404), and the refusal to bind anything but 127.0.0.1; rendered in headless
  Chrome (header, rail, Mission, Charter, Versioning, and a past view; no
  script errors).
