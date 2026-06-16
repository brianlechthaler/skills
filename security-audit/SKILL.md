---
name: security-audit
description: >-
  Perform an aggressive, leave-no-stone-unturned security audit of a codebase,
  dependencies, configs, infrastructure, and runtime surfaces. Use when the user
  asks for a security audit, vulnerability assessment, penetration-style review,
  threat model, security hardening review, or comprehensive security scan. After
  the audit, prompt whether to auto-fix findings unless the user already asked
  to audit and patch automatically.
---

# Security Audit

Conduct a **thorough, adversarial security audit**. Assume an attacker with repo access, network access, and user-level privileges. Do not stop at the happy path — probe edge cases, misconfigurations, and trust-boundary failures.

This skill audits the **entire attack surface**, not just recent diffs. For diff-only review of pending changes, also use the `review-security` skill.

## Fix Mode (decide first)

| User intent | Behavior after audit |
|-------------|----------------------|
| Default — "security audit", "scan for vulnerabilities", etc. | Deliver findings, then **ask** whether to automatically fix discovered vulnerabilities |
| Explicit auto-patch — "audit and fix", "audit and patch", "auto-fix", "fix automatically", "patch vulnerabilities", "remediate findings" | **Skip the prompt** — fix vulnerabilities immediately after the audit report |

When auto-patching:

1. Fix in severity order: Critical → High → Medium → Low → Informational
2. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) after each fix batch
3. Re-scan affected areas before marking complete
4. Do **not** commit unless the user asks

When prompting (default), use AskQuestion when available:

- **Prompt**: "Automatically fix the vulnerabilities discovered in this audit?"
- **Options**: "Yes — fix all findings" (recommended for Critical/High), "Yes — fix Critical and High only", "No — report only"

If AskQuestion is unavailable, ask conversationally with the same options.

## Audit Workflow

Copy and track progress:

```
Security audit progress:
- [ ] Phase 0: Recon — map stack, entry points, trust boundaries, data classes
- [ ] Phase 1: Secrets and credentials exposure
- [ ] Phase 2: Dependency and supply-chain vulnerabilities
- [ ] Phase 3: Application code — injection, auth, crypto, sessions
- [ ] Phase 4: API, web, and client security
- [ ] Phase 5: Infrastructure, containers, IaC, CI/CD
- [ ] Phase 6: Data protection, logging, and privacy
- [ ] Phase 7: MCP / agentic surfaces (if present)
- [ ] Phase 8: Configuration and deployment hardening
- [ ] Phase 9: Synthesize findings and severity ranking
- [ ] Phase 10: Fix mode — prompt or auto-patch
```

Run phases **in order**. Do not skip phases because "this looks like a simple app." Incomplete audits are failures.

### Phase 0 — Recon

Before hunting bugs, build an attack-surface map:

- Languages, frameworks, package managers, deployment model
- External entry points: HTTP routes, WebSockets, CLIs, webhooks, cron, queues, MCP tools
- Auth model: sessions, JWT, API keys, OAuth, service accounts
- Data classes: PII, credentials, payment data, health data, production secrets
- Trust boundaries: public internet → app → database → third parties

Search the repo for manifests (`package.json`, `go.mod`, `requirements.txt`, `Dockerfile`, `compose.yaml`, `.github/workflows/`, `terraform/`, `k8s/`, etc.) and read them. Identify what is in scope.

### Phases 1–8 — Active hunting

For each phase, **read code and run tools**. Grep, static analysis, dependency scanners, and config review are mandatory — do not rely on memory or assumptions.

Run every scanner the project supports. Examples (use what exists; add minimal tooling only when needed):

