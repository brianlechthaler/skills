# Jira Daily Plan Examples

## Browser scrape (primary fallback)

When the user is signed into Jira in the browser and asks to scrape:

```text
1. Open https://<site>.atlassian.net/jira/your-work (or user-named board URL)
2. Capture visible assigned / In Progress / Blocked cards: KEY, summary, status, due, priority
3. Open the active sprint board; sample To Do + In Progress + Flagged columns
4. Open only issues that look actionable; paraphrase latest @ask or blocker link
5. Stop if CAPTCHA / login interstitial appears — ask for MCP, API token, or pasted keys
```

## MCP-style scan (pseudocode)

Discover Jira MCP tools first, then approximate this sequence:

```text
1. myself / site → confirm account + cloud id
2. JQL: assignee = currentUser() AND resolution = EMPTY (max ~20)
3. JQL or board: active sprint issues for the named project
4. JQL: due soon / overdue assigned to me
5. Fetch comments on top candidates only when ask/blocker is unclear from fields
```

## REST API-style search

```bash
BASE="${JIRA_BASE_URL%/}"
USER="${JIRA_USER:-$JIRA_EMAIL}"
TOKEN="${JIRA_API_TOKEN:-$ATLASSIAN_API_TOKEN}"

curl -s -u "$USER:$TOKEN" -G "$BASE/rest/api/3/search/jql" \
  --data-urlencode 'jql=assignee = currentUser() AND resolution = EMPTY AND (duedate <= endOfDay("+1d") OR statusCategory = "In Progress" OR priority in (Highest, High)) ORDER BY priority DESC, duedate ASC' \
  --data-urlencode 'maxResults=20' \
  --data-urlencode 'fields=summary,status,priority,duedate,issuetype,updated,issuelinks'
```

## Sample ranked output

```markdown
## Daily plan — Wednesday, 2026-07-15 (assuming America/Los_Angeles)

**Window scanned:** Sprint 48 → Wed 09:30
**Sources:** Jira (browser scrape), assigned, due/blocked, board Payments

### Priority order

1. **[P0] Unblock checkout: fix null order total on PAY-442**
   - Why now: flagged blocker; PAY-455 waiting; due today
   - From: PAY-442 — "Null total on checkout retry" (Blocked; due today)
   - Next step: Reproduce on staging; confirm fix path; start PR

2. **[P1] Land review comments on PAY-418 webhook retries**
   - Why now: sprint commitment; reviewer pinged yesterday
   - From: PAY-418 — "Retry policy for billing webhooks" (In Progress; updated yesterday)
   - Next step: Address two open review threads; request re-review

3. **[P1] Confirm scope for CUST-210 escalation**
   - Why now: customer severity High; PM asking for ETA by noon
   - From: CUST-210 — "Export CSV truncates rows" (To Do; priority High)
   - Next step: Reply with reproduce status and ETA

4. **[P2] Spike search ranking experiment design**
   - Why now: soft sprint stretch goal
   - From: SRCH-77 — "Ranking experiment design" (To Do; no due)
   - Next step: Sketch options doc only if P0/P1 clear

### Needs clarification
- PAY-401 — ask: "Is this still yours after the reorg, or should it move to platform?"

### Parking lot
- PAY-390 docs polish (P3)
- Watch-only EPIC-12 updates (FYI)

### Intentionally skipped
- Done column cards; 6 unassigned backlog items; automation comments without asks
```

## Empty / quiet morning

```markdown
## Daily plan — Monday, 2026-07-13 (UTC)

**Window scanned:** active sprint + assigned open
**Sources:** Jira (MCP), assigned, Your work

### Priority order
_No P0/P1 asks found._

### Parking lot
- PAY-388 flaky CI follow-up — optional when free

### Intentionally skipped
- Done/Closed; unassigned Triage queue sample

Want me to widen to all open assigned, include board Platform, combine with Slack/Gmail, or pull GitHub issues instead?
```
