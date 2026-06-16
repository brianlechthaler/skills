# Orchestrate — Examples

## Example 1: Add authentication to an API

**User request:** "Add JWT auth to the REST API with login, middleware, and tests."

### Execution plan

**Goal:** Users can log in and protected routes require a valid JWT.

### Phase 1 — Discovery (parallel: yes)

| Task | Agent | Writes |
|------|-------|--------|
| Map existing routes and middleware | explore | — |
| Find test patterns and fixtures | explore | — |
| Check for existing auth utilities | explore | — |

### Phase 2 — Design (parallel: no)

| Task | Agent | Depends on |
|------|-------|------------|
| Parent: choose token shape, middleware hook point, file layout | — | Phase 1 |

### Phase 3 — Implement (parallel: yes)

| Task | Agent | Writes |
|------|-------|--------|
| Auth service + token helpers | generalPurpose | `src/auth/jwt.ts` |
| Login route handler | generalPurpose | `src/routes/auth.ts` |
| Middleware | generalPurpose | `src/middleware/requireAuth.ts` |

Parent integrates imports and registers middleware after all three complete.

### Phase 4 — Verify (parallel: yes)

| Task | Agent | Writes |
|------|-------|--------|
| Unit tests for jwt helpers | generalPurpose | `tests/auth/jwt.test.ts` |
| Integration tests for login + protected route | generalPurpose | `tests/auth/login.test.ts` |

### Phase 5 — Final gate (parallel: no)

Parent runs full test suite and lint.

---

## Example 2: Fix CI and a unrelated lint issue

**User request:** "CI is failing on the PR; also fix eslint in the frontend package."

These are **independent write surfaces** but CI diagnosis should inform whether lint fixes are related.

### Phase 1 — Diagnose (parallel: yes)

| Task | Agent |
|------|-------|
| Summarize failing PR check | ci-investigator |
| List eslint errors in frontend | shell or explore |

### Phase 2 — Fix (parallel: yes only if failures are unrelated)

If CI failed due to frontend lint → **serialize** (one owner for frontend).

If CI failed on backend tests and lint is frontend-only → parallel:

| Task | Agent | Writes |
|------|-------|--------|
| Fix backend test failure | generalPurpose | backend files only |
| Fix frontend eslint | generalPurpose | frontend files only |

---

## Example 3: Security audit then remediate

**User request:** "Run a security audit and fix critical issues."

### Phase 1 — Audit probes (parallel: yes, readonly)

| Task | Agent |
|------|-------|
| Dependency CVE scan | security-review or shell |
| Auth/session review | security-review |
| MCP/server surface review | security-review |

### Phase 2 — Consolidate (parallel: no)

Parent ranks findings; user confirms auto-fix scope if needed.

### Phase 3 — Remediate (parallel: yes by area)

| Task | Agent | Writes |
|------|-------|--------|
| Patch auth issues | generalPurpose | `src/auth/**` only |
| Patch dependency upgrades | shell | `package.json`, lockfile |
| Harden MCP config | generalPurpose | `mcp/**` only |

Never parallelize two remediation tasks on the same package lockfile.

---

## Example 4: When NOT to orchestrate

**User request:** "Rename `getUser` to `fetchUser` in one file."

Single pass, no subagents, no phased plan — overhead exceeds benefit.
