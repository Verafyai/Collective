# Brief: Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels

- **Paper:** https://arxiv.org/abs/2605.29800 (v1, 28 May 2026; link verified 2026-09-24)
- **Author:** Guneet Kohli
- **Topic:** panels, aggregation, judge dependence
- **Briefed by:** researcher · 2026-09-24
- **Read:** full HTML version (arxiv.org/html/2605.29800); tables 3 and 5 checked twice

## Claim

A panel of nine frontier LLM judges from seven model families carries about
as much independent information as **two** judges, because the judges tend
to get the same items wrong. Majority vote therefore falls far short of
what independent voting ("Condorcet") would predict, and the best single
judge matches or beats the full panel on every dataset tested. Smarter
aggregation doesn't fix it.

## Method

- **Judges (9, 7 families):** GPT-4o, GPT-4o-mini, Claude Sonnet 4.5, Gemini
  2.5 Pro, Llama 4 Maverick, Llama 4 Scout, Qwen3-32B, Mistral Large 3,
  DeepSeek-V3. Temperature 0 by default.
- **Data:** 1,000 items each from the ChaosNLI versions of MNLI, SNLI (both
  3-class) and AlphaNLI (2-class). Gold label is the majority of ~100 human
  annotators per item. RewardBench (binary preference, 1,000 items) is a
  fourth check.
- **Effective number of judges:** the Kish design-effect formula,
  n_eff = k / (1 + (k − 1)·φ̄), where φ̄ is the mean pairwise phi
  correlation between judges' binary *error* vectors. An eigenvalue version
  (k / λ_max) is the robustness check.
- **Independence baseline:** per-judge class-conditional confusion matrices,
  stratified by how much humans disagreed on the item; 10,000 Monte Carlo
  draws per item of independent votes give the accuracy majority vote
  *would* reach if errors were independent. The "Condorcet gap" is predicted
  minus actual.
- **Aggregators:** majority vote, Dawid-Skene EM, accuracy-weighted vote
  (5-fold CV, uses gold labels), and a Markowitz-style inverse-correlation
  weighting.
- **Robustness:** reframed prompt, reversed label order, chain-of-thought,
  temperature 0.5; leave-one-judge-out; one-judge-per-family panels; panel
  size curves.

## Key results

| | MNLI | SNLI | AlphaNLI |
|---|---|---|---|
| n_eff (of 9) | 2.18 [2.07–2.31] | 2.35 [2.21–2.51] | 2.48 [2.32–2.69] |
| Panel accuracy (majority) | 72.0% | 77.7% | 88.7% |
| Best single judge | 71.8% | 84.2% | 91.2% |
| Condorcet gap | 22.0 pp | 14.0 pp | 7.6 pp |

- Mean error correlation φ̄ = 0.391 on MNLI; the curve flattens toward
  1/φ̄ ≈ 2.56 effective judges however many are added. Five judges already
  give n_eff ≈ 1.96 (about 90% of what's reachable).
- **Unanimity isn't safety:** on the 319 MNLI items where all nine agreed,
  accuracy was 90.9%, against ~99.99% expected under independence.
- **Aggregation barely helps:** Dawid-Skene scored 70.7 / 77.6 / 89.5 on
  MNLI / SNLI / AlphaNLI; accuracy-weighted voting 72.2 / 77.7 / 88.7. The
  best closure of the gap by a stable method was ~11% (Dawid-Skene on
  AlphaNLI).
- **Families don't buy independence:** the most correlated pairs were
  *cross*-family (Claude × Gemini φ = 0.603, GPT-4o × Claude 0.588); keeping
  one judge per family lowered n_eff to 1.93. Chain-of-thought *raised*
  correlation (φ̄ 0.456, n_eff 1.94).
- For comparison, the human annotators' n_eff was 5.79 / 4.78 / 4.03.

## Limitations

- Classification only (NLI plus pairwise preference). Open-ended judging,
  fact-checking with evidence, and code review are untested.
- Gold is a 100-annotator majority, which may be a plurality rather than
  truth on high-disagreement items (the author runs a distributional check).
- A snapshot of current models; prompts explored are narrow (no few-shot,
  no persona, no debate, no retrieval).
- Confidence intervals cover item sampling, not the choice of judges.
- Single author; no venue stated. *Uncertain:* not yet peer reviewed as far
  as the arXiv page shows.

## Code and data

- No code repository is linked in the paper.
- Data is public: ChaosNLI (GitHub, and `metaeval/chaos-mnli-ambiguity` on
  Hugging Face) and RewardBench (`allenai/reward-bench` on Hugging Face).

## Relevance to Verafy

This is the most direct test yet of Verafy's core thesis, and on these tasks
the thesis fails: a diverse-by-family panel did not beat its best member.
It doesn't close the question. Verafy's claim is about judging *real claims
with evidence*, and about deliberation and evidence-weighting, none of which
this paper tests. But it changes how P-002 Verafy Bench must be built.
Every panel result should report n_eff and the error-correlation matrix next
to accuracy; "different model family" can't be assumed to mean
"independent"; unanimous verdicts need their own error rate rather than
being treated as settled (a direct caution for the Mission's "settled"
threshold); and the S1 best-single-model baseline is a serious bar, not a
formality. It also sharpens the useful question: does evidence or debate
*lower* φ̄? That would be a genuine, publishable finding whichever way it
comes out (Research Library 08 and 07 point the same way: compare to cheap
baselines, and expect debate to help mainly under information asymmetry).

## Prototype potential: **high**

Cheap and immediately useful: an `n_eff` and error-correlation diagnostic is
a few dozen lines on top of Verafy Bench's per-judge outputs, needs no new
model calls, and turns every Bench run into a test of this paper's claim on
fact-checking data (AVeriTeC). A small standalone demo ("your panel of 5 is
really 2 votes") is also a clear, honest video. Proposed to Ideas on the
board.
