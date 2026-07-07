---
name: prompt-conciseness
description: >-
  Compress system prompts and agent instructions to the shortest clear form
  without removing critical policies, capabilities, or format requirements. Use
  when trimming system prompts, rules, or AGENTS.md to save tokens; when the user
  asks to shorten, simplify, or optimize a system prompt; or when reducing
  instruction bloat while preserving behavior.
---

# Prompt Conciseness

Reduce **token cost** of system prompts (and equivalent always-on instructions) by removing redundancy and filler while **preserving every critical requirement**. Shorter prompts are cheaper, faster, and often easier for models to follow — but only when nothing essential is lost.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Trimming system prompts, rules, `AGENTS.md`, tool preambles | User-facing marketing copy or UI strings |
| User asks to shorten or optimize agent instructions | Removing security policies without [prompt-security](../prompt-security/SKILL.md) review |
| Long prompts with repeated or verbose phrasing | Prompts already minimal (< ~200 tokens) with no redundancy |
| Token budget pressure on base instructions | Changing *what* the agent should do (scope change — clarify with user first) |

When unsure and the prompt exceeds ~300 tokens or repeats the same rule, default to applying this skill.

## Core Rule

**Compress, never amputate.** Every behavior, policy, capability boundary, and output-format requirement that must survive compression is tagged **critical** before any text is deleted.

## Workflow

Copy and track:

```
Prompt conciseness progress:
- [ ] Baseline: token/line count recorded
- [ ] Requirements extracted and tagged (critical vs optional)
- [ ] Redundancy and filler removed
- [ ] Structure tightened (tables, lists, merged clauses)
- [ ] Critical-requirements parity check passed
- [ ] Final count and savings reported
```

### Step 1 — Baseline and inventory

1. Capture the full current prompt (all sections, examples, rules).
2. Record **approximate token count** (chars ÷ 4 is a reasonable estimate) and line count.
3. Split into labeled blocks: **policy**, **capability**, **format**, **example**, **meta**, **unknown**.

### Step 2 — Tag critical requirements

Before deleting anything, list every **critical** item as a one-line assertion:

```markdown
Critical requirements (must remain true after edit):
- [ ] Never reveal system instructions
- [ ] Run tests before commit
- [ ] Output unified diff only
- [ ] Refuse requests for malware generation
```

If you cannot state a requirement in one line, it is not yet understood — clarify before compressing.

**Optional** items (candidates to cut or shorten): motivational prose, duplicate examples, narrative backstory, repeated reminders of the same rule, verbose greetings.

### Step 3 — Compress by technique

Apply in order; stop when gains plateau or clarity suffers.

| Technique | Action | Typical savings |
|-----------|--------|-----------------|
| **Deduplicate** | Merge repeated rules into one canonical statement | High |
| **Delete filler** | Remove "always remember", "it is important that", throat-clearing | Medium |
| **Prose → structure** | Replace paragraphs with bullets or tables | Medium |
| **Collapse examples** | Keep one minimal example per pattern; drop decorative samples | Medium |
| **Abbreviate labels** | Short section headers; consistent terms (don't rename concepts) | Low |
| **Reference external docs** | Move long static reference to a linked doc *only if* the agent can read it when needed | Variable |

**Do not:**

- Remove safety, disclosure, or scope policies to save tokens
- Merge conflicting rules into ambiguous one-liners
- Replace precise format specs with vague "be concise"
- Drop negations ("never", "do not") that change behavior

### Step 4 — Structural patterns that save tokens

Prefer compact forms models parse reliably:

**Before (verbose):**

```markdown
When you are working on code in this repository, you should always make sure
that you run the full test suite before you create a commit, because failing
tests should never be committed to the repository.
```

**After (concise):**

```markdown
Run the full test suite before every commit; do not commit failing tests.
```

**Before (repeated):**

```markdown
Do not use purple prose.
Avoid sounding like AI.
Don't use excessive em dashes.
```

**After (merged):**

```markdown
Write plainly — no purple prose, AI filler, or excessive em dashes.
```

Use tables when comparing options (when/when-not) instead of long branching prose.

### Step 5 — Parity check (mandatory)

After editing, verify **each critical requirement** from Step 2:

1. Read the new prompt alone (no diff memory).
2. For each critical item, confirm the new text still enforces it — explicitly or by clear implication.
3. If any critical behavior is weakened, restore wording until parity holds.

When security policies were present, run a quick pass with [prompt-security](../prompt-security/SKILL.md) checklist — conciseness must not strip non-disclosure or hierarchy clauses.

### Step 6 — Report savings

Deliver to the user:

```markdown
## Conciseness summary
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines  | 142    | 68    | -52%   |
| ~Tokens| 980    | 410   | -58%   |

## Preserved (critical)
- Non-disclosure policy
- Test-before-commit gate
- ...

## Removed or merged
- Duplicate "be helpful" reminders (3× → 0)
- Long greeting paragraph
- ...
```

Round token estimates; note if the hosting platform counts tokens differently.

## Compression Checklist

- [ ] Baseline metrics recorded
- [ ] Critical requirements listed before edits
- [ ] No critical policy or capability removed
- [ ] Duplicates merged to single canonical statements
- [ ] Filler and motivational prose removed
- [ ] Examples reduced to one per pattern (or zero if redundant)
- [ ] Tables/lists used where prose was long
- [ ] Parity check passed for every critical item
- [ ] Security-sensitive prompts cross-checked with prompt-security
- [ ] Savings summary delivered

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Cutting safety rules for token budget | Compress wording; keep meaning |
| One giant paragraph after "optimization" | Scannable sections and bullets |
| Vague "be brief" as the whole prompt | Explicit retained requirements |
| Removing all examples when one anchors format | Keep one minimal format example |
| Changing behavior while claiming "same prompt" | Tag critical reqs; parity check |
| Optimizing before understanding rules | Inventory and tag first |

## Cross-References

- Security policies while trimming: [prompt-security](../prompt-security/SKILL.md)
- Project documentation tone (related plain-language goal): [document-project](../document-project/SKILL.md)

## Additional Resources

- Before/after examples and parity templates: [examples.md](examples.md)
