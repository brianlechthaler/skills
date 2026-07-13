# Skill Quality — Examples

## Example 1: Single skill review (report only)

**User request:** "Review the quality of the `browser-test` skill."

### Automated validation

```text
browser-test OK
pytest tests/test_skills.py -k browser-test — 4 passed
```

### Summary

| Dimension | Score | Notes |
|-----------|-------|-------|
| Trigger clarity | 4 | Strong description; when-table present |
| Actionability | 3 | Workflow clear but no copy-paste progress block |
| Structure | 4 | Good headings and checklist |
| Completeness | 3 | No anti-patterns table |
| Consistency | 5 | Matches lint/test skill patterns |
| Maintainability | 5 | Links valid |
| **Overall** | **4.0** | |

### Findings

| ID | Priority | Recommendation |
|----|----------|----------------|
| SKQ-001 | Medium | Add anti-patterns table (skip browser for API-only changes, etc.) |
| SKQ-002 | Medium | Add orchestrate-style progress checklist at start of workflow |
| SKQ-003 | Low | Move long Playwright snippet to `examples.md` if section grows |

**Agent response (default mode):** Deliver report, then ask: "Implement the recommended skill improvements?" with Yes all / Yes Critical+High / No.

---

## Example 2: Validation failure (Critical)

**User request:** "Why won't `my-skill` install?"

### Automated validation

```text
my-skill errors:
  - name 'my_skill' does not match directory 'my-skill'
  - broken cross-skill link: '../missing/SKILL.md'
```

### Findings

| ID | Priority | Dimension | Recommendation |
|----|----------|-----------|----------------|
| SKQ-001 | Critical | Consistency | Set `name: my-skill` in frontmatter |
| SKQ-002 | Critical | Maintainability | Fix link to `../lint/SKILL.md` or remove |

**Implement mode:** Fix frontmatter and links, re-run `skill_validate.validate_skill('my-skill', root)`.

---

## Example 3: New skill in this repository

**User request:** "Add a skill-quality analyzer and make sure it passes CI."

### Phase 7 checklist (implemented)

1. Create `skill-quality/SKILL.md`, `rubric.md`, `examples.md`
2. Add `skill-quality` to `skill_categories.py` under Testing & Quality
3. Add README table row
4. Run `pytest tests/test_skills.py` and `python scripts/sync_readme_skill_count.py`

### Closing summary after implement

```markdown
## Implemented
- SKQ-001: Added skill-quality skill with full workflow
- SKQ-002: Registered in categories and README

Re-validation: all tests passed
Overall score (self-review): 4.2
```

---

## Example 4: Batch audit (multiple skills)

**User request:** "Score all Context & Efficiency skills."

### Summary table

| Skill | Overall | Top issue |
|-------|---------|-----------|
| terse | 4.3 | Minor — add one anti-pattern row |
| prompt-conciseness | 4.8 | Exemplar |
| simple-code | 3.9 | Medium — strengthen when-not-applies |
| toonify | 3.5 | High — description triggers too narrow |

**Delivery:** One report section per skill, sorted by score ascending. Ask once whether to implement across all skills or only those below 4.0.

---

## Example 5: Efficiency pass without amputation

**User request:** "Shorten the docker skill but keep every gate."

1. Tag critical requirements (container-only builds, credential mounts, etc.)
2. Apply [prompt-conciseness](../prompt-conciseness/SKILL.md) techniques
3. Parity-check each critical item
4. Re-run skill validation and re-score Efficiency dimension

**Finding example:**

| ID | Priority | Recommendation |
|----|----------|----------------|
| SKQ-010 | Medium | Merge three duplicate "never install on host" paragraphs into one bullet under Core Rules |
| SKQ-011 | Low | Replace 20-line prose example with link to `examples.md` |

Do **not** file Low priority items that remove safety gates.
