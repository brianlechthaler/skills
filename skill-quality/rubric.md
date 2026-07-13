# Skill Quality — Rubric

Score each dimension **1–5**. Use evidence from `SKILL.md`, supporting files, and validation output.

| Score | Meaning |
|-------|---------|
| **5** | Exemplar — could be used as a template for new skills |
| **4** | Strong — minor polish only |
| **3** | Adequate — works but has clear improvement opportunities |
| **2** | Weak — agent may misapply or stall |
| **1** | Broken or misleading — fix before relying on the skill |

---

## 1. Trigger clarity

**What to check**

- [ ] YAML `description` is ≥ 20 characters and names concrete triggers ("Use when …")
- [ ] Opening paragraphs state purpose in one or two sentences
- [ ] "When This Applies" (or equivalent) table lists **applies** and **does not apply**
- [ ] Default behavior when unsure is explicit ("default to applying" or "skip unless …")
- [ ] Description keywords match user phrases (audit, fix, optimize, commit, etc.)

**Red flags**

- Description only restates the skill name
- No negative scope — skill fires on every task
- Triggers buried after long prose

---

## 2. Actionability

**What to check**

- [ ] Numbered workflow or phased steps
- [ ] Copy-paste progress checklist the agent can tick through
- [ ] Concrete commands, file paths, or tool names where relevant
- [ ] Clear stopping conditions ("do not commit unless user asks")
- [ ] Implement / fix mode decided up front when skill offers optional remediation

**Red flags**

- Only high-level principles, no steps
- "Be thorough" without how
- Missing decision tree for report-only vs implement

---

## 3. Structure

**What to check**

- [ ] Single `#` title matching skill purpose
- [ ] Sections use `##` / `###` consistently
- [ ] Tables for comparisons (when/when-not, severity, anti-patterns)
- [ ] Fenced blocks for checklists and commands (easy to copy)
- [ ] Body ≥ 100 characters with real content (automated gate)

**Red flags**

- Wall of prose without headings
- Critical rules only in footnotes
- No anti-patterns section for workflow-heavy skills

---

## 4. Completeness

**What to check**

- [ ] Core rules or non-negotiables stated early
- [ ] Boundaries and out-of-scope explicit
- [ ] Cross-references to related skills (`../other-skill/SKILL.md`)
- [ ] Additional resources (`examples.md`, `checklist.md`) linked when content is long
- [ ] Severity or priority guide when findings/recommendations are ranked

**Red flags**

- No cross-refs where overlap exists (duplicate conflicting guidance)
- Long inline examples that belong in `examples.md`
- Audit-style skill with no report field template

---

## 5. Consistency

**What to check**

- [ ] `name` in frontmatter matches directory name
- [ ] Link style matches repo (`../skill/SKILL.md` for cross-skill)
- [ ] Tone matches peer skills (imperative, scannable, no fluff)
- [ ] Implement-mode pattern aligned with similar skills (audit, performance, security)
- [ ] **This repo:** listed once in `skill_categories.py` and `README.md`

**Red flags**

- Different section order than every other skill with no reason
- Broken or non-standard cross-skill links
- Skill missing from README or categorized twice

---

## 6. Maintainability

**What to check**

- [ ] Links resolve (automated check ignores code literals)
- [ ] Examples reference current tooling, not deprecated commands
- [ ] No hard-coded skill counts or lists that drift (prefer `install.py --list`)
- [ ] Optional files documented in "Additional Resources"

**Red flags**

- Links to removed skills or paths
- Validation errors ignored in prose ("TODO fix links")
- Entire runbooks duplicated from another skill

---

## 7. Efficiency (optional dimension)

Score only when token budget matters or skill is unusually long.

- [ ] No duplicate rules in prose and tables
- [ ] One canonical statement per rule
- [ ] Examples deferred to `examples.md`
- [ ] Critical policies intact after any compression pass

---

## Automated validation mapping

| Validation error | Default priority | Typical dimension |
|------------------|------------------|-------------------|
| Missing frontmatter / name mismatch | Critical | Consistency |
| Description too short | Critical | Trigger clarity |
| Body too short / no heading | Critical | Structure |
| Broken link | Critical | Maintainability |
| Rule conversion empty/failed | Critical | Structure |
| README / category missing (this repo) | Critical | Consistency |

---

## Overall score

**Overall** = average of dimensions 1–6 (include 7 only if scored).

| Overall | Interpretation |
|---------|----------------|
| ≥ 4.5 | Exemplar — ship as-is or minor polish |
| 3.5 – 4.4 | Good — address High findings |
| 2.5 – 3.4 | Needs work — plan structured rewrite |
| < 2.5 | Not production-ready — fix Critical/High first |
