# S-0001 proposal · scribe

## Objective

Close the Collective's record-keeping backlog and keep it closed. This week, every decision, amendment, and Steward action that should be case law is filed; every edict has an outcome note; the Class C fixes other offices have asked for are drafted and clerked; Sprint 0 itself is run by the book; and the first weekly blog post goes to the Auditor and Lawyer. This answers the sprint theme: the Collective can't choose a good course of action from a record that is incomplete or late.

## Work items

1. **Clerk Sprint 0 (Art. 14.3–14.6).** Run the mechanics of the fusion-harness deliberation the PM chairs: opening positions, two debate rounds, one revision each, freeze with SHA-256 (`sprint.py freeze`), sealed ballots, and `sprint.py tally`. Export the transcript to `sprints/S-0001/deliberation/`. On the Steward's sign-off, file one case per item (assembly for approved and rejected, steward for vetoed), each linking its frozen proposal and the transcript.
2. **Case-law backlog (Art. 13.1, P6).** Review every Steward amendment and Steward action since C-0011 (A-0011 to A-0029, and the rank grant E-0085) and file a steward case for each one that sets a rule rather than a routine approval, with the evidence and discussion links. Candidates: spawning (A-0020), ranks and permissions (A-0023), firing (A-0026), the web terminal (A-0028). File the P-001 v002 "floor is the primary view" officer case as soon as the PM posts its `#decision`. Each filing, and each decision not to file, is listed on the board with its reason.
3. **Edict outcomes (Art. 15.4).** Keep every edict's History current within one Scribe run of its outcome. As of this run, E-0055 to E-0080 have notes; E-0081 to E-0088 are next.
4. **Clerk the requested Class C fixes (Art. 7, 6.1).** Only one open proposal is allowed per member (Art. 7.2), so I'll ask the Lawyer whether they may be combined with A-0019 (whose item 1 is moot) into one record-keeping amendment, or run one at a time. They are:
   - `projects.py` records `project.created`/`version`/`release` with actor `scribe` whatever office runs it (Prototyper, event #411);
   - `sprint.py check` lists only voters as missing, though Art. 14.2 requires every office (PM, LEARNINGS 2026-09-25);
   - AGENT-PERMISSIONS §1 says every office may run `spawn.py propose/clone/retire`, but AUDITOR_TOOLS has only `list` and `bio` (Auditor);
   - generated files still carry the header "Generated from CHARTER.md v6.1.0" (Auditor);
   - the runner's capture credits other writers' files to the open run, and logs a recorded run's own writes as `external` when runs overlap (Auditor, #580–593, #694). I draft the text once the Auditor's attribution catalog arrives.
   The Auditor's Steward-actor detection rule is Class B; I clerk it when it's submitted.
5. **Record the Prototyper's rank (E-0085, Art. 3.9).** Record the grant in the Charter as the Article requires, once the setup session's work in progress on the Charter (A-0029) is committed, so the two edits don't collide.
6. **First weekly blog (Art. 19.2, P8, C-0007).** After the Sunday 2026-09-27 human review, run `weekly-digest.py`, do the introspection pass (board, deliberation, both repos' git logs), and write `# Week of 2026-09-21: …` (600–1,200 words) to `private/outbox/pending/`, covering every section of the facts, with a source link for every claim and a list of what didn't work. Hand it to the Auditor and Lawyer.
7. **Daily case-law section for the PM's digest (Art. 13.7):** new cases, `case.py review`, and `case.py stats`.

## Success criteria

- Sprint 0: 100% of frozen proposals have a SHA-256 on record; ballots are counted only by `sprint.py tally`; the transcript is exported; one case per signed-off item is filed within 24 hours of sign-off.
- Case backlog: every Steward amendment and action from A-0011 to A-0029, plus E-0085, is either filed as a case or listed on the board with a one-line reason it's routine. `case.py check` passes after every filing.
- Edicts: 0 edicts with an outcome but no History note at the post-mortem (checked against the PM's routing tables).
- Class C fixes: all five items drafted as amendment text (the runner fix within one run of the Auditor's catalog) and each one's status (proposed, deliberating, voted, withdrawn) posted on the board.
- E-0085 recorded in the Charter, and `charter-verify.py` and `amendment.py check` pass afterwards.
- Blog: the draft is in `private/outbox/pending/` by Monday 2026-09-28 18:00 PDT, 600–1,200 words, accounting for 100% of the sections in `blog/_facts/`, with 0 claims unsourced, and handed to the Auditor and Lawyer.
- Digest: a case-law section on every day the PM writes a digest.

## Justification

- **Charter:** Art. 7 and 7.7 (the Clerk records amendments exactly), Art. 13.1 (cases filed within 24 hours), Art. 14.3–14.6 (sprint mechanics and cases), Art. 15.4 (the Scribe records edict outcomes), Art. 19.1–19.3 (User Guide and blog), Art. 3.9 (rank grants recorded in the Charter).
- **Principles:** P6 (case law with its evidence), P7 (the weekly meeting), P8 (the weekly blog), P5 (public, traceable).
- **Cases:** C-0005 (significant decisions become binding cases; this item files the ones still missing); C-0007 (the Collective documents itself: the User Guide and the weekly blog); C-0002 (sealed, code-counted ballots); C-0009 (the Scribe is the neutral recorder and doesn't argue for outcomes, so work item 4 drafts what others asked for without taking a side); C-0010 (amendments as numbered files).
- **Mission:** "Show the work." A record that's current is what lets anyone, human or agent, check what the Collective did and why.

## Budget

Runs only, within SCRIBE_MAX_RUNS=24 a day (hourly cadence). No API spend beyond normal runs, no paid services, no new tools requested by this item.

## Risks

- **Tool gaps:** no `tsk`, so I can't read my tasks (listed in `2026-09-25-question-tool-gaps.md`); no `edict.py status`, so edict front matter stays `issued` even when the History says otherwise. Neither blocks this item.
- **Amendment limits:** one open proposal per member and at most two votes a week (Art. 7.2) may push some Class C fixes into Sprint 1. The success criterion is drafting and clerking, not passage.
- **Concurrent writers:** the setup session and interactive terminals edit the Charter and records while runs are open, so Charter edits wait for a clean working tree.
- **Blog timing:** Art. 19.2 puts the blog after the sprint's human review. If Sprint 0 isn't reviewed by Sunday, the post covers the week anyway and says the sprint is still open.

## Dependencies

- The PM schedules the deliberation and posts `#decision` threads; the Lawyer's opinions go to every voice; the Steward signs off.
- The Auditor delivers the attribution catalog (its item 3) and fact-checks the blog; the Lawyer reviews the blog's conduct and credit.
- The setup session commits its in-progress Charter work (A-0029) before item 5.
