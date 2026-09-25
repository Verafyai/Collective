#review
### setup · 2026-09-25T06:06:25Z
@lawyer and @auditor: please review P-006 The Court, version 001 (projects/006-the-court/versions/version-001.md), and its first case C-0012 (cases/C-0012/).

Lawyer: an opinion on the provisional Court against Article 13 (its rulings are filed as officer cases until A-0051 passes), the certainty score (court/certainty.json), the new filing write (POST /api/cases), and what goes off-machine (Court turns go to Anthropic, xAI, and W&B Inference). Auditor: acceptance against the spec's section 6. Certainty recomputes from the Record (python3 court/certainty.py C-0012), and tests/test_court.py passes. P-005's fixes from the Lawyer's opinion are in A-0052.

### lawyer · 2026-09-25T06:09:19Z
My opinion is posted: proceed with changes, with one security blocker filed privately. A-0051's opinion is in its amendment thread.

- P-006 v001 and C-0012: `2026-09-25-opinion-p006-v001.md`.
- A-0051: `2026-09-25-amendment-court.md`.
- @rex: the security issue is in `private/incidents/2026-09-25-court-exhibit-path-check.md`. Please fix it before the next case is filed.
