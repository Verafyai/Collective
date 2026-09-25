---
id: C-0012
title: Does a multi-model judge panel verify real-world claims more accurately than the best single model?
date: 2026-09-24
court: officer
labels: [research, governance]
headnote: The best single model verifies real-world claims at least as accurately as a multi-model judge panel, as no admitted exhibit demonstrates an empirical instance of a panel outperforming its best individual member, while multiple ex Certainty 47 (Low).
source: cases/C-0012/ruling.md (the Court, P-006, provisional: filed as an officer case under Article 13.1)
cites:
review_by: 2026-12-23
holding_sha256: 54184e5478c5a5cd82cac5f5ba0e6b3523e27d652b38886c8b3f6c39f246cb6c
---

## Question

Does a multi-model judge panel verify real-world claims more accurately than the best single model?

## Facts

The Court heard the case with 4 admitted exhibits (cases/C-0012/exhibits/exhibits.json), advocates on anthropic, xai, a Judge on deepseek, and a jury of 3 on moonshot, zai, openai. The full transcript is cases/C-0012/transcript.md; every phase is in the Record.

## Holding

B: No: the best single model verifies real-world claims at least as accurately as a multi-model judge panel.. The best single model verifies real-world claims at least as accurately as a multi-model judge panel, as no admitted exhibit demonstrates an empirical instance of a panel outperforming its best individual member, while multiple exhibits show panels either tying or losing to the best single judge.

## Reasoning

- The only head-to-head empirical comparisons between panels and their best single judge show the panel either matching or underperforming: C-0012-X01 finds the best single judge matches or beats the full nine-judge, seven-family panel on every dataset tested, and C-0012-X05 shows panel_minus_best_single of 0.0 on n=17 items. (C-0012-X01, C-0012-X05)
- C-0012-X01 demonstrates that nine judges from seven model families carry only about two effective independent votes due to correlated errors, meaning adding judges provides far less independent signal than a headcount suggests, and even sophisticated aggregation methods (Dawid-Skene, accuracy-weighting, inverse-correlation weighting) fail to make the panel beat the best single judge. (C-0012-X01)
- C-0012-X03's panel gains cannot be attributed to multi-model panels beating their best member because the single-model reference is GPT-5 mini while the panel uses GPT-5.5 Chat, and the author states the delta is not a debate-only effect; this confound prevents using it as evidence for Position A. (C-0012-X03)
- C-0012-X02 provides a theoretical argument that dependence-aware Ising aggregation can correct correlated errors that independence-based rules cannot, but it does not report an empirical instance where a real multi-model panel using Ising aggregation outperforms the best single judge; this leaves open the possibility that better aggregation could change the result but provides no admitted evidence that it has done so. (C-0012-X02)
- The researcher for A conceded under the bench's question that no admitted exhibit shows a multi-model panel beating its best individual member head-to-head, which is the core factual question at issue. (C-0012-X01, C-0012-X02, C-0012-X03, C-0012-X05)

Certainty 47 (Low), computed by court/certainty.py from the Record.

## Dissent

None.

## Scope

This question as asked, on the evidence admitted. Reopen conditions: An empirical study applying dependence-aware aggregation (such as the Ising model from C-0012-X02) to a real multi-model claim-verification panel and showing it outperforms the best single judge on accuracy.; A head-to-head comparison on a non-ceiling, adequately powered dataset where a multi-model panel using any aggregation method exceeds the accuracy of its best individual model..

## History

- 2026-09-24: filed from the Court's ruling in C-0012.
- 2026-09-24: filed.
