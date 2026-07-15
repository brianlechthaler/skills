---
name: gmail-daily-plan
description: >-
  Scrape or read recent Gmail activity (inbox, starred, important, unread, and
  label filters), extract actionable asks, and produce a high-level prioritized
  plan for what to accomplish today. Use when the user asks for a daily plan,
  morning priorities, email triage, what to work on next from Gmail, or a ranked
  todo list from inbox messages.
---

# Gmail Daily Plan

Turn **Gmail signal into a ranked daily plan**. Scan inbox, unread, important/starred, and priority labels; classify urgency; deliver a short, ordered list of what matters most today — not a dump of every message.

## Core Rules

1. **Read before planning** — never invent priorities from memory; pull live Gmail context first.
2. **Prefer actionable items** — decisions requested of the user, blockers they own, deadlines today/tomorrow, and explicit asks beat newsletters and FYI noise.
3. **Rank, don't dump** — output a prioritized plan (typically 3–7 items). Defer or fold the rest into "Later / parking lot".
4. **Cite sources** — every plan item must cite sender + subject + approximate time (and message/thread id or permalink when available).
5. **Do not send email** unless the user explicitly asks to reply, draft, or forward.
6. **Respect privacy** — do not paste full private email bodies into public channels, PRs, or shared docs; paraphrase asks.

## When This Applies

| Use this skill | Skip |
|----------------|------|
| Morning "what should I do today?" from email | Pure GitHub issue backlog (use [github-issues](../github-issues/SKILL.md)) |
| Triage inbox / unread into a ranked plan | User already gave an explicit ordered task list |
| "Prioritize my email" / standup prep from Gmail | Implementing code with no planning ask |
| Catch up after time off via Gmail signals | Bulk sending replies without a plan request |
| Slack+email day plan when user wants Gmail | Slack-only triage (use [slack-daily-plan](../slack-daily-plan/SKILL.md)) |

When unsure and the user mentions Gmail/inbox/email + priorities/plan/day, **apply this skill**.

## Prerequisites

### Preferred — Gmail MCP

If a Gmail MCP server is configured, discover its tools and use them. Typical capabilities:

| Need | Typical tool patterns |
|------|----------------------|
| Who am I / profile | `get_profile`, auth/user info |
| List messages | inbox, unread, important, starred, label queries |
| Search | Gmail search operators (`is:unread`, `newer_than:2d`, `to:me`, etc.) |
| Read thread | fetch message/thread body or snippet |
| Labels | list/apply labels (read-only unless user asks to file mail) |

Always call MCP schema discovery for the Gmail server before invoking tools. Prefer **read-only** tools.

### Fallback — scrape or API without MCP

When MCP is unavailable, gather mail with the best available local method (try in order):

1. **Google API / `gcloud` / official client** with an OAuth token the user already has
2. **IMAP** (`imap.gmail.com`) if the user provides an app password or existing mail client credentials
3. **Browser scrape** of `mail.google.com` (Playwright / browser tools) when the user is already signed in and asks to scrape the UI

```bash
# Detect common local helpers (presence only — do not invent credentials)
command -v gcloud >/dev/null && echo "gcloud available"
command -v himalaya >/dev/null && echo "himalaya available"
test -n "${GOOGLE_ACCESS_TOKEN:-}" && echo "GOOGLE_ACCESS_TOKEN set"
```

#### Browser scrape notes

- Use only on accounts the user controls and is signed into.
- Prefer list/snippet views (inbox rows, search results) over opening every thread.
- Expand a thread only when the subject/snippet is insufficient to classify the ask.
- Capture: sender, subject, time, labels/badges (Important, Starred, unread), and a short ask paraphrase.
- If Google blocks automation (CAPTCHA, consent interstitial), stop and ask the user to use MCP, OAuth, or paste the threads they care about.

### Blocked access

If neither MCP nor a usable scrape/API path works:

1. Say Gmail is unreachable.
2. Ask the user to connect Gmail MCP, provide OAuth/IMAP access, sign in for browser scrape, or paste the threads they care about.
3. Do **not** fabricate a Gmail-backed plan.

Optional: offer a lightweight plan from Slack ([slack-daily-plan](../slack-daily-plan/SKILL.md)) or GitHub ([github-issues](../github-issues/SKILL.md)) only if the user agrees — label it as **not Gmail-sourced**.

## Workflow Checklist

Copy and track:

```
Gmail daily plan:
- [ ] Access verified (MCP, API/IMAP, or browser scrape)
- [ ] Time window set (default: since yesterday morning / last ~24–36h)
- [ ] Unread + important/starred scanned
- [ ] Priority labels / search queries scanned
- [ ] Items classified and ranked
- [ ] Plan delivered (ordered list + parking lot + unknowns)
- [ ] Optional: user asked whether to act on P1 (draft reply / start work)
```

## 1. Scope the time window

Default window unless the user specifies otherwise:

| Context | Window |
|---------|--------|
| Typical morning plan | Last **24–36 hours** + anything still unread / unreplied |
| Monday / after time off | Last **business day they were active** through now (ask if unclear) |
| User says "today only" | Since local midnight |
| User names labels/senders | Those filters + unread/important still included |

Record the user's timezone if known; otherwise state assumptions (e.g. "assuming local morning").

## 2. Gather Gmail signal

