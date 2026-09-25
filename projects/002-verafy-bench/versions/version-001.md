---
project: P-002
version: 001
title: Dataset, locked split, bench.py with S1 and S2, a 50-claim dev run
status: planned
date: 2026-09-24
---

# Verafy Bench · version 001 · Dataset, locked split, bench.py with S1 and S2, a 50-claim dev run

## Plan

Spec §6, version 001 (and §5's first steps), as a Sprint 0 item for the Prototyper, with the
Researcher choosing the dataset and the Lawyer clearing its license (§4.3, P4):
1. **Dataset chosen and cleared.** Primary candidate AVeriTeC (license CC BY-NC 4.0, per its
   Hugging Face page, checked 2026-09-24; the Lawyer's opinion asks the Steward whether Verafy's
   use counts as non-commercial). Sanity set: FEVER (CC BY-SA 3.0, Wikipedia-derived). No data is
   committed: `data/fetch.sh` plus `manifest.sha256`, data in the private repo or a local cache.
2. **Locked split** (dev/test), recorded as a SHA-256 of the claim IDs (§4.6 rule 1).
3. **`bench.py`** with S1 (each single model, one call) and S2 (the best single model with
   self-consistency, k = 5), resumable, refusing test runs without a pre-registered config hash.
4. **`metrics.py`** (accuracy, macro-F1, ECE with 10 bins, Brier, bootstrap 95% CIs).
5. **A dev run on 50 claims**, Track J (claim plus provided evidence).

Done when the Auditor reproduces the dev metrics from the committed config and hash (§6).
**Cost estimate for the dev run** (prices from the providers, 2026-09-24; about 4,000 input and
2,000 output tokens per call): S1 across claude-opus-5-5, claude-sonnet-5, claude-haiku-4-5, and
grok-4.7 is about $5.90; S2 (k = 5) on the priciest model is about $14.00; so about $20 per full
dev pass, about $60 for three passes while building. **Budget requested: a hard cap of $75**
(board #decision @rex). Nothing runs until the Steward approves it (§7).

## Changes

(filled in as it's built)

## Release notes

(filled in on release: what a human will see, what's known not to work)

## Links

(sprint item, case, commits)
