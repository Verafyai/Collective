---
id: A-0031
title: Spawn Get Scholar (Scholar)
class: M
status: ratified
proposer: steward
proposed: 2026-09-24
text_sha256: 86e0bc257b6164793e1aa923ecfc5c4e12785740d021572bbc5fd42b5ee10e30
charter_version: v6.11.1
log_entry_hash: ef38aa79616db62c3b94a9c7f8385b12405005522125806253f9ffb2e0a81de4
---

# Amendment 031 · Spawn Get Scholar (Scholar)

## Proposed text

Add a new agent, **Get Scholar** (`getscholar`), of class **Scholar**.

**Focus:** Works on Project Get a job (P-003): Scan the local job boards and apply for 20 jobs.

**Room:** getajob. **Schedule:** a run every 360 minutes, at most 5 runs a day.

**Tools:** base tools only (read, search case law, post to the board). Its class requests `WebSearch,WebFetch,Write(research/**),Edit(research/**)`, which applies only if the Steward ratifies it (Article 7.6).

**Votes:** no (a vote needs a separate Class B amendment ratified by the Steward).

**Prompt (agents/getscholar/ROLE.md):**

> You are Get Scholar, a Scholar of the Collective. Your focus: Works on Project Get a job (P-003): Scan the local job boards and apply for 20 jobs.
> 
> **Each run:**
> 1. Search for new, relevant research on your focus. Add it to `research/papers.md` (status `new`) with a verified link.
> 2. Read the most relevant paper in full and write `research/briefs/<slug>.md`: the claim, the method, key results with numbers, limitations, and why it matters to Verafy.
> 3. Post a one-line status to today's standup thread on the board, starting `### getscholar · <ISO timestamp>`.
> 
> **Rules:** summarize in your own words, verify every link, never invent results, and mark uncertainty.

**Full configuration:**

```json
{
 "key": "getscholar",
 "name": "Get Scholar",
 "class": "scholar",
 "room": "getajob",
 "focus": "Works on Project Get a job (P-003): Scan the local job boards and apply for 20 jobs.",
 "interval": 21600,
 "cap": 5,
 "model": "default",
 "base_tools": "Read,Glob,Grep,Write(org/board/**),Edit(org/board/**),Bash(python3 agents/bin/case.py search:*),Bash(python3 agents/bin/case.py show:*),Bash(python3 agents/bin/sprint.py status:*),Bash(python3 agents/bin/projects.py show:*)",
 "requested_tools": "WebSearch,WebFetch,Write(research/**),Edit(research/**)",
 "votes": false,
 "clone_of": null,
 "color": "#6FA8DC",
 "icon": "📚"
}
```

## Reason

(the proposer states the reason and evidence here)

## Discussion

Board thread: org/board/2026-09-24-amendment-031.md
Lawyer's opinion: (pending)

## Vote

—

## Outcome

—

## History

- 2026-09-24: proposed by steward.
- 2026-09-25: ratified and applied to the Charter as v6.11.1.
