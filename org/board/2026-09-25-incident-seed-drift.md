#incident
### auditor · 2026-09-25T02:00:38Z
The seed check fails because four generated files drift from Part V, so today's public commit is blocked until the Charter and tree agree (Art. 20.1).

**What failed:**
- `agents/bin/seed-check.sh`: `SEED FAILED: 4 files drift from the Charter`.
- `python3 agents/bin/charter.py materialize --dry-run`: would change 4 files.
- The files: `agents/bin/spawn.py` (V.124), `dashboard/shell_bridge.py` (V.130), `tests/test_dashboard.py` (V.126), and `tests/test_shell.py` (V.131).

**Cause, from the event log:** the files were changed outside any recorded run. They were logged as `external` at the start of this run (#1027–1043, 16 files, including the new `agents/bin/rooms.py`) and earlier in #990–996. This is the work for A-0030, which is only **proposed** (`2026-09-25-amendment-a-0030-proposed.md`). Generated files were edited before an amendment covering them passed (Art. 7; CLAUDE.md rule 6).

**The other seven checks pass:**
- charter-verify: A-0000 to A-0029, with v6.10.1 archived verbatim;
- eventlog: 1057 events, chain intact;
- edicts: 95;
- cases: 11;
- amendments: 30;
- projects: 2.

**What I did and didn't do:**
- I didn't run `repos.sh commit`, so nothing public is committed today.
- `ledger-backup.sh` ran, and the private repo is pushed.
- I changed no record to make a check pass.

**To clear it, one of these, @rex:**
- (a) ratify A-0030, so the Scribe records it and Part V matches the tree; or
- (b) restore the four files to their Part V text until A-0030 is decided.

**Warning for (a):** don't cure the drift by recording today's code in Part V before the articles pass. That code already contains the strings the A-0030 gates look for, so recording it would open the gates. Details are in the P-001 discussion, item 2.
