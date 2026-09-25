# Verafy Org: Learnings

The single file of things we learned along the way. **Append only.** Never
rewrite or delete another agent's entry. Chief consolidates duplicates monthly
into a "Consolidated" section at the top, keeping the originals.

Entry format:

```
## YYYY-MM-DD · <agent> · <short title>
What happened:
What we learned:
What we'll do differently:
```

---

## 2026-09-23 · rex · Starting principles
What happened: Designed Verafy across several iterations (truth chain,
decision engine, browser extension, simulation console, ProofSwarm).
What we learned: Work that's cheap to verify is what makes strangers' work
trustworthy. Formalized statements need human vetting. Label anything
simulated.
What we'll do differently: Show the work in public, and never post anything
we couldn't defend with sources.

## 2026-09-24 · steward (via Claude) · Archives must be untouchable
What happened: A bulk rename (verafy-org.toml → collective.toml) was applied to every file mentioning it, including the archived Charter versions. `charter-verify.py` failed immediately on the altered archives.
What we learned: Bulk edits must exclude archives and frozen records (charter/history, cases, edicts, the event log). The hash chain catches this, which is why it exists.
What we'll do differently: Scope every bulk edit to generated files only, and run `charter-verify.py` after any repo-wide change.

## 2026-09-24 · steward (via Claude) · Secret detectors need word boundaries
What happened: The file name "task-T-0002-user-guide-and-blog" contains "sk-T-0002-…", which the key detector took for an API key. The event log stored redacted copies of a case and the Charter, which would have made replay inexact, and the public-commit scan would have blocked the commit.
What we learned: Detection patterns need word boundaries, and a false positive in redaction is an integrity bug, not just noise. The weekly-blog test caught it because it checks exact incident counts.
What we'll do differently: Keep key-pattern tests with both real-shaped keys and innocent look-alikes, and treat any unexpected redaction incident as something to investigate before continuing.

## 2026-09-25 · scribe (via Claude) · The version header must move with the log entry
What happened: When recording A-0013, the amendment log's Part VI entry was correctly stamped v6.1.1, but the Charter's own header field ("Charter version: X") in charter_head.md wasn't bumped first. charter-verify.py reads the header to pick which archived file to check against, so it compared the new content to the OLD v6.1.0 archive and failed.
What we learned: The two version markers (the header line and the latest Part VI entry) must always be edited together, in the same step, or verification catches a real inconsistency rather than a cosmetic one.
What we'll do differently: Treat "bump the header" as the first sub-step of every amendment, before assembling Part V, and let charter-verify.py run immediately after every rebuild, not just at the end of a batch.

## 2026-09-25 · scribe (via Claude) · An edict recorded isn't an edict done
What happened: E-0035 (amendments folder, projects, launch script) was recorded, then the next request arrived and was implemented first; E-0035 sat at status "issued" until the Steward noticed.
What we learned: Recording an edict is only step one. The Project Manager's daily check of edicts still at "issued" exists for exactly this, and edict_latency_days (≤ 7) is the KPI that would have caught it.
What we'll do differently: Before starting any new edict, check `edict.py replay` for earlier ones still "issued" and finish or explicitly schedule them first.

## 2026-09-25 · scribe (via Claude) · Rebuilds must restore permissions too
What happened: A from-scratch rebuild restored launch.sh byte-for-byte but not its executable bit, because the rebuild only restored permissions for scripts under bin/ and setup/.
What we learned: "Identical content" isn't "identical files"; the seed check compares content, so the fresh-rebuild test caught this, not the daily check.
What we'll do differently: charter.py marks every .sh file executable, and the fresh-rebuild test checks the launch script is executable.

## 2026-09-25 · scribe (via Claude) · A plugin isn't a program on your PATH
What happened: On the Steward's first real launch, launch.sh installed herdr-plus as a herdr plugin and then called `herdr-plus` as a command, which failed: installing the plugin doesn't put its binary on PATH. The script's "already installed?" check also missed the installed plugin and prompted for a reinstall.
What we learned: The first run on the real machine is the only true test of anything that touches installed software; stand-ins encode our assumptions, including wrong ones.
What we'll do differently: launch.sh now detects the plugin by its config folder, finds the binary inside herdr's plugin folders (or points to the documented Homebrew install), and states the next two commands plainly. When the Steward reports a real-machine error, fix it at the root and add a test for that exact case.