Pull in this order (stop expanding when you have enough for a solid plan — usually ≤20 candidate items):

### 2a. Direct asks (highest signal)

1. **Unread** messages to the user (not automated digests)
2. **Important / starred** and anything marked for follow-up
3. **Threads waiting on a reply** (user last received; no outbound reply in-window)

Useful search patterns (MCP, API, or Gmail search box):

```text
is:unread newer_than:2d -category:promotions -category:social
is:important newer_than:2d
is:starred newer_than:7d
to:me newer_than:2d -from:noreply -from:no-reply
```

### 2b. Priority labels and filters

Scan recent mail in:

- Labels the user names (e.g. `Work`, `Action`, `Clients`)
- VIP senders / aliases they mention
- Otherwise: primary inbox with recent traffic — **sample**, don't boil the ocean

Skip Promotions, Social, Forums, and newsletter noise unless mentioned.

### 2c. What to extract per candidate

For each possible work item, capture:

| Field | Example |
|-------|---------|
| Ask | "Approve the vendor SOW by EOD" |
| Who | `Alex Kim <alex@acme.com>` |
| Where | thread "SOW — Acme" / message id |
| When | today 09:14 |
| Deadline | "by EOD" / Friday / none |
| Blocking? | yes — procurement waits on signature |
| Type | decision / review / reply / implement / FYI |

Ignore pure FYIs, calendar noise without action, shipping notifications, resolved threads, and marketing unless they reopen work.

## 3. Classify and prioritize

Rank every actionable item:

| Priority | Criteria |
|----------|----------|
| **P0 — Do first** | Production/security/legal incident; explicit "ASAP"/"blocked on you"; deadline within a few hours |
| **P1 — Today** | Clear ask owned by the user; deadline today; stakeholder waiting on a decision or review |
| **P2 — Today if capacity** | Useful progress, soft deadlines, non-blocking reviews |
| **P3 — Later** | Nice-to-have, no deadline, FYI that might become work |
| **Drop / ignore** | Resolved, spam, not directed at the user, duplicate of a higher item |

**Tie-breakers** (same priority): external blockers waiting on the user → customer/stakeholder impact → explicit deadline sooner → oldest unreplied ask.

**Deduplicate:** same ask across email + Slack → one plan item; if this skill is Gmail-only, cite the Gmail thread and note Slack overlap if known.

**Ambiguity:** if ownership or deadline is unclear, put under **Needs clarification** with one suggested clarifying question — do not invent urgency.

## 4. Deliver the plan

Present a **high-level** daily plan. Keep it scannable — no message dumps.

```markdown
## Daily plan — <weekday, date> (<timezone assumption>)

**Window scanned:** <start> → <now>
**Sources:** Gmail (<MCP|API|IMAP|browser scrape>), unread, important/starred, <labels…>

### Priority order

1. **[P0] <outcome-oriented title>**
   - Why now: <deadline / blocker>
   - From: <sender> — "<subject>" (<time>)
   - Next step: <one concrete action>

2. **[P1] …**
3. …

### Needs clarification
- <item> — ask: "<one question>"

### Parking lot (not today unless capacity)
- <P2/P3 items, one line each>

### Intentionally skipped
- <noise categories or empty: "N newsletters, M shipping notices">
```

Rules for the write-up:

- Titles are **outcomes** ("Unblock vendor: approve Acme SOW"), not "Check email".
- **One next step** per item — the smallest useful action.
- Cap the main list at **~7**; park the rest.
- If nothing actionable: say so, list what was scanned, and offer optional deep-dives (specific label, longer window, or Slack).

After delivering, ask whether to:

- Start on **P0/P1** in the codebase
- Draft Gmail replies for waiting threads
- Re-run with a different window, label set, or combine with [slack-daily-plan](../slack-daily-plan/SKILL.md)

Do not start implementation or send messages until the user confirms — unless they already said "plan and then do P0".

## 5. Optional follow-through

| User ask | Action |
|----------|--------|
| Start P0/P1 work | Switch to implementation; use [orchestrate](../orchestrate/SKILL.md) if multi-step |
| Draft replies | Draft text for the user to send; send only with explicit approval |
| File / label mail | Apply labels or archive only after approval |
| Replan midday | Re-scan a shorter window; update the ranked list |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Listing every unread message | Rank 3–7 actionable outcomes |
| Planning with stale/cached inbox memory | Fresh MCP/API/scrape for the window |
| Marking newsletters as P0 | Require deadline, blocker, or explicit ask |
| Sending replies or archives unprompted | Deliver locally; send only on request |
| Hiding uncertainty as fake urgency | Use "Needs clarification" |
| Dumping full private bodies into public posts | Cite sender + subject + paraphrase the ask |
| Fighting CAPTCHAs / bypassing Google auth walls | Stop; ask for MCP, OAuth, or pasted threads |

## Cross-References

- Slack-sourced daily plan: [slack-daily-plan](../slack-daily-plan/SKILL.md)
- Multi-step execution after planning: [orchestrate](../orchestrate/SKILL.md)
- Repo issue backlog (non-email): [github-issues](../github-issues/SKILL.md)
- Shipping resulting code work: [github-publish](../github-publish/SKILL.md)

## Additional Resources

- Sample scans and plan output: [examples.md](examples.md)
