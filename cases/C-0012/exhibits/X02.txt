# Brief: Dependence-Aware Label Aggregation for LLM-as-a-Judge via Ising Models

- **Paper:** https://www.amazon.science/publications/dependence-aware-label-aggregation-for-llm-as-a-judge-via-ising-models
  (PDF: https://cdn.amazon.science/ed/3b/36ee4b654cf7835388380be7558b/scipub-approval152129-44917021-dependenceaware-label-aggregation-for-llmasajudge-via-ising-models.pdf;
  both verified 2026-09-24)
- **Authors:** Krishnakumar Balasubramanian, Aleksandr Podkopaev, Shiva
  Prasad Kasiviswanathan (AWS; UC Davis)
- **Venue:** ICML 2026, PMLR 306
- **Topic:** aggregation, judge dependence
- **Briefed by:** researcher · 2026-09-24
- **Read:** main paper, pages 1–8 (appendices not read)

## Claim

Standard ways of combining several LLM judges' votes (majority vote,
weighted vote, Dawid-Skene) assume the judges are independent once you know
the true label. LLM judges aren't: they share data, architectures, prompts,
and failure modes. Modeling that dependence explicitly with an Ising model
gives more accurate aggregate labels, and the independence-based methods can
stay wrong by a fixed margin no matter how many judges are added.

## Method

- Binary labels only (Y ∈ {0,1}); K judges each vote 0/1. Multiclass is
  noted as possible via Potts models but not done.
- **Model hierarchy:** conditional independence (weighted vote) ⊂
  class-independent Ising (one shared coupling matrix W) ⊂ class-dependent
  Ising (a different W for each true label).
- **Aggregation rules:** with class-independent couplings, the Bayes rule is
  still a linear weighted vote, but with weights corrected for correlation.
  With class-dependent couplings, the Bayes log-odds are **quadratic** in the
  votes: pairs of judges agreeing carries its own evidence.
- **Theory:** a Curie-Weiss construction where every judge is individually
  better than chance, yet the independence-based predictor keeps a
  non-vanishing error as K → ∞ while the Bayes-optimal predictor's error goes
  to zero; the failure mode is a correlated "wrong-mode" agreement that
  weighted voting reads as strong evidence. A latent-factor extension shows
  the same.
- **Estimation:** EM for posterior labels (details in an appendix I did not
  read). The text calls the training samples "unsupervised"; *uncertain*
  whether any gold labels are used in fitting.
- **Experiments:** 10 judges: Claude Opus 4.5, Claude Sonnet 4.5, Claude
  Haiku 4.5, gpt-oss-120b, gpt-oss-20b, Llama 4 Maverick, Llama 4 Scout,
  Llama 3.3 70B, DeepSeek V3.2, DeepSeek-R1, all at temperature 0. Three
  binary tasks: relevance (WikiQA, ~3,000 items), toxicity (Jigsaw, 1,000
  sampled), and summarization consistency (CNN/DailyMail via the Arize
  Phoenix benchmark, 1,100 items). 20 random trials each.

## Key results

Test accuracy, all 10 judges, maximum training data (Table 1, mean ± s.e.
over 20 trials):

| Task | Class-dep. Ising | Class-indep. Ising | Weighted majority (CI) | Uniform majority |
|---|---|---|---|---|
| Relevance | **0.912** ± 0.007 | 0.899 ± 0.005 | 0.820 ± 0.004 | 0.804 ± 0.003 |
| Toxicity | **0.792** ± 0.004 | 0.780 ± 0.006 | 0.694 ± 0.004 | 0.695 ± 0.003 |
| Summarization | 0.801 ± 0.004 | **0.806** ± 0.005 | 0.737 ± 0.005 | 0.561 ± 0.005 |

- Ising models beat weighted majority by about 6–10 accuracy points (roughly
  9–14% relative, which matches Amazon's blog summary).
- Note: on summarization the table bolds class-dependent Ising, but the
  class-independent number is higher (0.806 vs 0.801). Within error, but
  worth recording.
- The Ising advantage appears only once there are enough samples and about
  5–6+ judges (Figure 3); with 3–4 judges or small samples the methods are
  close, and class-independent Ising sometimes wins.

## Limitations

- Binary tasks only; Verafy's likely benchmark (AVeriTeC) has four labels.
- The theory is about the true Bayes rule; the practical EM or
  pseudo-likelihood estimators aren't proven to inherit the guarantees (the
  authors say so).
- Class-dependent Ising has many parameters (O(K²) per class); it needs
  large samples, and the paper's own curves show it can lose at small n.
- No comparison against the best single judge is reported in the main
  table. That's the comparison Verafy Bench cares about most (see the
  companion brief `nine-judges-two-effective-votes.md`).
- No human-disagreement analysis; gold labels come from dataset annotations.

## Code and data

- No code link found in the main paper. *Uncertain* whether the appendices
  or a later arXiv version link code.
- Datasets are public: WikiQA, Jigsaw Unintended Bias (Kaggle), Arize Phoenix
  summarization benchmark. Check each license before reuse.

## Relevance to Verafy

This paper is the "dependence-aware (Ising)" aggregator named in the P-002
Verafy Bench spec (system S4), and its argument matches Verafy's founding
intuition (F1: agreement should be weighed, not counted). Read together with
Kohli's "Nine Judges" paper, it gives Verafy the right frame: correlated
judges are the central problem for AI consensus, and aggregation can
partly correct for it *if* the dependence structure is learned. The two papers disagree
in tone: Kohli finds Dawid-Skene closes at most ~11% of the gap, while this
paper finds dependence-aware models clearly beat independence-based ones.
They use different tasks, judges, and baselines, so Verafy Bench is a
natural place to test both on the same claims. For AVeriTeC the model would
need a multiclass (Potts) extension or a binarized label scheme; that's a
design decision for the Prototyper and should be stated in the Bench spec.

## Prototype potential: **medium**

Worth building as the S4 aggregator in Verafy Bench, but not on its own:
without per-judge outputs on a few thousand items, and without a
multiclass version or a binarization choice, there's nothing to fit.
Build order: collect S1/S3 outputs first, then fit class-independent Ising
(cheaper, more stable), and try class-dependent only if the sample size
supports it. Implementation effort is moderate (EM over a pairwise model).
