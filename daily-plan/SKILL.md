---
name: daily-plan
description: >-
  Combine Slack, Gmail, and Jira signals into one ranked high-level plan for
  what to accomplish today. Use when the user asks for a daily plan, morning
  priorities, standup prep, or what to work on next across Slack, email, and/or
  Jira — not when they already named a single source or gave an ordered task
  list.
---

# Daily Plan

Turn **multi-channel work signals into one ranked daily plan**. Gather from the available sources — Slack, Gmail, and Jira — merge and deduplicate, classify urgency, and deliver a short ordered list of what matters most today.

This skill **orchestrates** the channel-specific skills; it does not replace them:

| Source | Detailed gather + access rules |
|--------|--------------------------------|
| Slack | [slack-daily-plan](../slack-daily-plan/SKILL.md) |
| Gmail | [gmail-daily-plan](../gmail-daily-plan/SKILL.md) |
| Jira | [jira-daily-plan](../jira-daily-plan/SKILL.md) |

## Core Rules

1. **Read before planning** — never invent priorities from memory; pull live context from every reachable source first.
2. **Use every available source** — probe Slack, Gmail, and Jira; skip only what is unreachable or explicitly excluded by the user.
3. **One merged plan** — produce a single ranked list (typically 3–7 items), not three separate plans.
4. **Deduplicate across channels** — the same ask in Slack + email + Jira is one plan item with all cites.
5. **Cite sources** — every item must cite channel detail (Slack person/channel, Gmail sender/subject, and/or Jira key).
6. **Do not mutate** — no Slack posts, email sends, or Jira transitions unless the user explicitly asks.
7. **Respect privacy** — paraphrase asks; do not paste private DM/email/comment bodies into public channels, PRs, or shared docs.

## When This Applies

| Use this skill | Skip / use a single-source skill |
|----------------|----------------------------------|
| Morning "what should I do today?" with no single channel named | User says **Slack-only** → [slack-daily-plan](../slack-daily-plan/SKILL.md) |
| Standup / day plan across Slack + email + tickets | User says **Gmail-only** / inbox triage → [gmail-daily-plan](../gmail-daily-plan/SKILL.md) |
| Catch up after time off from multiple tools | User says **Jira-only** / sprint board → [jira-daily-plan](../jira-daily-plan/SKILL.md) |
| "Prioritize my day" / "what's on my plate" | Pure GitHub backlog → [github-issues](../github-issues/SKILL.md) |
| User names two or more of Slack, Gmail, Jira | User already gave an explicit ordered task list |

When unsure and the user mentions priorities / plan / day / standup without locking to one tool, **apply this skill**.

## Prerequisites

For each source, follow that skill’s access path (MCP preferred, then API/token/scrape). Summarize reachability before gathering:

| Source | Prefer | Fallback | If blocked |
|--------|--------|----------|------------|
| Slack | Slack MCP | `SLACK_USER_TOKEN` / `SLACK_BOT_TOKEN` | Note unreachable; continue with others |
| Gmail | Gmail MCP | Google API / IMAP / browser scrape | Note unreachable; continue with others |
| Jira | Jira / Atlassian MCP | REST API / `acli` / browser scrape | Note unreachable; continue with others |

```
Source access:
- [ ] Slack: MCP | token | blocked
- [ ] Gmail: MCP | API/IMAP/scrape | blocked
- [ ] Jira: MCP | REST/scrape | blocked
```

- If **all** sources are blocked: say so, ask the user to connect at least one, and do **not** fabricate a plan.
- If **some** are blocked: plan from reachable sources; label missing channels in the write-up.
- Prefer **read-only** tools on every server. Discover MCP schemas before invoking tools.

## Workflow Checklist

Copy and track:

```
Daily plan (multi-source):
- [ ] Sources in scope confirmed (default: Slack + Gmail + Jira)
- [ ] Access probed per source
- [ ] Time / sprint window set
- [ ] Slack candidates gathered (if available)
- [ ] Gmail candidates gathered (if available)
- [ ] Jira candidates gathered (if available)
- [ ] Cross-source merge + dedupe
- [ ] Items classified and ranked
- [ ] Single plan delivered (ordered list + parking lot + unknowns)
- [ ] Optional: user asked whether to act on P0/P1
```

## 1. Scope sources and time window

**Sources:** default to Slack + Gmail + Jira. Drop a source only if the user excludes it or access is blocked.

**Window** (align each source’s scan to the same day intent):

| Context | Slack / Gmail | Jira |
|---------|---------------|------|
| Typical morning plan | Last **24–36 hours** + unreplied / unread | Active sprint + due soon + recently updated assigned |
| Monday / after time off | Last active business day → now (ask if unclear) | Active sprint + still-open assigned since last work |
| User says "today only" | Since local midnight | Due today / overdue + In Progress + Blocked |
| User names channels/labels/boards | Those filters + DMs/mentions/assigned still included | Same |

Record timezone and which sources will be scanned. State assumptions when unknown.

## 2. Gather per source (in parallel when safe)

Pull candidates from each reachable source using that skill’s gather steps. Cap at roughly **≤20 candidates per source**, then merge.

