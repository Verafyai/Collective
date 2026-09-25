# P-002 Verafy Bench: dataset licenses and provider terms

Filed by the Researcher for C-0011 conditions (c) and (d), tsk task 2.
Checked 2026-09-24 (PDT) at the primary pages listed. This is a record of
what the pages say, not legal advice: the Lawyer reviews it, and the
non-commercial question is the Steward's (C-0011).

For the data manifest notes of version 001: `projects/002-verafy-bench/data/`
doesn't exist yet (the Prototyper creates it). The Prototyper should link or
copy this file there when it does.

## 1. AVeriTeC (primary candidate)

- **Paper:** Schlichtkrull, Guo, Vlachos, "AVeriTeC: A Dataset for
  Real-world Claim Verification with Evidence from the Web," NeurIPS 2023
  Datasets and Benchmarks. https://arxiv.org/abs/2305.13117
- **License, as stated on the official page** (https://fever.ai/dataset/averitec.html):
  "Creative Commons Attribution-NonCommercial 4.0 International". The
  official Hugging Face repo (https://huggingface.co/chenxwh/AVeriTeC)
  carries the metadata `license: cc-by-nc-4.0`. The two agree.
- **What CC BY-NC 4.0 requires, in brief:** attribution (credit the authors,
  link the license, say if changed), and no use "primarily intended for or
  directed towards commercial advantage or monetary compensation." It
  permits sharing and adapting on those terms. Whether Verafy's use is
  non-commercial is **open, for @rex**.
- **Size:** 4,568 claims from 50 fact-checking organizations (abstract).
  Inter-annotator agreement on verdicts κ = 0.619 (abstract).
- **Labels (4):** Supported, Refuted, Not Enough Evidence, Conflicting
  Evidence/Cherry-picking.
- **Evidence for Track J:** each claim carries annotated question–answer
  pairs with source URLs and a justification. These are the "evidence the
  benchmark provides."
- **Labeled splits available:** train and dev. A mirror
  (https://huggingface.co/datasets/pminervini/averitec) shows about 3.07k
  train and 500 dev rows. The shared-task test set (2,215 claims; IDs 0–999
  from the original source, 1000–2214 newly built, released 2024-07-18) is
  described by fever.ai as a *blind* test set. **Uncertain:** I couldn't
  confirm from the README whether `test.json` carries gold labels and QA
  pairs, and the repo's file listing needed a login. Plan on train + dev
  only until someone opens the file.
- **Access:** public download, not gated, at the time of checking.
- **Consequence for the split (§4.6):** our locked dev/test split should be
  drawn from the labeled pool (train + dev, about 3,568 claims) and hashed,
  not from the shared-task blind test.
- **Credit (P4):** cite the paper above in results and `CREDITS.md`.

## 2. FEVER (sanity set)

- **Page:** https://fever.ai/dataset/fever.html. 185,445 claims generated
  by altering sentences from Wikipedia. Labels: Supported, Refuted,
  NotEnoughInfo. A labeled shared-task dev set is downloadable.
- **License** (https://fever.ai/download/fever/license.html): the
  annotations incorporate Wikipedia material under the Wikipedia copyright
  policy, and, where those terms are unavailable, **CC BY-SA 3.0**.
  Share-alike: anything we redistribute that adapts the data carries the
  same license. Commercial use is allowed.
- **Caveat:** FEVER claims are synthetic, not real-world, and the evidence is
  Wikipedia, which every model has seen. It's a sanity check against
  published numbers only.

## 3. Model provider terms on publishing benchmark results (condition (d))

| Provider | Page checked | What it says about publishing results | Status |
|---|---|---|---|
| Anthropic | https://www.anthropic.com/legal/commercial-terms (effective date shown: 2025-06-17) | No clause on benchmarking or publishing evaluation results found. §D.4 bars using the Services "to build a competing product or service, including to train competing AI models," reverse engineering, or reselling. §B: the customer owns its Outputs. | Verified at the primary page. Whether this is the version on Rex's account should be confirmed (enterprise or Bedrock terms may differ). |
| xAI (Grok) | https://x.ai/legal/terms-of-service-enterprise | The page returned HTTP 403 to my fetcher, as did the archived 2025-06-27 version. Search results didn't show a benchmarking clause, but **search results aren't a source** (LEARNINGS 2026-09-24). | **Not verified.** @rex or @lawyer: please open this page in a browser and look for "benchmark", "evaluation", "publish", and "competing". |
| Others | — | v001's cost estimate names only Anthropic models and grok-4.7. Any provider added later gets a row here before its first test run. | — |

**My reading (for the Lawyer to confirm or correct):** publishing aggregate
accuracy for Claude models appears unrestricted by the Anthropic terms I
read. Using model outputs to *train* a competing model would not be; the
Bench trains nothing. xAI is unknown until someone reads its terms.

## 4. What this means for version 001

- **If @rex rules our use non-commercial:** AVeriTeC train + dev as the
  pool; a locked 50-claim dev slice drawn from it; no data committed (§4.3).
- **If not:** AVeriTeC can't be used without written permission from the
  authors (P4, POLICIES §1a). The fallback is FEVER (CC BY-SA 3.0) for
  v001's plumbing, with the caveats above, while permission is requested
  through the Steward.
- Either way: public results carry claim IDs, not claim text (condition
  (d)).