## 2026-09-24 · setup (Claude Code) · A secret scanner must see exactly what will be published
What happened: With real keys in the git-ignored agents/.env, repos.sh's gitleaks pass (run over the whole folder with --no-git) refused every public commit. Fixing it surfaced more: the Charter's own gitleaks flag (-q) was invalid and had been removed on disk without an amendment; a single-file grep hit recorded the secret itself as its "location"; `date -Is` produced blank timestamps on macOS, including approval stamps; and the tests copied agents/.env into temp folders and overwrote the Steward's global git email. The setup agent ran one such test before noticing; the email was restored and the copy deleted.
What we learned: A gate that scans more than it publishes blocks for the wrong reasons, and a gate that prints what it finds leaks it. Scripts only ever tested in a sandbox without real secrets, or on Linux, hide these faults until the first real run on the Steward's Mac. Read a test before running it against the live tree.
What we'll do differently: Scan exactly the files being committed and report locations only (A-0016). Tests never copy secrets, always clean up, and never write outside their sandbox. Before running any script for the first time on the live tree, read what it touches.

## 2026-09-24 · researcher · Verify metadata at the primary page, and read PDFs directly
What happened: A web-search summary gave the wrong authors for arXiv 2606.01034; the arXiv page itself named different ones. The page-summarizing fetch returned "not stated" for every result in the Ising paper's PDF, although the numbers were all there when the saved PDF was read page by page.
What we learned: Search snippets and fetch summaries are leads, not sources. Titles, authors, and every number in a brief must come from the paper's own page or PDF.
What we'll do differently: Take metadata from the arXiv abstract page, read PDFs with the file reader when the summarizer comes back thin, and check key tables twice before quoting numbers.

## 2026-09-24 · ideas · Fold a demo into the instrument it measures
What happened: The best new brief (Kohli, n_eff) suggested both a standalone demo and a metric the P-002 Verafy Bench spec already lists (§4.5 "Agreement"). A separate prototype would have built the same code twice, and it would have used one of the three open-proposal slots on a duplicate.
What we learned: When a paper's insight is also a measurement, the demo and the metric should be one module. The demo runs on simulated data now and on real Bench output later. Checking the code against a paper's published arithmetic (9 / (1 + 8 × 0.391) = 2.18) is a cheap, honest test, but it isn't a replication.
What we'll do differently: Before proposing, check the active project specs for overlap. Propose overlapping ideas as work items of that project, and post them in the existing thread instead of opening a new proposal.

## 2026-09-24 · lawyer · "Re-run" means recompute, unless someone pays for it
What happened: E-0053's `reproducibility_rate` says the Auditor "re-runs" published results and gets "the same answer". Model outputs can't be reproduced (Art. 12.4, C-0004), so a literal re-run of a benchmark would be a new, paid experiment that can't match exactly.
What we learned: For LLM results, reproducibility has two levels. Recomputing metrics from committed predictions, config, and split hash is deterministic and free. Re-calling the models is a new measurement that needs a tolerance band and a budget.
What we'll do differently: Any KPI or "done when" test that says "reproduce" or "re-run" must say which level it means. The default is recomputation from committed artifacts.

## 2026-09-24 · scribe · Check whether a record is generated before editing it
What happened: The Auditor asked the Scribe to bump the User Guide's "Matches Charter" line. The Scribe owns the guide, but `docs/USER-GUIDE.md` is generated from Part V (V.112), so a direct edit would have shown up as drift in the next materialize check. Separately, edicts the PM wanted "marked adopted" already had outcome notes; only their front-matter status was stale, and no tool can change it.
What we learned: Owning a record isn't the same as being able to edit its file. Before touching a file, search CHARTER.md for `## V.` plus its path. If it's there, the change is an amendment (Class C for wording). "Stale" can mean a field no tool can reach, not missing work.
What we'll do differently: Grep Part V before editing any record, and when a request can't be done with the office's tools, say which tool is missing rather than working around it.

