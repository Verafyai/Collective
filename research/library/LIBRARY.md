# Research Library

Two shelves: **foundations of AI debate** (01–08, research evidence) and
**founding documents** (F1–F2, Verafy's own vision).

## Foundations of AI debate

The Collective's reference shelf for prototyping and operating decisions. The PDFs
live in `private/library/pdfs/` (private repo only; see Licensing).
Rebuild or verify them anytime with `research/library/fetch.sh`, which checks
every file against the SHA-256 below.

## How the Collective uses the library

- **Ideas:** every prototype proposal cites at least one library paper for
  its design, and states which finding it relies on. If the prototype uses
  debate, the proposal also says how it will compare against a cheap baseline
  (paper 08) and whether the judge lacks information the debaters have
  (paper 07).
- **Prototyper:** the README of every debate-based prototype names the
  protocol it implements (e.g. "Du et al. rounds, Liang assigned stances")
  with library IDs.
- **Researcher:** keeps this file current. New papers go to
  `research/papers.md` first. Adding a paper to or removing one from the
  library is a Class C amendment.
- **Governance:** amendment proposals about judging or debate cite the
  relevant library papers.

## Shelf

| ID | Paper | Authors | Year | arXiv (pinned) | Key finding | Use it for |
|---|---|---|---|---|---|---|
| 01 | [AI safety via debate](https://arxiv.org/abs/1805.00899) | Irving, Christiano, Amodei | 2018 | [1805.00899v2](https://arxiv.org/pdf/1805.00899v2) | The origin: two AIs argue, a judge decides; lying is harder to defend than exposing a lie. | Why debate at all: the core premise behind Verafy's judges. |
| 02 | [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325) | Du, Li, Torralba, Tenenbaum, Mordatch | 2023 | [2305.14325v1](https://arxiv.org/pdf/2305.14325v1) | Several instances propose, critique each other over rounds, and converge on more accurate answers. | Baseline protocol for /fh-debate and the Discussion feature. |
| 03 | [Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate](https://arxiv.org/abs/2305.19118) | Liang et al. | 2023 | [2305.19118v4](https://arxiv.org/pdf/2305.19118v4) | Single models lock onto first ideas; assigned opposing sides plus a judge break the lock. | Assigned stances (Devil's Advocate, Pro/Con takes). |
| 04 | [ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate](https://arxiv.org/abs/2308.07201) | Chan et al. | 2023 | [2308.07201v1](https://arxiv.org/pdf/2308.07201v1) | A panel of persona referees that discuss before grading agrees with humans more than single judges. | Persona judge panels for evaluation. |
| 05 | [Debate Helps Supervise Unreliable Experts](https://arxiv.org/abs/2311.08702) | Michael, Mahdi, Rein, Petty, Dirani, Padmakumar, Bowman | 2023 | [2311.08702v1](https://arxiv.org/pdf/2311.08702v1) | Human study: debate 84% judge accuracy vs 74% for a single advocate (consultancy); debates shorter. | Prefer two-sided debate over one persuasive advocate. |
| 06 | [Debating with More Persuasive LLMs Leads to More Truthful Answers](https://arxiv.org/abs/2402.06782) | Khan et al. | 2024 | [2402.06782v4](https://arxiv.org/pdf/2402.06782v4) | More persuasive debaters raise judge accuracy; skill helps the honest side more. | Put the strongest models in debater seats; judges can be weaker. |
| 07 | [On scalable oversight with weak LLMs judging strong LLMs](https://arxiv.org/abs/2407.04622) | Kenton et al. (Google DeepMind) | 2024 | [2407.04622v2](https://arxiv.org/pdf/2407.04622v2) | Debate beats consultancy everywhere, but beats direct answering mainly when the judge lacks information the debaters have. | Use debate where evidence is asymmetric; skip it where it adds nothing. |
| 08 | [Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs](https://arxiv.org/abs/2311.17371) | Smit, Grinsztajn, Duckworth, Barrett, Pretorius | 2024 | [2311.17371v3](https://arxiv.org/pdf/2311.17371v3) | Default debate doesn't reliably beat self-consistency/ensembling; tuned agreement levels can beat all non-debate methods. | Always compare against a cheap baseline; tune agreement before claiming gains. |

## Founding documents

Verafy's own founding vision, from the Steward (edict E-0030). They're the
primary source for `org/MISSION.md`. They're kept privately and have no
public link.

| ID | Document | Date | What it holds | Use it for |
|---|---|---|---|---|
| F1 | ETHDenver talk: "The Internet of Truth" (Rex St. John, with IQ6900) | Feb 2025 | The problem ("who is telling the truth?"), Truth Mining, AI consensus as the successor to BFT and smart contracts, verified document bundles, the atomic fact store for agents, merit-weighted voting with salted tracer questions, heterogeneous threshold consensus, (g) chains | Mission alignment, and the origin of ideas the Collective builds on |
| F2 | Verafy update deck | 14 Mar 2025 | Verafy as "the verification layer for an internet of autonomous agents (and humans)"; history and traction; the A0 verified-intelligence layer; TruthMiner v1; the virtuous content cycle; competition map | Mission alignment, and what was promised publicly before |

**How the Collective uses them:**
- Sprint proposals and amendment proposals may cite F1 and F2 for **mission
  alignment** ("per F1, merit-weighted voting").
- They're the founder's vision, **not research evidence**, so citing them
  doesn't meet the Research Library requirement in C-0003. A design choice
  still needs a research paper behind it.
- **Historical content isn't policy.** Both decks describe tokens ($truth,
  $verafy), tokenomics, staking, and fundraising. Those reflect Verafy's 2025
  plans. The Collective never promotes tokens, prices, or funding claims
  (Constitution Article 4.4), and a deck mentioning them doesn't change that.
- F2 names team members and partners. Don't name people from it publicly
  without the Steward's approval.
- Never publish these PDFs or quote them at length. They stay in the
  private repo.

## Manifest (for fetch.sh)

```
01-irving-2018-ai-safety-via-debate.pdf  https://arxiv.org/pdf/1805.00899v2  58b8999dda10e3c6bc3552287dd8d7b696a042b827765ceabf27f7cb5895da8f
02-du-2023-multiagent-debate.pdf  https://arxiv.org/pdf/2305.14325v1  b302ff15202dc3cda03f40ea1ac92b29e1519978540b345af92991f6d3e619b4
03-liang-2023-divergent-thinking-mad.pdf  https://arxiv.org/pdf/2305.19118v4  7696fb358c8a8ba982a314b95269485b49b5ab830eec3e2f217d89f71e541c17
04-chan-2023-chateval.pdf  https://arxiv.org/pdf/2308.07201v1  33cf1da3370e441b6a2f6ce29c420be79760e45b6efdbad2261bc6fbc7396698
05-michael-2023-debate-supervise-unreliable-experts.pdf  https://arxiv.org/pdf/2311.08702v1  007265507e127a7754fb16f7b8ca6b841e76fc710053bdebc318a8631112d478
06-khan-2024-persuasive-debaters-truthful.pdf  https://arxiv.org/pdf/2402.06782v4  7c821195db82719f5fbecdfaf6762d626bf5b47b20bc862b6a7dbfe577b0ecc6
07-kenton-2024-weak-judges-strong-llms.pdf  https://arxiv.org/pdf/2407.04622v2  ff0a323d6109044ee6b6cc4b77634e27a1273999e757a0921ccd4da5941aaff3
08-smit-2024-should-we-be-going-mad.pdf  https://arxiv.org/pdf/2311.17371v3  cf31ec80f408df56d7e6010fb28fc04094638830d6d94ed9dd8f0965577c57f2
F1-ethdenver-2025-verafy-talk.pdf  private  1c875914dd5d1ae1e9a943be417b76a415943e5128f6a70259fe24a3234d438c
F2-verafy-2025-03-14-update-deck.pdf  private  23dc57057e3c75fe5d0eed77ee69584cd872425016aa25ec8d0cc734b038acf3
```

## Licensing

These papers are distributed by arXiv under each author's chosen license.
Many allow arXiv to distribute them but don't allow redistribution. The
library PDFs are for internal use in the private repo only. Never copy them
into the public governance repo, posts, or media. Link to arXiv instead, and
quote only briefly with credit (POLICIES §1).

## Reading order for new members

F1 → F2, then 08 → 07 → 02 → 03 → 04 → 05 → 06 → 01. Start with where Verafy came from, then
the skeptic and the largest benchmark, then the protocols, then the evidence,
then the theory.
