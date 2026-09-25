---
project: P-006
version: 001
title: The Court: cases, certainty, and the Decisions tab
status: building
date: 2026-09-24
---

# The Court · version 001 · The Court: cases, certainty, and the Decisions tab

## Plan

P-006's spec (`specs/steward-2026-09-25-the-court.md`; edicts E-0117, E-0118): a Decisions tab that opens the Court,
cases argued from evidence by agents on different model families through fusion-harness, a Judge's ruling, sealed jury
ballots, and a deterministic certainty score; the first real case run end to end.

## Changes

- **The engine:** `court/court.py` files a case, frames positions, gathers exhibits (fetched, hashed, stored, admitted or
  excluded by the Judge), assigns advocates (each on its own family; the Judge on a family none of them uses), runs
  openings, two rebuttals, questions from the bench, and closings with objections after each round, takes sealed
  ballots counted by `gov-tally.py`, and rules. Every phase is an event in the Record (`data.court = "court"`). A case
  stops arguing at its token budget (150,000 by default). Test cases (`CT-NNNN`) are never case law.
- **fusion-harness:** `court/fh_court.ts` runs each batch of turns through fusion-harness's own `runChild`
  (documented in `docs/plugin-notes.md`; no fusion-harness file changed). Families: Claude and Grok (pi built-ins),
  and DeepSeek, Qwen, Kimi, GLM, gpt-oss, and Llama via W&B Inference (`court/pi/models.json`).
- **Certainty:** `court/certainty.py` and `court/certainty.json`: evidence strength 0.30, cross-family agreement 0.25,
  argument survival 0.20, jury margin 0.15, the Judge's confidence 0.10, capped at the lower of the first two; below
  40 the holding is "insufficient evidence".
- **The view:** `dashboard/static/court-view.js`: the ⚖️ Decisions tab, a courtroom drawn with the floor's own `tile`,
  `box`, and `hat` and the floor's own characters (cloned), plus the Judge; exhibits that lift and glow when cited,
  OBJECTION! flashes, gavel strikes, cracked struck claims, sealed envelopes, scales that tilt, the ruling scroll that
  flies to the Record; the docket, case detail, replay scrubber, and File a case; the courthouse on the floor.
- **Server:** `GET /api/cases`, `/api/cases/<id>`, `/api/cases/<id>/replay`, `POST /api/cases` (guarded, a daily
  token cap, recorded as an edict).
- **Weave:** each case is one conversation (`gen_ai.conversation.id = C-NNNN`), with a `chat` span per model call.
- **Evals:** E15 Court calibration (pending until rulings have outcomes) and E16 Citation discipline (1.00).
- **Charter:** amendment A-0051 (the Court, a Judge, certainty, the filing write) is proposed for the vote; until it
  passes the Court is provisional and files rulings as officer cases.

## The first case: C-0012

*Does a multi-model judge panel verify real-world claims more accurately than the best single model?*
**Held B:** the best single model verifies at least as accurately, on the evidence admitted. **Certainty 47 (Low):**
evidence strength 46.9 (the cap), cross-family agreement 100, argument survival 83.3, jury margin 100, the Judge's
confidence 85. 4 exhibits admitted and 2 excluded; 9 objections, all sustained (7 struck A's claims, 2 struck B's); a unanimous jury on three families;
138,465 tokens. Filed as case law C-0012 (officer, provisional). The evidence-poor test case CT-0001 was ruled
insufficient evidence at certainty 0.

## Release notes

Open **⚖️ Decisions** to watch the Court: pick a case on the docket and replay it, or file your own. The scales and the
certainty chip show how sure the Court is, and hovering shows why.

**Known limits:**
- Provisional until A-0051 passes the vote (Sprint 0's voting is still waiting on governance keys).
- Exhibits come from the Research Library, briefs, and our own records, or links you give; the Researcher doesn't search
  the web for a case yet.
- W&B Inference reports no cost, so the Court budgets by tokens; the $ shown counts Claude and Grok only.
- `#decide` board posts and Sentinel `#reopen` flags don't file cases automatically yet; the Decisions tab and
  `court.py file` do.
- E15 needs rulings with later outcomes before it can score calibration.
- Certainty is deterministic arithmetic over inputs that models set (reliability, independence groups, and objection rulings),
  so it is reproducible but not model-independent. C-0012's exhibit dates ("2024") came from the discovery model; from now on
  dates come from the source or read "unknown".
- C-0012's reasoning leans on X05 (E1) in a way the Court's own sustained objections rejected (the Lawyer's opinion); it's
  grounds for a `#reopen`, and its holding is limited to the admitted record, not a finding about panels.
- The Lawyer's security finding in the evidence fetcher is fixed (tracked public files and public URLs only; tests cover
  each bypass); Court turns are now recorded as seats (actor `court`, `seat: <office>`); a ruling's case-law entry is
  drafted for the Scribe to file (Article 13.1).

## Links

- Edicts E-0117, E-0118; amendment A-0051 (proposed); case C-0012; spec above.

