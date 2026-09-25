---
id: A-0051
title: The Court: cases, a Judge, and certainty
class: B
status: proposed
proposer: steward
proposed: 2026-09-24
text_sha256: b0fc1bf38a04a14bf7825d96c738708b2202b44311578983c33a8becd66e91b9
charter_version: (pending)
---

# Amendment 051 · The Court: cases, a Judge, and certainty

## Proposed text

# The Court: cases, a Judge, and certainty

**Proposed by the Steward** (edicts E-0117, E-0118), for P-006. Class B: it adds a court to Article 13 and a
dashboard write to Article 18.7. Until this passes, the Court runs **provisionally**: its rulings are filed as
officer cases (the lowest rank), and the dashboard says "Provisional court".

## Changes

**New Article 13.12, The Court.** A question the evidence can settle may be filed as a case in the case-law
sequence (`C-NNNN`), by the Steward (the dashboard's Decisions tab), a `#decide` board post, a Sentinel's
`#reopen`, or a sprint proposal that needs a ruling. The Court then:
- frames two to four mutually exclusive positions (the Lawyer, when the filer gives none);
- gathers exhibits (the Researcher and any Scholars): each fetched, hashed, stored, rated for reliability and
  independence, and admitted or excluded by the Judge;
- **assigns** advocates to positions (they don't choose), each on a different model family, through
  fusion-harness; the Judge sits on a family no advocate uses;
- hears openings, two rebuttal rounds, questions from the bench, and closings. Every factual claim cites an
  admitted exhibit. An opposing advocate may object to an uncited or misrepresented claim, and a sustained
  objection strikes it;
- takes sealed ballots from the voting offices not arguing the case, each on its own family, counted by the
  deterministic counter;
- rules: the holding (or "insufficient evidence"), reasoning citing exhibits, any dissent, the certainty
  score, and the conditions that would reopen the case.

Every phase is an event in the Record. A case costs at most its token budget (150,000 by default); when the
budget is spent, the Court goes straight to closings. Test cases (`CT-NNNN`) are never case law.

**Certainty** is computed by deterministic code from the case's events (`court/certainty.py`), never taken
from the Judge alone: a weighted mean of evidence strength (0.30), cross-family agreement (0.25), argument
survival (0.20), jury margin (0.15), and the Judge's stated confidence (0.10), capped at the lower of evidence
strength and cross-family agreement. Below 40 the holding is "insufficient evidence". The weights live in
`court/certainty.json` and change only by amendment.

**Rank.** The Court's rulings are **court** cases, ranking with officer cases (Article 13.5): the Lawyer may
distinguish or overrule them, and they bind until then. `case.py` gains the court name `court`.

**Article 18.7(k).** In private view only, the Steward files a case from the Decisions tab: rate-limited,
length-capped, refused when the day's Court budget is spent, and recorded as an edict.

## Reason

(the proposer states the reason and evidence here)

## Discussion

Board thread: org/board/2026-09-24-amendment-051.md
Lawyer's opinion: (pending)

## Vote

—

## Outcome

—

## History

- 2026-09-24: proposed by steward.