| Order | Source | Follow |
|-------|--------|--------|
| 2a | Slack | [slack-daily-plan](../slack-daily-plan/SKILL.md) §2 — DMs, mentions, priority channels |
| 2b | Gmail | [gmail-daily-plan](../gmail-daily-plan/SKILL.md) §2 — unread, important/starred, labels |
| 2c | Jira | [jira-daily-plan](../jira-daily-plan/SKILL.md) §2 — assigned, due/blocked, sprint, @mentions |

Prefer running source gathers **concurrently** (parallel readonly subagents or parallel MCP calls) when tools allow and there are no shared mutations — same spirit as [orchestrate](../orchestrate/SKILL.md).

For each candidate, normalize to a common shape:

| Field | Example |
|-------|---------|
| Ask | "Approve the vendor SOW by EOD" |
| Sources | Gmail thread "SOW — Acme"; Slack DM `@alex`; Jira `PROC-12` |
| When | today 09:14 / due today |
| Deadline | EOD / Friday / none |
| Blocking? | yes — procurement waits |
| Type | decision / review / reply / implement / bug / FYI |

Ignore pure FYIs, bots without action, Done/Closed tickets, promotions/newsletters, and resolved threads unless they reopen work.

## 3. Merge, classify, and prioritize

**Deduplicate first:** same underlying work across channels → one item. Keep the strongest title; list every citation under **From**. Prefer Jira key in the title when a ticket exists; otherwise outcome-oriented wording.

Rank every merged actionable item:

| Priority | Criteria |
|----------|----------|
| **P0 — Do first** | Production/security/legal incident; explicit "ASAP"/"blocked on you"; deadline within a few hours; flagged release blocker |
| **P1 — Today** | Clear ownership; deadline today; sprint In Progress; stakeholder waiting on decision/review/reply |
| **P2 — Today if capacity** | Soft deadlines, unstarted sprint work, non-blocking reviews |
| **P3 — Later** | Nice-to-have, no deadline, FYI that might become work |
| **Drop / ignore** | Resolved, spam, not directed at the user, duplicate of a higher item |

**Tie-breakers** (same priority): external people/systems blocked on the user → customer/stakeholder impact → sooner explicit deadline → oldest unreplied ask → multi-channel pressure (same ask in 2+ sources) slightly above single-channel.

**Ambiguity:** ownership or deadline unclear → **Needs clarification** with one suggested question — do not invent urgency.

## 4. Deliver the plan

Present **one** high-level daily plan. Keep it scannable.

```markdown
## Daily plan — <weekday, date> (<timezone assumption>)

**Window scanned:** <start> → <now>
**Sources:** Slack (<status>), Gmail (<status>), Jira (<status>) — <filters/boards…>

### Priority order

1. **[P0] <outcome-oriented title>**
   - Why now: <deadline / blocker / multi-channel pressure>
   - From: <Slack …>; <Gmail …>; <Jira KEY — "summary" (status)>
   - Next step: <one concrete action>

2. **[P1] …**
3. …

### Needs clarification
- <item> — ask: "<one question>"

### Parking lot (not today unless capacity)
- <P2/P3 items, one line each>

### Intentionally skipped
- <noise categories or empty: "N newsletters, M Done tickets, …">

### Source gaps
- <blocked or excluded channels, or "none">
```

Rules for the write-up:

- Titles are **outcomes** ("Unblock vendor: approve Acme SOW"), not "Check Slack/email/Jira".
- **One next step** per item — the smallest useful action.
- Cap the main list at **~7**; park the rest.
- If nothing actionable: say so, list what was scanned per source, and offer single-source deep-dives.

After delivering, ask whether to:

- Start on **P0/P1** in the codebase
- Draft replies/comments for waiting threads (Slack / Gmail / Jira)
- Re-run with a different window, or narrow to one source skill

Do not start implementation or send/mutate anything until the user confirms — unless they already said "plan and then do P0".

## 5. Optional follow-through

| User ask | Action |
|----------|--------|
| Start P0/P1 work | Switch to implementation; use [orchestrate](../orchestrate/SKILL.md) if multi-step |
| Draft replies / comments | Draft for the user; post/send only with explicit approval |
| Narrow to one channel | Hand off to the matching `*-daily-plan` skill for a deeper rescan |
| Replan midday | Re-scan a shorter window across the same sources; update the ranked list |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Three separate plans, one per tool | One merged ranked list |
| Listing every unread/assigned item | Rank 3–7 actionable outcomes |
| Planning from only the first tool that works | Probe all in-scope sources; note gaps |
| Treating Slack ping + Jira ticket as two todos | Deduplicate; cite both |
| Mutating Slack/email/Jira while planning | Deliver locally; mutate only on request |
| Hiding uncertainty as fake urgency | Use "Needs clarification" |
| Dumping private bodies into public posts | Cite + paraphrase |
| Replacing the single-source skills | Keep using them when the user locks to one channel |

## Cross-References

- Slack-only: [slack-daily-plan](../slack-daily-plan/SKILL.md)
- Gmail-only: [gmail-daily-plan](../gmail-daily-plan/SKILL.md)
- Jira-only: [jira-daily-plan](../jira-daily-plan/SKILL.md)
- Multi-step execution after planning: [orchestrate](../orchestrate/SKILL.md)
- Repo issue backlog: [github-issues](../github-issues/SKILL.md)
- Shipping resulting code work: [github-publish](../github-publish/SKILL.md)

## Additional Resources

- Sample multi-source merge and plan output: [examples.md](examples.md)
