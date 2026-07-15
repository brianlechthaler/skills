---
name: jira-daily-plan
description: >-
  Scrape or read recent Jira activity (assigned issues, sprint board, due dates,
  blockers, and @mentions), extract actionable work, and produce a high-level
  prioritized plan for what to accomplish today. Use when the user asks for a
  daily plan, morning priorities, Jira triage, sprint standup prep, what to work
  on next from Jira, or a ranked todo list from assigned tickets.
---

# Jira Daily Plan

Turn **Jira signal into a ranked daily plan**. Scrape or read the assignment queue, active sprint board, due/blocked issues, and recent mentions; classify urgency; deliver a short, ordered list of what matters most today — not a dump of every ticket.

## Core Rules

1. **Read before planning** — never invent priorities from memory; pull live Jira context first.
2. **Prefer actionable items** — blockers you own, due today/tomorrow, sprint commitments, and explicit @asks beat watch-only noise and Done/Closed cards.
3. **Rank, don't dump** — output a prioritized plan (typically 3–7 items). Defer or fold the rest into "Later / parking lot".
4. **Cite sources** — every plan item must cite issue key + summary + status (and board/sprint + commenter when relevant).
5. **Do not transition, comment, or assign** issues unless the user explicitly asks.
6. **Respect privacy** — do not paste full private description/comment bodies into public channels, PRs, or shared docs; paraphrase asks.

## When This Applies

| Use this skill | Skip |
|----------------|------|
| Morning "what should I do today?" from Jira | Pure GitHub issue backlog (use [github-issues](../github-issues/SKILL.md)) |
| Triage assigned / sprint issues into a ranked plan | User already gave an explicit ordered task list |
| "Prioritize my Jira" / standup prep from the board | Implementing code with no planning ask |
| Catch up after time off via Jira signals | Bulk status transitions without a plan request |
| Scraping a Jira Cloud/Server board the user is signed into | Slack- or Gmail-only triage (use those skills) |

When unsure and the user mentions Jira/tickets/sprint/board + priorities/plan/day, **apply this skill**.

## Prerequisites

### Preferred — Jira MCP

If a Jira / Atlassian MCP server is configured, discover its tools and use them. Typical capabilities:

| Need | Typical tool patterns |
|------|----------------------|
| Who am I / site | `get_myself`, cloud id / site URL |
| Search issues | JQL search (`assignee = currentUser()`, due, sprint) |
| Issue detail | get issue fields, status, priority, links |
| Comments / mentions | list recent comments on watched/assigned issues |
| Boards / sprints | active sprint, board issues (read-only) |

Always call MCP schema discovery for the Jira server before invoking tools. Prefer **read-only** tools.

### Fallback — scrape or API without MCP

When MCP is unavailable, gather issues with the best available local method (try in order):

1. **Jira REST API** (`/rest/api/3/...` or `/rest/api/2/...`) with `JIRA_BASE_URL` + email/`JIRA_USER` and `JIRA_API_TOKEN` (or PAT the user already has)
2. **`acli` / Atlassian CLI** if installed and authenticated
3. **Browser scrape** of the user's Jira site (Playwright / browser tools) when they are already signed in and ask to scrape the UI — prefer this when tokens are missing

```bash
# Detect common local helpers (presence only — do not invent credentials)
command -v acli >/dev/null && echo "acli available"
test -n "${JIRA_BASE_URL:-}" && echo "JIRA_BASE_URL set"
test -n "${JIRA_API_TOKEN:-${ATLASSIAN_API_TOKEN:-}}" && echo "Jira API token set"
```

#### Browser scrape notes

- Use only on sites/accounts the user controls and is signed into.
- Prefer **list/board views** over opening every issue:
  - Assigned to me filter / "My open issues"
  - Active sprint board (or user-named board)
  - Filters the user names (e.g. `priority = Highest`, `duedate <= endOfWeek()`)
- Capture per visible card/row: issue key, summary, status/column, assignee, priority, due date badges, and blocker/flag chips when shown.
- Open an issue only when the card text is insufficient to classify the ask (due reason, last comment @ask, linked blocker).
- Expand recent comments only enough to paraphrase who is waiting and what they need.
- If Atlassian blocks automation (CAPTCHA, consent interstitial, login wall), stop and ask the user to use MCP, API token, or paste the issue keys they care about.

Useful scrape entry URLs (adjust site host / board id):

```text
https://<site>.atlassian.net/jira/your-work
https://<site>.atlassian.net/jira/software/projects/<KEY>/boards/<id>
https://<site>.atlassian.net/issues/?jql=assignee%20=%20currentUser()%20AND%20resolution%20=%20EMPTY%20ORDER%20BY%20priority%20DESC,%20duedate%20ASC
```