| Area | Commands / actions |
|------|-------------------|
| Secrets | `gitleaks detect`, `trufflehog filesystem .`, grep for API keys, private keys, tokens, `.env` committed, hardcoded passwords |
| Dependencies | `npm audit`, `pnpm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `trivy fs .`, Dependabot/GitHub advisory cross-check |
| SAST | `semgrep --config auto`, language linters with security rules, framework-specific scanners |
| Containers | `trivy image`, read `Dockerfile` for root user, secrets in layers, `latest` tags, exposed ports |
| IaC | `checkov`, `tfsec`, `trivy config` on Terraform/CloudFormation/K8s manifests |
| Web headers | If a running app exists, inspect CSP, HSTS, X-Frame-Options, cookie flags |

**Be aggressive.** For every file type in scope:

- Trace user-controlled input to sinks (SQL, shell, HTML, path, SSRF, deserialization)
- Check authorization on every mutating endpoint and admin path — IDOR, missing authz, privilege escalation
- Verify crypto: no MD5/SHA1 for passwords, no hardcoded IVs, proper randomness, TLS verification not disabled
- Review error handling for stack traces, internal paths, and secret leakage
- Check file operations for path traversal, symlink attacks, unsafe uploads
- Review CORS, CSRF, rate limiting, and mass-assignment / over-posting
- Inspect CI/CD for secret exfiltration, unpinned actions, overly broad `permissions:`, deploy keys in logs
- Scan git history for committed secrets even if removed in HEAD

Full per-phase checklists: [checklist.md](checklist.md)

If the repo contains MCP server code, apply [mcp-security](../mcp-security/SKILL.md) as Phase 7 — treat agentic tool surfaces as **high blast radius**.

### Phase 9 — Report

Present findings in a structured audit report. For audits with more than a handful of findings, use the `canvas` skill — security audits with categorized findings are a primary canvas use case.

Every finding MUST include:

| Field | Content |
|-------|---------|
| ID | `SEC-001`, `SEC-002`, … |
| Severity | Critical / High / Medium / Low / Informational |
| Category | e.g. Injection, AuthZ, Secrets, Dependency, Config |
| Location | `path:line` or config key |
| Evidence | What you observed (grep hit, scanner output, code path) |
| Impact | What an attacker achieves |
| Remediation | Concrete fix — not "review this" |

Sort by severity (highest first). Include an executive summary with counts by severity and the top 3 risks.

End the report with:

```
Total: N findings (C critical, H high, M medium, L low, I informational)
```

### Phase 10 — Remediation

**If auto-patch mode** (user requested it): proceed immediately to fixes. No prompt.

**If default mode**: ask whether to auto-fix. On "Yes", fix per the Fix Mode rules above. On "No", stop after the report.

When fixing:

- Prefer minimal, correct patches over broad refactors
- Replace secrets with env vars / secret managers; rotate exposed credentials and tell the user
- Upgrade vulnerable dependencies to patched versions; note breaking changes
- Add tests for security regressions when the project has test infrastructure
- After fixes, re-run relevant scanners and update the finding list (mark fixed / residual risk)

## Severity Guide

| Severity | Criteria |
|----------|----------|
| **Critical** | Remote unauthenticated RCE, auth bypass to admin, exposed production secrets with live access, SQLi with data exfiltration |
| **High** | Authenticated privilege escalation, stored XSS in sensitive context, SSRF to internal services, weak crypto protecting secrets at rest |
| **Medium** | CSRF on state-changing actions, missing rate limits on auth, verbose errors, dependency with known exploit path but mitigated |
| **Low** | Missing security headers, informational dependency CVEs without exploit path, defense-in-depth gaps |
| **Informational** | Best-practice deviations with no direct exploit path |

When uncertain, **round up** — this is an aggressive audit.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Auditing only changed files | Audit full attack surface unless user narrows scope |
| Listing generic OWASP advice without evidence | Cite file, line, scanner output, or reproducible path |
| Skipping dependency scans because "we trust npm" | Run every applicable scanner |
| Fixing without re-scanning | Verify each fix; residual findings stay in the report |
| Committing fixes without being asked | Report and fix in working tree; commit only on request |
| Treating MCP tools as normal API routes | Apply mcp-security skill with full NSA checklist |

## Cross-References

- Diff-focused review: `review-security` skill
- MCP server hardening: [mcp-security](../mcp-security/SKILL.md)
- Rich audit report UI: `canvas` skill
- Tests after fixes: [test](../test/SKILL.md)
- Lint after fixes: [lint](../lint/SKILL.md)
- Container scanning context: [docker](../docker/SKILL.md)

## Additional Resources

- Detailed phase checklists: [checklist.md](checklist.md)