## 2026-09-24 · prototyper · Appearing in Part V doesn't make a file frozen; read the other offices' findings before saying "nothing to do"
What happened: I posted that P-001 needed no maintenance, then found the Auditor's review in P-001's discussion asking me, the owner, to fix an untrue Plan line. The file's text also appears in Part V (V.110), which made it look generated and off-limits. But `charter.py` lists `projects/` under LIVE: it seeds the file once and never overwrites or drift-checks it. Separately, `projects.py new` credited P-002's creation to the scribe in the event log (seq 411), because `event()` defaults the actor.
What we learned: Part V holds two kinds of files: generated ones, which only an amendment can change, and seed records, which are live. The LIVE tuple in `charter.py` is the test, and `materialize --dry-run` confirms there's no drift. A "nothing to do" status needs every project discussion read first.
What we'll do differently: Before any status post, read each owned project's discussion to the end. Before editing a file found in Part V, check it against charter.py's LIVE list. Check the event log's actor on the first run of any tool.

## 2026-09-24 · media · Compute design checks, don't eyeball them, and copy numbers from the output
What happened: With no demo ready, I reviewed the dashboard palette's contrast. I wrote a small script that reads the CSS variables and prints WCAG ratios, so the result can be reproduced. When I summarized its output in the P-001 discussion, I still misreported one line (I called --ink the lowest dark-theme pair; it's --muted, at 5.87). The discussion is append-only, so I posted a correction.
What we learned: A reproducible check helps only if the summary matches what it printed. Hand-transcribing a table is where errors creep in, even with the table on screen.
What we'll do differently: Paste figures straight from the tool's output, or have the script print the summary line itself (e.g. the lowest pair per theme). Re-read each number against the output before posting to an append-only record.

## 2026-09-25 · lawyer · A gate is only as strong as the field it reads
What happened: Reviewing spawn.py against Article 3.8, every rule had a refusal and a test. But `activate` checks the `status:` line in an amendment file, and sprint.py takes voters from `votes` in the roster. Both are plain text that six offices can write. Separately, A-0019 had gone stale before its opinion was written: a later Steward amendment had already made its first item unnecessary.
What we learned: "The tool refuses" and "the rule holds" aren't the same claim. Check what the refusal reads, and who else can write it. A proposal's facts can change while it waits in the queue.
What we'll do differently: For every enforcement claim, name the field it depends on and who can write that field. Before writing an opinion, re-check the proposal's premises against the current files, not the proposal's own description of them.

## 2026-09-25 · auditor · UTC strings aren't local time, and tests that pass in winter can fail in summer
What happened: Reviewing P-001 v002, I found `server.py` turning UTC event timestamps into epoch seconds with `time.mktime(time.strptime(ts)) - time.timezone`. `mktime` reads the struct as local time and applies daylight saving time, but `time.timezone` is only the standard offset. On this machine in PDT, every derived time runs one hour early: the "stuck after 2 hours" rule fires at 1 hour, next-run times are an hour early, and the last-60-minutes activity chart shows the hour before. The setup session reported the tests passing, and none of them pin a timezone or a date in DST.
What we learned: Any code that parses a UTC string with local-time functions is right for only part of the year, and only in some zones. `calendar.timegm` or `datetime.fromisoformat(...).timestamp()` is the correct conversion. A reported "tests pass" can't stand in for acceptance, especially when the reviewer can't run the tests.
What we'll do differently: When reviewing any code that handles time, grep for `mktime`, `time.timezone`, and naive `datetime`, and ask whether the tests set a DST timezone (e.g. `TZ=America/Los_Angeles` with a July date). State in every acceptance what was checked by reading code and what was actually run.

## 2026-09-25 · auditor · A run's capture records who was running, not who wrote the file; and Write without delete leaves mistakes behind
What happened: Checking incidents, I found my previous run's capture (events #580–593) credits the Auditor with a spawn proposal (`agents/_proposed/charlie`), `roster.json`, `amendment-021.md`, and edicts E-0067 to E-0071. I wrote none of them. The Steward and the setup session were working while my run was open, and the runner diffs the whole tree at run end. Separately, I created a stray scratch file with Write in this run. `rm` isn't in AUDITOR_TOOLS, and `repos.sh commit` stages everything with `git add -A`, so I couldn't remove the file or commit around it.
What we learned: In the event log, "actor" means "the office whose run was open", not "the author". Reading it as authorship would have wrongly shown the Auditor acting outside its lane. An office that can create files but not delete them has to get every Write right the first time, because a mistake blocks its own commit until someone else cleans it up.
What we'll do differently: When an event's actor matters (lane violations, misattribution), check it against the run's transcript before concluding anything. Write only to paths I mean to keep, and never use scratch files in the repo.

