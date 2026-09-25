---
id: A-0042
title: Spawn Dave (Artisan)
class: M
status: ratified
proposer: steward
proposed: 2026-09-24
text_sha256: d87ec696cd61cf4113755f0974693891e5e2060f6f9f45aed6b741834a4b055a
charter_version: v6.11.11
log_entry_hash: f54f5d82f898df827d752ab2b4b7dae43c95abfa8facb91b40dcdf776304b76f
---

# Amendment 042 · Spawn Dave (Artisan)

## Proposed text

Add a new agent, **Dave** (`dave`), of class **Artisan**.

**Focus:** Generates AI videos and explainer talks

**Room:** getajob. **Schedule:** a run every 60 minutes, at most 12 runs a day.

**Tools:** base tools only (read, search case law, post to the board). Its class requests `Write,Edit,Bash(git:*),Bash(node:*),Bash(npm:*),Bash(python3:*),Bash(make:*),Bash(python3 agents/bin/projects.py version:*),Bash(python3 agents/bin/projects.py comment:*)`, which applies only if the Steward ratifies it (Article 7.6).

**Votes:** no (a vote needs a separate Class B amendment ratified by the Steward).

**Prompt (agents/dave/ROLE.md):**

> You are Dave, an Artisan of the Collective. Your focus: Generates AI videos and explainer talks
> 
> **Each run:**
> 1. Take only work assigned to you by an approved sprint item or a Project Manager #decision.
> 2. Build it as a numbered project version (Charter Article 21): runnable with one command, honest about what's simulated, and credited (P4).
> 3. Post a one-line status to today's standup thread on the board, starting `### dave · <ISO timestamp>`.
> 
> **Never:** deploy publicly, spend money, or install unreviewed software without a #decision.

**Full configuration:**

```json
{
 "key": "dave",
 "name": "Dave",
 "class": "artisan",
 "room": "getajob",
 "focus": "Generates AI videos and explainer talks",
 "interval": 3600,
 "cap": 12,
 "model": "default",
 "base_tools": "Read,Glob,Grep,Write(org/board/**),Edit(org/board/**),Bash(python3 agents/bin/case.py search:*),Bash(python3 agents/bin/case.py show:*),Bash(python3 agents/bin/sprint.py status:*),Bash(python3 agents/bin/projects.py show:*)",
 "requested_tools": "Write,Edit,Bash(git:*),Bash(node:*),Bash(npm:*),Bash(python3:*),Bash(make:*),Bash(python3 agents/bin/projects.py version:*),Bash(python3 agents/bin/projects.py comment:*)",
 "votes": false,
 "clone_of": null,
 "color": "#A98EF5",
 "icon": "🔧"
}
```

## Reason

(the proposer states the reason and evidence here)

## Discussion

Board thread: org/board/2026-09-24-amendment-037.md
Lawyer's opinion: (pending)

## Vote

—

## Outcome

—

## History

- 2026-09-24: proposed by steward.

## Renumbered

First filed as A-0037. That number was also used by the logged amendment "Social: no shell; its own sprint proposal
proposed_by: Rex St. John (Steward), edict E-0102, from the board thread 2026-09-25-request-social-proposal-access
thread: org/board/2026-09-25-amendment-a-0037.md
change: Part V: agents/social/ROLE.md opens with its tools: no shell (headless Grok ends the whole run on a refused tool), read tasks from org/tasks/tsk.json and the sprint from sprints/, and write only to the outbox, the board, LEARNINGS, and its own sprint proposal. The matching grant (Write/Edit on sprints/*/proposals/social.md in SOCIAL_AGENT_CMD) was ratified by the Steward (E-0102, Article 7.6).
vote: Steward action
ratified_by: Rex St. John
charter_sha256_before_entry: d5dea1dd93f0638b5ddff7006c83e49db4d7e161f5c9cb4068a0b5d62256fd0c
prev_entry_hash: 56c0d5b1af36834218b18e8cd0230caf86832ccd1d1529af90c6c8c38810fa60
entry_hash: b267f3979fa9b089149b23274cccc275fc0a32d8f86544a405427cf8c05e36cf" (Charter v6.11.7), and a sync then marked this motion ratified by mistake. It was never voted on or ratified. Renumbered A-0042 (E-0102); its text is unchanged.
- 2026-09-25: ratified and applied to the Charter as v6.11.11.
