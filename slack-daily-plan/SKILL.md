---
name: slack-daily-plan
description: >-
  Read recent Slack activity (mentions, DMs, priority channels, and threads),
  extract actionable asks, and produce a high-level prioritized plan for what to
  accomplish today. Use when the user asks for a daily plan, morning priorities,
  what to work on next from Slack, a Slack triage, or a ranked todo list from
  messages and mentions.
---

# Slack Daily Plan

Turn **Slack signal into a ranked daily plan**. Scan mentions, DMs, key channels, and active threads; classify urgency; deliver a short, ordered list of what matters most today — not a dump of every message.

## Core Rules

1. **Read before planning** — never invent priorities from memory; pull live Slack context first.
2. **Prefer actionable items** — decisions requested of the user, blockers they own, deadlines today/tomorrow, and explicit @-asks beat FYI noise.
3. **Rank, don't dump** — output a prioritized plan (typically 3–7 items). Defer or fold the rest into "Later / parking lot".
4. **Cite sources** — every plan item must link or cite channel/DM + approximate time + who asked.
5. **Do not send Slack messages** unless the user explicitly asks to reply, ack, or post the plan.
6. **Respect privacy** — do not paste full private DM transcripts into public channels, PRs, or shared docs.

## When This Applies

| Use this skill | Skip |
|----------------|------|
| Morning "what should I do today?" from Slack | Pure GitHub issue backlog (use [github-issues](../github-issues/SKILL.md)) |
| Triage mentions / DMs into a ranked plan | User already gave an explicit ordered task list |
| "Prioritize my Slack" / standup prep from Slack | Implementing code with no planning ask |
| Catch up after time off via Slack signals | Sending bulk Slack replies without a plan request |
| Slack-only triage when user locks to Slack | Day plan across Slack + email + Jira (use [daily-plan](../daily-plan/SKILL.md)) |

When unsure and the user mentions Slack + priorities/plan/day, **apply this skill**.

## Prerequisites

### Preferred — Slack MCP

If a Slack MCP server is configured, discover its tools and use them. Typical capabilities:

| Need | Typical tool patterns |
|------|----------------------|
| Who am I / workspace | `auth_test`, `get_user`, workspace info |
| DMs and MPIM | list conversations, history |
| Mentions | search `from:@me` / mentions, or notification feeds |
| Channel history | `conversations_history`, `conversations_replies` |
| Resolve user/channel names | users/conversations lookup |

Always call MCP schema discovery for the Slack server before invoking tools. Prefer **read-only** tools.

### Fallback — Slack Web API (`curl`)

When MCP is unavailable but a token exists (`SLACK_BOT_TOKEN` or `SLACK_USER_TOKEN`):

```bash
test -n "${SLACK_USER_TOKEN:-$SLACK_BOT_TOKEN}" || echo "No Slack token; configure Slack MCP or set SLACK_USER_TOKEN"
TOKEN="${SLACK_USER_TOKEN:-$SLACK_BOT_TOKEN}"

# Identity
curl -s -H "Authorization: Bearer $TOKEN" https://slack.com/api/auth.test

# Unread DMs / conversations (user token works best for personal triage)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://slack.com/api/conversations.list?types=im,mpim,public_channel,private_channel&limit=200"
```

User tokens triage personal mentions and DMs better than bot tokens. If only a bot token is available, limit scope to channels the bot is in and say so in the plan.

### Blocked access

If neither MCP nor a usable token works:

1. Say Slack is unreachable.
2. Ask the user to connect Slack MCP or provide a read token / paste the threads they care about.
3. Do **not** fabricate a Slack-backed plan.

Optional: offer a lightweight plan from Gmail ([gmail-daily-plan](../gmail-daily-plan/SKILL.md)), Jira ([jira-daily-plan](../jira-daily-plan/SKILL.md)), GitHub ([github-issues](../github-issues/SKILL.md)), or calendar notes only if the user agrees — label it as **not Slack-sourced**.

## Workflow Checklist

Copy and track:

```
Slack daily plan:
- [ ] Access verified (MCP or token)
- [ ] Time window set (default: since yesterday morning / last ~24–36h)
- [ ] Mentions + DMs scanned
- [ ] Priority channels scanned
- [ ] Items classified and ranked
- [ ] Plan delivered (ordered list + parking lot + unknowns)
- [ ] Optional: user asked whether to act on P1 (reply / start work)
```

## 1. Scope the time window

Default window unless the user specifies otherwise:

| Context | Window |
|---------|--------|
| Typical morning plan | Last **24–36 hours** + anything still unmarked / unreplied |
| Monday / after time off | Last **business day they were active** through now (ask if unclear) |
| User says "today only" | Since local midnight |
| User names channels | Those channels + DMs/mentions still included |

Record the user's timezone if known; otherwise state assumptions (e.g. "assuming local morning").

## 2. Gather Slack signal