#### REST API notes

```bash
BASE="${JIRA_BASE_URL%/}"   # e.g. https://acme.atlassian.net
USER="${JIRA_USER:-${JIRA_EMAIL:-}}"
TOKEN="${JIRA_API_TOKEN:-${ATLASSIAN_API_TOKEN:-}}"

# Identity
curl -s -u "$USER:$TOKEN" "$BASE/rest/api/3/myself"

# My open issues (Cloud API v3 example)
curl -s -u "$USER:$TOKEN" -G "$BASE/rest/api/3/search/jql" \
  --data-urlencode 'jql=assignee = currentUser() AND resolution = EMPTY ORDER BY priority DESC, duedate ASC' \
  --data-urlencode 'maxResults=20' \
  --data-urlencode 'fields=summary,status,priority,duedate,issuetype,updated,comment,issuelinks'
```

On Server/DC, use `/rest/api/2/search` with the same JQL if `/search/jql` is unavailable.

### Blocked access

If neither MCP nor a usable scrape/API path works:

1. Say Jira is unreachable.
2. Ask the user to connect Jira MCP, provide site URL + API token, sign in for browser scrape, or paste the issue keys / board filters they care about.
3. Do **not** fabricate a Jira-backed plan.

Optional: offer a lightweight plan from Slack ([slack-daily-plan](../slack-daily-plan/SKILL.md)), Gmail ([gmail-daily-plan](../gmail-daily-plan/SKILL.md)), or GitHub ([github-issues](../github-issues/SKILL.md)) only if the user agrees — label it as **not Jira-sourced**.

## Workflow Checklist

Copy and track:

```
Jira daily plan:
- [ ] Access verified (MCP, REST API, or browser scrape)
- [ ] Time / sprint window set (default: active sprint + due soon + recently updated assigned)
- [ ] Assigned + due/blocked issues scanned
- [ ] Active sprint board / named filters scanned
- [ ] Recent @mentions / waiting comments scanned
- [ ] Items classified and ranked
- [ ] Plan delivered (ordered list + parking lot + unknowns)
- [ ] Optional: user asked whether to act on P1 (transition / comment / start work)
```

## 1. Scope the time window

Default scope unless the user specifies otherwise:

| Context | Window |
|---------|--------|
| Typical morning plan | **Active sprint** (or current board) + assigned open issues updated/due in last **7 days** / next **2 days** |
| Monday / after time off | Active sprint + anything still assigned/open since they last worked (ask if unclear) |
| User says "today only" | Due today / overdue + In Progress + Blocked |
| User names projects/boards/filters | Those scopes + "assigned to me" still included |

Record the user's timezone and Jira site if known; otherwise state assumptions (e.g. "assuming local morning; site from `JIRA_BASE_URL`").

## 2. Gather Jira signal

Pull in this order (stop expanding when you have enough for a solid plan — usually ≤20 candidate issues):

### 2a. Direct ownership (highest signal)

1. **Assigned to me** and unresolved (especially In Progress / Blocked)
2. **Overdue or due today/tomorrow**
3. **Flagged / impediment** cards and issues with **is blocked by** links still open
4. **Recent comments @-mentioning the user** or "waiting on you" language

Useful JQL patterns (MCP, API, or Issues search box):

```text
assignee = currentUser() AND resolution = EMPTY ORDER BY priority DESC, duedate ASC
assignee = currentUser() AND duedate <= endOfDay("+1d") AND resolution = EMPTY
assignee = currentUser() AND statusCategory != Done AND updated >= -2d
text ~ currentUser() AND updated >= -2d ORDER BY updated DESC
```

Sprint/board: prefer the **active sprint** for the project the user names; otherwise their default board / "Your work".

### 2b. Board and filter scan

Scan:

- Active sprint columns the user cares about (To Do, In Progress, Blocked / Impediment)
- Filters or queues they name (`Team triage`, `Customer bugs`)
- Highest/Highest-priority backlog items assigned to them even if not started

Skip Done/Closed columns and unassigned backlog noise unless mentioned. Sample — do not scrape every epic in the project.

### 2c. What to extract per candidate

For each possible work item, capture:

| Field | Example |
|-------|---------|
| Ask | "Unblock checkout: fix PAY-442 null total" |
| Key | `PAY-442` |
| Where | board "Payments" / sprint 48 / In Progress |
| When | updated today 09:14 / due today |
| Deadline | due date / sprint end / none |
| Blocking? | yes — `PAY-455` waits on this |
| Type | bug / story / task / spike / review |
| Who waits | `@alex` in latest comment |

