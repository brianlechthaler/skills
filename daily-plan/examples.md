# Daily Plan Examples

## Parallel gather (pseudocode)

```text
1. Probe Slack MCP / token, Gmail MCP / API, Jira MCP / REST
2. In parallel (readonly):
   a. Slack: DMs + mentions + priority channels (last 24–36h)
   b. Gmail: unread + important/starred (newer_than:2d)
   c. Jira: assignee = currentUser() open + due soon + active sprint
3. Normalize candidates → merge duplicates across sources
4. Rank P0–P3 → deliver one plan
```

## Cross-source merge

Same underlying ask arriving three ways:

| Raw signal | Normalized |
|------------|------------|
| Slack `@you` in #procurement: "need SOW approval today" | Ask: approve Acme SOW |
| Gmail from Alex: subject "SOW — Acme", unreplied | Same ask |
| Jira `PROC-12` In Progress, due today | Same ask → prefer KEY in title |

**Merged plan item:**

```markdown
1. **[P0] Unblock vendor: approve Acme SOW (PROC-12)**
   - Why now: due today; Alex waiting in email + Slack
   - From: @alex in #procurement (08:10); Alex Kim — "SOW — Acme" (07:55);
     PROC-12 — "Approve Acme SOW" (In Progress; due today)
   - Next step: Review SOW PDF and approve or list blockers in PROC-12
```

## Sample ranked output (all three sources)

```markdown
## Daily plan — Wednesday, 2026-07-15 (assuming America/Los_Angeles)

**Window scanned:** Tue 18:00 → Wed 09:30
**Sources:** Slack (MCP), Gmail (MCP), Jira (REST) — #incidents, #eng-deploys; primary inbox; board Payments sprint 48

### Priority order

1. **[P0] Unblock prod: confirm rollback on payments-api**
   - Why now: open incident; on-call waiting
   - From: @sam in #incidents (08:12); PAY-901 — "payments-api 5xx spike" (Blocked)
   - Next step: Reply go/no-go on rollback vs hotfix

2. **[P1] Unblock vendor: approve Acme SOW (PROC-12)**
   - Why now: due today; multi-channel pressure
   - From: @alex in #procurement (08:10); Alex Kim — "SOW — Acme" (07:55); PROC-12 (In Progress; due today)
   - Next step: Approve or comment blockers on PROC-12

3. **[P1] Review deploy PR for checkout flags**
   - Why now: review asked before 14:00 ship window
   - From: @alex in #eng-deploys (yesterday 17:40) + DM (08:01)
   - Next step: Review PR, approve or request changes

4. **[P2] Skim RFC comments on search ranking**
   - Why now: soft ask, no deadline
   - From: @casey in #eng (yesterday 11:20)
   - Next step: Read RFC §3; leave one comment if you disagree

### Needs clarification
- Gmail from Lee "the dashboard thing" — ask: "Which dashboard and what outcome today?"

### Parking lot
- PAY-770 unstarted sprint polish (P2)
- Newsletter: "Weekly design digest" (P3)

### Intentionally skipped
- 8 Gmail promotions; 3 Done Jira cards; #memes digest

### Source gaps
- none
```

## Partial access (Gmail blocked)

```markdown
## Daily plan — Monday, 2026-07-13 (UTC)

**Window scanned:** last 36h / active sprint
**Sources:** Slack (MCP), Gmail (blocked), Jira (MCP)

### Priority order
1. **[P1] …**

### Source gaps
- Gmail unreachable — plan is Slack+Jira only; connect Gmail MCP or paste threads to include email
```

## Quiet morning

```markdown
## Daily plan — Monday, 2026-07-13 (UTC)

**Window scanned:** last 36h / active sprint
**Sources:** Slack (token), Gmail (IMAP), Jira (scrape)

### Priority order
_No actionable P0/P1 items._

### Parking lot
- Watch-only Jira epics updated by bots
- FYI Slack channel summaries

### Intentionally scanned
- Slack: DMs, mentions, #eng
- Gmail: unread + important
- Jira: assigned open + sprint board
```