Pull in this order (stop expanding when you have enough for a solid plan — usually ≤20 candidate items):

### 2a. Direct asks (highest signal)

1. **DMs and group DMs** with recent messages or unreplied asks
2. **@-mentions** of the user (and @channel/@here in channels they own or moderate, if visible)
3. **Threads they were pulled into** (replies waiting on them)

### 2b. Priority channels

Scan recent history in:

- Channels the user names
- Channels they starred / mark as priority (if API exposes that)
- Otherwise: engineering/product/incident channels with recent traffic — **sample**, don't boil the ocean

Skip high-volume noise channels (meme, random) unless mentioned.

### 2c. What to extract per candidate

For each possible work item, capture:

| Field | Example |
|-------|---------|
| Ask | "Review the deploy PR before 2pm" |
| Who | `@alex` |
| Where | `#deployments` thread |
| When | today 09:14 |
| Deadline | "before 2pm" / EOD / none |
| Blocking? | yes — release waits on review |
| Type | decision / review / reply / implement / FYI |

Ignore pure FYIs, bots without action, emoji-only reactions, and resolved threads unless they reopen work.

## 3. Classify and prioritize

Rank every actionable item:

| Priority | Criteria |
|----------|----------|
| **P0 — Do first** | Production/security incident; explicit "ASAP"/"blocked on you"; deadline within a few hours |
| **P1 — Today** | Clear ask owned by the user; deadline today; stakeholder waiting on a decision or review |
| **P2 — Today if capacity** | Useful progress, soft deadlines, non-blocking reviews |
| **P3 — Later** | Nice-to-have, no deadline, FYI that might become work |
| **Drop / ignore** | Resolved, spam, not directed at the user, duplicate of a higher item |

**Tie-breakers** (same priority): external blockers waiting on the user → customer/stakeholder impact → explicit deadline sooner → oldest unreplied ask.

**Deduplicate:** same ask across DM + channel → one plan item, cite both sources.

**Ambiguity:** if ownership or deadline is unclear, put under **Needs clarification** with one suggested clarifying question — do not invent urgency.

## 4. Deliver the plan

Present a **high-level** daily plan. Keep it scannable — no message dumps.

```markdown
## Daily plan — <weekday, date> (<timezone assumption>)

**Window scanned:** <start> → <now>
**Sources:** DMs, mentions, <channels…>

### Priority order

1. **[P0] <outcome-oriented title>**
   - Why now: <deadline / blocker>
   - From: <person> in <channel/DM> (<time>)
   - Next step: <one concrete action>

2. **[P1] …**
3. …

### Needs clarification
- <item> — ask: "<one question>"

### Parking lot (not today unless capacity)
- <P2/P3 items, one line each>

### Intentionally skipped
- <noise categories or empty: "no incidents, N FYI-only bot posts">
```

Rules for the write-up:

- Titles are **outcomes** ("Unblock release: review PR #452"), not "Check Slack".
- **One next step** per item — the smallest useful action.
- Cap the main list at **~7**; park the rest.
- If nothing actionable: say so, list what was scanned, and offer optional deep-dives (specific channel, longer window).

After delivering, ask whether to:

- Start on **P0/P1** in the codebase
- Draft Slack replies for waiting threads
- Re-run with a different window or channel set, or combine sources via [daily-plan](../daily-plan/SKILL.md)

Do not start implementation or send messages until the user confirms — unless they already said "plan and then do P0".

## 5. Optional follow-through

| User ask | Action |
|----------|--------|
| Start P0/P1 work | Switch to implementation; use [orchestrate](../orchestrate/SKILL.md) if multi-step |
| Draft replies | Draft text for the user to send; post only with explicit approval |
| Publish the plan | Post a short version to a user-named channel/DM only after approval |
| Replan midday | Re-scan a shorter window; update the ranked list |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Listing every unread message | Rank 3–7 actionable outcomes |
| Planning with stale/cached Slack memory | Fresh MCP/API read for the window |
| Marking FYI channels as P0 | Require deadline, blocker, or explicit ask |
| Posting the plan or acks unprompted | Deliver locally; send only on request |
| Hiding uncertainty as fake urgency | Use "Needs clarification" |
| Dumping private DM bodies into public posts | Cite "DM with @user" + paraphrase the ask |

## Cross-References

- Multi-source daily plan (Slack + Gmail + Jira): [daily-plan](../daily-plan/SKILL.md)
- Gmail-sourced daily plan: [gmail-daily-plan](../gmail-daily-plan/SKILL.md)
- Jira-sourced daily plan: [jira-daily-plan](../jira-daily-plan/SKILL.md)
- Multi-step execution after planning: [orchestrate](../orchestrate/SKILL.md)
- Repo issue backlog (non-Slack): [github-issues](../github-issues/SKILL.md)
- Shipping resulting code work: [github-publish](../github-publish/SKILL.md)

## Additional Resources

- Sample scans and plan output: [examples.md](examples.md)