Ignore pure FYI watches, automated bot chatter without action, resolved/Done issues, and duplicates unless they reopen work.

## 3. Classify and prioritize

Rank every actionable item:

| Priority | Criteria |
|----------|----------|
| **P0 — Do first** | Production/security incident ticket; explicit "ASAP"/"blocked on you"; overdue / due within a few hours; flagged blocker holding a release |
| **P1 — Today** | Clear assignee ownership; due today; sprint commitment In Progress; stakeholder waiting on a review/decision |
| **P2 — Today if capacity** | Soft due dates, unstarted sprint stories, non-blocking reviews |
| **P3 — Later** | Nice-to-have backlog, no due date, watch-only |
| **Drop / ignore** | Done/Closed, not assigned to the user (unless @asked), duplicate of a higher item |

**Tie-breakers** (same priority): issues blocking others → customer/P1-P2 bug impact → sooner due date → oldest In Progress without progress.

**Deduplicate:** same work across Jira + Slack/email → one plan item; if this skill is Jira-only, cite the issue key and note other-channel overlap if known.

**Ambiguity:** if ownership, acceptance criteria, or due date is unclear, put under **Needs clarification** with one suggested clarifying question — do not invent urgency.

## 4. Deliver the plan

Present a **high-level** daily plan. Keep it scannable — no ticket dumps.

```markdown
## Daily plan — <weekday, date> (<timezone assumption>)

**Window scanned:** <sprint / start> → <now>
**Sources:** Jira (<MCP|REST API|browser scrape>), assigned, due/blocked, <board/filter…>

### Priority order

1. **[P0] <outcome-oriented title>**
   - Why now: <due / blocker / incident>
   - From: <KEY> — "<summary>" (<status>; <due/updated>)
   - Next step: <one concrete action>

2. **[P1] …**
3. …

### Needs clarification
- <KEY> — ask: "<one question>"

### Parking lot (not today unless capacity)
- <P2/P3 items, one line each with KEY>

### Intentionally skipped
- <Done columns, unassigned backlog sample, bot comments, etc.>
```

Rules for the write-up:

- Titles are **outcomes** ("Unblock release: fix PAY-442 null total"), not "Check Jira".
- **One next step** per item — the smallest useful action (reproduce, comment, start PR, update AC).
- Cap the main list at **~7**; park the rest.
- If nothing actionable: say so, list what was scanned, and offer optional deep-dives (other board, longer window, or Slack/Gmail).

After delivering, ask whether to:

- Start on **P0/P1** in the codebase
- Draft Jira comments for waiting threads
- Transition status / update estimates (only with explicit approval)
- Re-run with a different board, filter, or combine with [slack-daily-plan](../slack-daily-plan/SKILL.md) / [gmail-daily-plan](../gmail-daily-plan/SKILL.md)

Do not start implementation or mutate issues until the user confirms — unless they already said "plan and then do P0".

## 5. Optional follow-through

| User ask | Action |
|----------|--------|
| Start P0/P1 work | Switch to implementation; use [orchestrate](../orchestrate/SKILL.md) if multi-step |
| Draft comments | Draft text for the user to post; comment only with explicit approval |
| Transition / assign | Change status or assignee only after approval |
| Replan midday | Re-scrape/re-query a shorter window; update the ranked list |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Listing every assigned ticket | Rank 3–7 actionable outcomes |
| Planning with stale/cached board memory | Fresh MCP/API/scrape for the window |
| Marking every sprint story as P0 | Require due, blocker, incident, or explicit ask |
| Transitioning or commenting unprompted | Deliver locally; mutate only on request |
| Hiding uncertainty as fake urgency | Use "Needs clarification" |
| Dumping full private descriptions into public posts | Cite KEY + paraphrase the ask |
| Fighting CAPTCHAs / bypassing Atlassian auth walls | Stop; ask for MCP, API token, or pasted keys |
| Boiling the entire project backlog | Sample assigned + active sprint + named filters |

## Cross-References

- Slack-sourced daily plan: [slack-daily-plan](../slack-daily-plan/SKILL.md)
- Gmail-sourced daily plan: [gmail-daily-plan](../gmail-daily-plan/SKILL.md)
- Multi-step execution after planning: [orchestrate](../orchestrate/SKILL.md)
- Repo issue backlog (non-Jira): [github-issues](../github-issues/SKILL.md)
- Shipping resulting code work: [github-publish](../github-publish/SKILL.md)

## Additional Resources

- Sample scans and plan output: [examples.md](examples.md)