## 2026-09-25 · lawyer · A flag that says who you are is not an identity check, and a broad grant voids narrow ones
What happened: Reviewing P-001 v003, I found `perms.py` accepts any caller who passes `--steward`, and `supervise.py` accepts any `--by`. Prototyper and Media hold `Bash(python3:*)`, so either could grant itself a vote or tools, recorded as the Steward's edict. The dashboard's writes also accept requests with no Origin header, so any local script counts as "the Steward's click".
What we learned: On one OS user, no tool can prove the Steward is the caller. And one broad grant (`python3:*`) makes every narrow `Bash(python3 agents/bin/x.py sub:*)` gate advisory for the offices that hold it. Authority claims have to be checked against something the caller can't set (the runner's environment, the run window in the event log), and they have to be detectable after the fact.
What we'll do differently: For any tool that acts "as the Steward" or "as a supervisor", ask how the tool knows who is calling, and list which offices can reach it through broad grants, not only through their named ones.

## 2026-09-25 · pm · A completeness check can be narrower than the rule it checks
What happened: Opening Sprint 0's proposal phase, `sprint.py check` listed only the six voting offices as missing. Art. 14.2 requires every office, voting or not, to file one proposal, so the Scribe, Lawyer, and Auditor would never show up as late. I first wrote on the board that they "may" file, then corrected it before the run ended.
What we learned: A tool's "complete" means complete by the tool's own definition. Before reporting a phase as ready, compare what the tool checks with what the Charter requires.
What we'll do differently: At every sprint gate, check the Charter article directly as well as the tool's output, and name any office the tool skips. The mismatch goes to the Scribe as a candidate Class C fix to `sprint.py`.

## 2026-09-25 · researcher · A benchmark's "test set" may not be one we can score; and mirrors disagree
What happened: Checking AVeriTeC for P-002, fever.ai calls the shared-task test set "blind", while a page summary of the official HF repo said its test labels were released. The README itself didn't say either way, and the file listing needed a login. Separately, the xAI terms page refused my fetcher, and a search summary offered a confident answer about its contents.
What we learned: For a benchmark, "has a test split" and "has gold labels we can score against" are different facts, and summaries blur them. A page we can't open is unverified, however confident the search snippet.
What we'll do differently: When choosing a dataset, record which splits are labeled, counted from the files, and draw our own locked split from the labeled pool. Mark any terms page we can't read as "not verified" and ask a human to open it.

## 2026-09-25 · prototyper · Split the paid step from the build, so a pending decision gates only the spend
What happened: P-002 v001 was planned as one item: build the harness and run it on paid APIs. Three Steward decisions are still open (the $75 budget, the AVeriTeC license, and the xAI terms), so as written, the whole version waited on all three.
What we learned: Almost all of a benchmark harness (split, hashing, the resume logic, metrics, the test-split refusal, the cost guard) can be built and tested against a seeded, clearly labeled simulated judge for $0. Only the real run needs the money and the license. Each open decision can also have a stated fallback (FEVER as the dataset, a config without Grok), so a "no" or a slow answer doesn't stall the work.
What we'll do differently: When a proposal includes spend, write the paid step as its own work item with its own gate, and grade the rest of the item on what can be done for $0. Name the fallback for each pending decision in the proposal itself.

## 2026-09-25 · media · Check a tool's prerequisites before promising work that uses it
What happened: Writing Media's Sprint 0 proposal, I checked what the video tools actually need before committing to them. `agents/bin/tts.sh` is in MEDIA_TOOLS and Piper is on PATH, but the voice model lives outside the repo, where Media's tools can't look, so it's unconfirmed. `npx playwright` is granted, but no Playwright package is installed, and installing one needs approval (POLICIES §4).
What we learned: A grant in `*_TOOLS` means you're allowed to run the command, not that it will work. A proposal that depends on a tool whose prerequisites haven't been checked can fail on day one for reasons that have nothing to do with the work.
What we'll do differently: Before a proposal depends on a tool, check the binary, its data files, and its packages. List anything unconfirmed under Risks with a fallback that needs no new install (here: terminal captures and stills instead of browser recording).

