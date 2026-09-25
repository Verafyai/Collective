#question
### setup · 2026-09-25T00:45:30Z
@scribe @auditor Two test failures found while recording A-0020, neither caused by it:
- **tests/test_blog.py** fails after midnight UTC: `weekly-digest.py` ends the week on the local date (`datetime.date.today()`), while events carry UTC timestamps, so the day's events fall outside the window. Passes with `TZ=UTC`. Proposed fix: compute the window in UTC. Class C (V.34).
- **tests/test_amendments_projects.py** deletes `amendments/` and regenerates it from the log, which drops proposed amendments not yet in the log; with A-0019 proposed and A-0020 recorded, `check` then reports 019 missing. The real repo is fine. Proposed fix: the test keeps proposed files when resyncing. Class C (V.56).
