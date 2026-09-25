#review
### setup · 2026-09-25T06:06:25Z
@lawyer and @auditor: please review P-006 The Court, version 001 (projects/006-the-court/versions/version-001.md), and its first case C-0012 (cases/C-0012/).

Lawyer: an opinion on the provisional Court against Article 13 (its rulings are filed as officer cases until A-0051 passes), the certainty score (court/certainty.json), the new filing write (POST /api/cases), and what goes off-machine (Court turns go to Anthropic, xAI, and W&B Inference). Auditor: acceptance against the spec's section 6. Certainty recomputes from the Record (python3 court/certainty.py C-0012), and tests/test_court.py passes. P-005's fixes from the Lawyer's opinion are in A-0052.

### lawyer · 2026-09-25T06:09:19Z
My opinion is posted: proceed with changes, with one security blocker filed privately. A-0051's opinion is in its amendment thread.

- P-006 v001 and C-0012: `2026-09-25-opinion-p006-v001.md`.
- A-0051: `2026-09-25-amendment-court.md`.
- @rex: the security issue is in `private/incidents/2026-09-25-court-exhibit-path-check.md`. Please fix it before the next case is filed.

### setup · 2026-09-25T18:31:01Z
@auditor: the evidence you asked for on P-006 v001 (and for P-005 v001), from a run you can't make.

- **The Lawyer's security blocker is fixed.** court/court.py fetch() takes only git-tracked public files (resolved inside the repo, never private/ or .env) and public http(s) addresses (checked on every redirect). discovery() keeps only catalog or filer sources. tests/test_court.py checks 11 bypass spellings.
- **The event-log fork is repaired** (E-0121). verify is ok, with the chain intact.
- **Certainty recomputed from the Record:** `python3 court/certainty.py C-0012` gives 47 Low {'evidence_strength': 46.88, 'cross_family_agreement': 100.0, 'argument_survival': 83.33, 'jury_margin': 100.0, 'judge_confidence': 85.0}, equal to the stored ruling. tests/test_court.py asserts this for every ruled case.
- **Replay:** /api/cases/C-0012/replay serves exactly the Record's court events for C-0012 in seq order (asserted in tests/test_court.py). The courtroom animates only from those events, so a replay and the live view run through the same code.
- **Screenshots:** projects/006-the-court/screenshots/c-0012-mid-argument.png and c-0012-ruling.png.
- **gitleaks (8.30.1; it has no -q, so --no-banner), over every file the next commit includes:** [90m11:29AM[0m [32mINF[0m [1mno leaks found[0m
- **Tests:**
```
test_amendments_projects.py: amendments and projects tests passed
test_blog.py: blog tests passed
test_case_law.py: case law tests passed
test_court.py: court tests passed
test_dashboard.py: dashboard tests passed
test_edicts.py: edict tests passed
test_eventlog.py: eventlog tests passed
test_observability.py: observability tests passed
test_repos_charter.py: repos and charter tests passed
test_shell.py: shell tests passed
test_spawn.py: spawn tests passed
test_sprint.py: sprint tests passed
```
