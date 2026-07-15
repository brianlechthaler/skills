# Slack Daily Plan Examples

## MCP-style scan (pseudocode)

Discover Slack MCP tools first, then approximate this sequence:

```text
1. auth / whoami → confirm workspace + user id
2. list DMs + MPIMs with recent activity
3. search or notifications for mentions since yesterday
4. conversations.history on #eng, #incidents, #product (or user-named channels)
5. conversations.replies for threads where the user was @-mentioned
```

## Web API fallback — mentions and recent DMs

```bash
TOKEN="${SLACK_USER_TOKEN:-$SLACK_BOT_TOKEN}"
OLDEST=$(date -u -d '36 hours ago' +%s 2>/dev/null || date -u -v-36H +%s)

# Search mentions (user token)
curl -s -G -H "Authorization: Bearer $TOKEN" \
  --data-urlencode "query=@me" \
  --data-urlencode "sort=timestamp" \
  --data-urlencode "count=20" \
  https://slack.com/api/search.messages

# DM history example (replace CHANNEL with IM id)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://slack.com/api/conversations.history?channel=${CHANNEL}&oldest=${OLDEST}&limit=50"
```

## Sample ranked output

```markdown
## Daily plan — Wednesday, 2026-07-15 (assuming America/Los_Angeles)

**Window scanned:** Tue 18:00 → Wed 09:30
**Sources:** DMs, mentions, #incidents, #eng-deploys, #product

### Priority order

1. **[P0] Unblock prod: confirm rollback decision on payments-api**
   - Why now: incident thread still open; on-call waiting on your call
   - From: @sam in #incidents (08:12)
   - Next step: Reply with go/no-go on rollback vs hotfix

2. **[P1] Review and approve deploy PR for checkout flags**
   - Why now: asks for review before 14:00 ship window
   - From: @alex in #eng-deploys (yesterday 17:40) + DM bump (08:01)
   - Next step: Open PR link, review diff, approve or request changes

3. **[P1] Answer design question on billing webhook retries**
   - Why now: @-mention; blocks @jordan's implementation today
   - From: @jordan in #product thread (yesterday 16:05)
   - Next step: Reply with retry policy choice (at-least-once vs idempotent keys)

4. **[P2] Skim RFC comments on search ranking**
   - Why now: soft ask, no deadline
   - From: @casey in #eng (yesterday 11:20)
   - Next step: Read RFC section 3; leave one comment if you disagree

### Needs clarification
- DM from @lee about "the dashboard thing" — ask: "Which dashboard (admin vs customer) and what outcome do you need today?"

### Parking lot
- #random party planning poll (P3)
- Changelog reminder bot in #eng (FYI)

### Intentionally skipped
- 12 emoji-only replies; 3 resolved threads; #memes digest
```

## Empty / quiet morning

```markdown
## Daily plan — Monday, 2026-07-13 (UTC)

**Window scanned:** last 36h
**Sources:** DMs, mentions, #eng

### Priority order
_No P0/P1 asks found._

### Parking lot
- #eng thread on flaky CI — optional look when free (@riley, Fri)

### Intentionally skipped
- Newsletter posts in #general; standup bot summaries

Want me to widen to 72h, add #customer-success, or pull open GitHub issues instead?
```