## 2026-09-25 · lawyer · "IDs, not text" isn't enough when a model's reasoning quotes the text
What happened: The P-002 license record says public results carry claim IDs, not claim text. That handles AVeriTeC's NC terms and FEVER's share-alike. But judge outputs usually include a rationale, and rationales quote the claim and its evidence. Committing them would redistribute the licensed data through a side door.
What we learned: A licensing rule written in terms of input fields can be defeated by output fields that echo those inputs. The rule has to list which fields are *allowed* in committed artifacts, not which ones are forbidden.
What we'll do differently: License conditions on data become an allowlist of artifact fields, enforced by a test that fails on any other field. For any dataset with NC or SA terms, check model outputs as well as inputs.

## 2026-09-25 · auditor · Acceptance only covers what's submitted; check what's actually running
What happened: A-0028's web terminal (`shell_bridge.py`, a `/ws/shell` route, and vendored xterm) went into `dashboard/` through a Steward amendment and a setup-session commit. No P-001 version named it, so the Article 21.3 gate never saw it. I found it only because an out-of-band incident listed the files. Reading it, I also found the token endpoint checks Host but not Origin. An Origin check only stops browsers, not a local script that sets the header itself.
What we learned: Version acceptance is a gate on submissions, not on the product. Code can reach the running product by other routes (Steward amendments, setup sessions, interactive terminals), and it arrives unreviewed. Separately, Origin and Host checks defend against web pages, not against local processes. Any office with a broad grant (`python3:*`, `node:*`) can pass them.
What we'll do differently: At each run, compare the files changed under a project's code folder since the last accepted version against that version's Plan, and flag anything no version covers. When a local endpoint claims to be "Steward-only", ask what stops a local non-browser client, and name which offices could be one.

## 2026-09-25 · social · A refused tool ends the run, so read the grant before the first call
What happened: Earlier Social runs called a shell command the office is not granted. Headless Grok cancels the whole run on a refused tool, so the Sprint 0 proposal never got written. A-0037 and E-0102 now say Social has no shell, and may write only the outbox, the board, LEARNINGS, and its own proposal file.
What we learned: For an office whose first refused tool call aborts the run, the grant list is a precondition, not a recovery step. Sprint phase can be read from `sprint.json` when `sprint.py` is not granted.
What we'll do differently: Never call a command tool. Read tasks from `org/tasks/tsk.json` and the sprint from `sprints/`, and ask the Project Manager to run `sprint.py check`.

## 2026-09-25 · auditor · A gate keyed on Charter text is opened by recording the code that holds the key
(Appended by the Scribe at the Auditor's request, from `org/board/2026-09-25-standup.md`, 02:00:38Z; the Auditor has no Edit.)
What happened: The A-0030 features unlock when CHARTER.md contains a marker string. Part V holds the full text of the gating code and its tests, and both contain the marker. So recording the code satisfies the gate before the article passes.
What we learned: A gate must read a field that only ratification can set: the amendment's ratified status in the verified log. It should never read a string search over a file that also holds the code itself.
What we'll do differently: When reviewing any "until ratified" gate, grep Part V and the tests for its marker.

## 2026-09-25 · scribe · A number that's been corrected once gets copied wrong again unless you name the correction
What happened: The Weave blog needed P-005's eval spend. The version file said $4.33, the eval-budget `#decision` repeats $4.33, and the per-eval results files add up to $4.33 too (they hold the reruns' cost in place of the first runs'). The Auditor's acceptance review had already corrected the figure to $4.24 for the first runs and $4.44 with the reruns. Three records pointed to one wrong number, and only one pointed to the right one.
What we learned: When a figure has been corrected, the wrong one usually survives in more places than the correction does, and each copy looks authoritative. Adding up the raw results files can reproduce the error rather than catch it, when those files overwrite the earlier runs.
What we'll do differently: Before citing any figure in public writing, search the project discussion for "correction" and the Auditor's review. Cite the corrected number and say where it came from. List the records that still carry the old number, so their owners can fix them.

## 2026-09-25 · lawyer · "Their docs say" is only sourced if we link their docs
What happened: The Weave blog draft says "W&B's own documentation says" that its native integrations send full prompts. The only link behind that sentence is our own spec's notes, which repeat the claim without a link to W&B.
What we learned: A claim about what a third party says, backed only by our own record of it, is secondhand. Every copy of it looks sourced, because each one cites the one before it. POLICIES §1 needs the source we actually read.
What we'll do differently: When a public draft attributes a statement to an outside party, check that the chain of links ends at that party's own page. If it doesn't, ask for that link, or for the sentence to be reworded as our own reading.
