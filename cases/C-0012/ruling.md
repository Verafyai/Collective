# C-0012 · ruling (provisional court)

**Question:** Does a multi-model judge panel verify real-world claims more accurately than the best single model?

**Holding:** B: No: the best single model verifies real-world claims at least as accurately as a multi-model judge panel.. The best single model verifies real-world claims at least as accurately as a multi-model judge panel, as no admitted exhibit demonstrates an empirical instance of a panel outperforming its best individual member, while multiple exhibits show panels either tying or losing to the best single judge.

**Certainty:** 47 (Low). Evidence strength 46.88, cross-family agreement 100.0, argument survival 83.33, jury margin 100.0, the Judge's confidence 85.0 (weight 0.10); capped at 46.88. Recompute: `python3 court/certainty.py C-0012`.

## Reasoning

- The only head-to-head empirical comparisons between panels and their best single judge show the panel either matching or underperforming: C-0012-X01 finds the best single judge matches or beats the full nine-judge, seven-family panel on every dataset tested, and C-0012-X05 shows panel_minus_best_single of 0.0 on n=17 items. (C-0012-X01, C-0012-X05)
- C-0012-X01 demonstrates that nine judges from seven model families carry only about two effective independent votes due to correlated errors, meaning adding judges provides far less independent signal than a headcount suggests, and even sophisticated aggregation methods (Dawid-Skene, accuracy-weighting, inverse-correlation weighting) fail to make the panel beat the best single judge. (C-0012-X01)
- C-0012-X03's panel gains cannot be attributed to multi-model panels beating their best member because the single-model reference is GPT-5 mini while the panel uses GPT-5.5 Chat, and the author states the delta is not a debate-only effect; this confound prevents using it as evidence for Position A. (C-0012-X03)
- C-0012-X02 provides a theoretical argument that dependence-aware Ising aggregation can correct correlated errors that independence-based rules cannot, but it does not report an empirical instance where a real multi-model panel using Ising aggregation outperforms the best single judge; this leaves open the possibility that better aggregation could change the result but provides no admitted evidence that it has done so. (C-0012-X02)
- The researcher for A conceded under the bench's question that no admitted exhibit shows a multi-model panel beating its best individual member head-to-head, which is the core factual question at issue. (C-0012-X01, C-0012-X02, C-0012-X03, C-0012-X05)

## Dissent

None.

## Jury

- pm (moonshot): B. The admitted empirical record shows the best single judge matches or beats the multi-model panel on every real-world dataset tested (X01, X05), and no exhibit demonstrates a panel outperforming its best individual member. X02’s dependence-aware aggregator is only theoretical and untested in this setting, so the evidence supports that the best single model is at least as accurate.
- social (zai): B. On every admitted head-to-head empirical comparison (X01, X05), the best single model either matched or beat the full panel, and no admitted exhibit demonstrates a real-world multi-model panel exceeding its best individual member; X02's dependence-aware aggregator remains purely theoretical with no empirical test against a best-single-judge baseline, and side A's own researcher conceded in closing
- ideas (openai): B. No admitted exhibit shows a multi‑model panel outperforming its best individual judge; the record (X01, X05) indicates the best single model matches or exceeds panel accuracy on all head‑to‑head tests.

## Reopen conditions

- An empirical study applying dependence-aware aggregation (such as the Ising model from C-0012-X02) to a real multi-model claim-verification panel and showing it outperforms the best single judge on accuracy.
- A head-to-head comparison on a non-ceiling, adequately powered dataset where a multi-model panel using any aggregation method exceeds the accuracy of its best individual model.

## Parties

- Advocates: researcher for A (anthropic/claude-sonnet-5), prototyper for B (xai/grok-4.7)
- Judge: wandb/deepseek-ai/DeepSeek-V4-Pro (deepseek)
- Jury: pm (wandb/moonshotai/Kimi-K2.6), social (wandb/zai-org/GLM-5.2), ideas (wandb/openai/gpt-oss-120b)
- Tokens: 138465 of 150000
