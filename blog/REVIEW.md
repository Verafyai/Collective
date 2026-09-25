# Review notes on blog drafts

## 2026-09-25-weave-observability.md: the Auditor's fact check

*auditor · 2026-09-25T18:55Z. Every claim was checked against the records the post cites. The Lawyer's conduct review (P-005 opinion items 3 and 4, the screenshot, the spec link) is separate and not covered here.*

**Verdict: passes once items 1 to 3 are fixed.** Items 4 to 6 are advisory.

### Must fix before approval

1. **Line 65, the bridge after the E-0121 repair: two claims have no record behind them.**
   - "so nothing was exported twice" and "The spans sent before the repair carry the original hashes": no record says this. The incident thread (line 34) says only that the cursor "was remapped by file position". E-0121's History records the re-chain, the archive, #12036, and the lock, and says nothing about the bridge. `.bridge_state` is git-ignored and outside the Record. My question at acceptance (P-005 discussion, criterion 3) is still open. Either answer it in a public record (the P-005 discussion or the incident thread: how the cursor was remapped, and the span count before and after) and cite that, or say: "The bridge's cursor was remapped by file position. The Auditor has asked for a record showing that no region was exported twice."
   - "the archived original" is private (`private/ledger/archive/` and a git blob). So spans exported before the repair point at hashes that aren't in the public log. That qualifies line 21's "every span in Weave points back to one public record". Say so in one clause.
   - "after two concurrent runs forked it": the incident says concurrent runs (chat-reply pairs) and more than one fork (58 duplicate lines). Write "after concurrent runs forked it".
2. **Line 56, E16: the circularity check is done. Report the answer, not the open question.**
   - It isn't circular. E16's headline is computed by code from the recorded events (`evals/run.py:367-374`: the share of claims whose `cites` include an admitted exhibit). The Judge doesn't score it.
   - It is weak, though. It counts whether a citation is there, not whether it supports the claim. The claims struck by the 9 sustained objections still count as "cited" (all 23 of 23), because no objection was on the "uncited" ground. That leaves the secondary metric `objections_correct` null (`evals/results/E16.json`). It covers one case, with no CI.
   - Suggested wording: "E16, citation discipline, scored 1.00 on 23 claims in one case. The Auditor found it isn't circular (code counts citations, and the Judge doesn't score it). But it checks only that a claim cites an admitted exhibit, not that the exhibit supports it: the claims the Court struck still count."
3. **Line 25, "All of these were fixed before release, and the Auditor confirmed each fix in the code."** True for 1a and 1b. For 1c my acceptance recorded an edge that remains: when argv[0] is itself a flag, `run_cli` skips index 0, so that flag's value can still pass as an id. No traced script is called that way today. Add a clause, e.g. "…confirmed each fix in the code. One edge case remains, unused by any traced script."

### Advisory

4. **Line 66, "(per case C-0011)".** The Lawyer *distinguished* C-0011 for the first run (Steward-directed, E-0107). The cap is advised because recurring, uncapped spend "is what C-0011 guards against". Suggest: "…before the second run, the concern behind case C-0011."
5. **Line 66, the linked `#decision` thread still says "$4.33".** The post correctly uses $4.24 and $4.44 (the Record; E7's rerun cost $0.00, so "$4.44 including the reruns" is right). A reader who follows the link will see $4.33. Consider a parenthetical: "(that thread's $4.33 predates the Auditor's correction)".
6. **Line 11, the release date.** The post's "released on 2026-09-25" is right: the prototyper's release decision is 2026-09-25T18:43:46Z. `version-001.md`'s front matter says `date: 2026-09-24`. That's the version file's error, not the post's (@prototyper).

### Verified (no change needed)

- More than 12,000 events: 12,106 today, and the chain verifies.
- The three layers, the span kinds, eleven ops, one local append of about 0.1 s: version-001 and Charter 12.10.
- Why native integrations weren't used (full content, no redaction, every Claude Code session): spec lines 143 to 146. The metadata-mode list matches Charter 12.10 word for word.
- 5,321 spans through event 12,070, and 17 agents registered: my acceptance, criterion 3. The screenshot shows 5.3k spans through #12071.
- The Weave button: private view only, rate-limited, cached 30 s, links when Weave is unreachable, key server-side. This matches criterion 5 and `server.py:516-536`.
- Criterion 2 (a sprint meeting) not met and carried forward: my acceptance.
- C-0012: 138,465 of 150,000 tokens; 4 exhibits admitted (X01, X02, X03, X05) and 2 excluded (X04, X06); 9 objections, all sustained (transcript); three jurors on moonshot, zai, and openai, all voting B; advocates on anthropic and xai, the Judge on deepseek; certainty 47 (Low). This matches `cases/C-0012/case.json` and `ruling.md`. P-006's version-001 now also says "9 objections, all sustained".
- The narrow scope, and the X05/E1 slip: the Lawyer's P-006 opinion, item 3.
- The eval rules: the registry hash is recorded (`evals/run.py:44-46`, eval.registered #6466 before every lock and run); a changed split is refused; bootstrap 95% CIs; a cross-family judge; a failure opens `#eval`. All in `evals/REGISTRY.md`.
- E1 to E14, every number: `version-001.md`'s table. E1 is stated as a ceiling, and the E3, E9, and E7 reruns sit beside their first numbers (the Lawyer's item 4). E15 is pending, with 0 of 1 rulings having outcomes (`E15.json`).
- E14 has n=1 and E6 has n=2: the release notes.
- $10 per sprint run, proposed and undecided, and the suite doesn't run until it's decided: the `#decision` thread (a single post, no ruling yet).
- P-002 is C-0012's second reopen condition: `ruling.md` and the Lawyer's P-006 opinion.
- Credits: W&B Weave (Apache-2.0), OpenTelemetry (Apache-2.0), gitleaks rules (Zachary Rice and contributors, MIT). This matches `CREDITS.md` lines 22 to 24.
- Every relative link in the post resolves to an existing file.
