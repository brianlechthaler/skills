# Gmail Daily Plan Examples

## MCP-style scan (pseudocode)

Discover Gmail MCP tools first, then approximate this sequence:

```text
1. profile / whoami → confirm account email
2. search is:unread newer_than:2d (exclude promotions/social)
3. search is:important OR is:starred in the same window
4. fetch thread snippets for top ~20 candidates
5. open full bodies only when ask/deadline is unclear from snippet
```

## Browser scrape fallback

When the user is signed into Gmail in the browser and asks to scrape:

```text
1. Open https://mail.google.com/mail/u/0/#inbox (or user-specified account index)
2. Optionally run Gmail search: is:unread newer_than:2d -category:promotions
3. For each visible row, capture: unread state, star/important, sender, subject, time
4. Open only threads that look actionable; paraphrase the ask (do not dump full body)
5. Stop if CAPTCHA / login interstitial appears — ask for MCP or pasted threads
```

## API / IMAP-style search

```bash
# Gmail search operators (paste into Gmail UI, MCP, or API q= parameter)
q='is:unread newer_than:2d -category:promotions -category:social to:me'

# Example: gcloud / access token presence check only
test -n "${GOOGLE_ACCESS_TOKEN:-}" && echo "token present — use Gmail API users.messages.list"
```

## Sample ranked output

```markdown
## Daily plan — Wednesday, 2026-07-15 (assuming America/Los_Angeles)

**Window scanned:** Tue 18:00 → Wed 09:30
**Sources:** Gmail (browser scrape), unread, important/starred, label:Work

### Priority order

1. **[P0] Unblock prod: confirm rollback decision for payments-api**
   - Why now: on-call escalated; decision needed before 10:00
   - From: Sam Lee — "INC-442 payments-api rollback?" (08:12)
   - Next step: Reply with go/no-go on rollback vs hotfix

2. **[P1] Approve vendor SOW for Acme**
   - Why now: procurement needs signature by EOD
   - From: Alex Kim — "SOW — Acme (needs your approval)" (yesterday 17:40)
   - Next step: Open PDF, confirm scope/dates, reply approve or questions

3. **[P1] Answer design question on billing webhook retries**
   - Why now: blocks Jordan's implementation today
   - From: Jordan Park — "Retry policy for billing webhooks?" (yesterday 16:05)
   - Next step: Reply with retry policy choice (at-least-once vs idempotent keys)

4. **[P2] Skim RFC comments on search ranking**
   - Why now: soft ask, no deadline
   - From: Casey Ng — "Comments welcome on search ranking RFC" (yesterday 11:20)
   - Next step: Read section 3; reply only if you disagree

### Needs clarification
- From Lee Ortiz — "the dashboard thing" — ask: "Which dashboard (admin vs customer) and what outcome do you need today?"

### Parking lot
- Conference CFP reminder (P3)
- Weekly ops digest (FYI)

### Intentionally skipped
- 8 newsletters; 4 shipping notifications; 2 calendar accepts with no ask
```

## Empty / quiet morning

```markdown
## Daily plan — Monday, 2026-07-13 (UTC)

**Window scanned:** last 36h
**Sources:** Gmail (MCP), unread, important

### Priority order
_No P0/P1 asks found._

### Parking lot
- Thread on flaky CI from Riley (Fri) — optional look when free

### Intentionally skipped
- Promotions tab; social notifications; noreply digests

Want me to widen to 72h, include label:Clients, combine with Slack, or pull open GitHub issues instead?
```
