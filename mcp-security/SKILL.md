---
name: mcp-security
description: >-
  Implement and harden MCP (Model Context Protocol) servers using NSA AISC
  security design considerations (CSI PP-26-1834). Use when creating, modifying,
  reviewing, or deploying MCP servers, tools, gateways, or agent integrations;
  when the user mentions MCP security, NSA MCP guidance, or production MCP
  hardening.
---

# MCP Security (NSA CSI PP-26-1834)

Apply the NSA Artificial Intelligence Security Center guidance — **"Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation"** (U/OO/6030316-26, PP-26-1834, v1.0, May 2026) — to every MCP server implementation in this project.

Source: [NSA CSI MCP Security PDF](https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf)

Treat MCP as a **high-risk agentic environment**, not a simple RPC layer. Security must be designed in; the protocol leaves many controls to implementers.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New or changed MCP server code | Consuming MCP as a client-only integration with no server code |
| Tool/resource/prompt handlers | Documentation that merely mentions MCP |
| MCP gateway or proxy in the repo | Unrelated backend APIs with no MCP surface |
| Deployment/config for MCP servers | General app security with no MCP component |

When unsure and the repo contains MCP server code, **default to applying this skill**.

## Four Architectural Commitments

NSA guidance compresses to four operational principles. Every MCP design must address all four:

1. **Gateway trust boundary** — agents reach external MCP servers through a single inspection point (DLP, rate limits, injection scanning), not direct ad-hoc connections.
2. **Least privilege at the tool-call boundary** — each invocation gets minimum scope; no ambient session authority.
3. **Tamper-evident audit** — structured, SIEM-ready records of every agent action (tool calls, results, policy decisions), not free-text app logs.
4. **Cryptographic message integrity** — sign and verify MCP messages at the protocol layer (TLS alone is insufficient).

## Implementation Workflow

Copy and track:

```
MCP security progress:
- [ ] Threat model documented (trust boundaries, data classes, tool blast radius)
- [ ] Gateway/proxy path defined (no direct agent → arbitrary server)
- [ ] Tool handlers enforce least privilege per call
- [ ] Input validation + output inspection before returning to agent
- [ ] Structured audit events emitted (tool, params hash, identity, result metadata)
- [ ] Tool definitions versioned/pinned; drift detectable
- [ ] Server runs in OS-level sandbox (container + seccomp/namespace or equivalent)
- [ ] AuthN/AuthZ at server and per-tool level; fail closed
- [ ] Message-signing hooks or verification stubs (even if ecosystem gap remains)
- [ ] Discovery/inventory documented for operators
```

### Step 1 — Map trust boundaries

Before writing handlers, document:

- Who connects (host agent, gateway, human operator)
- What data classes tools touch (PII, secrets, production systems)
- What each tool can do if fully compromised (blast radius)

Design so a compromised tool cannot exceed its declared capability. Assume **indirect prompt injection** in all tool inputs and outputs.

### Step 2 — Design for gateway placement

Requirements 1–3 assume a **filtering proxy** between agents and MCP servers. Server-side responsibilities:

- Accept traffic only from the gateway (mTLS, network policy, or localhost bind)
- Expose stable tool schemas for inventory pinning
- Return outputs the gateway can scan (no opaque blobs when avoidable)
- Support rate-limit-friendly idempotency where applicable

Do not assume agents connect directly in production.

### Step 3 — Harden tool handlers

Every tool implementation MUST:

- **Validate inputs** against a strict JSON Schema; reject unknown fields
- **Scope permissions per call** — derive authorization from the invocation context, not a long-lived super-token
- **Sanitize outputs** — strip secrets, redact PII in logs, cap response size
- **Fail closed** — on validation, auth, or policy errors, deny; never silently degrade to broader access
- **Avoid tool-chain pivots** — do not return instructions, markup, or URLs that steer the agent to other tools unless explicitly intended

```typescript
// Pattern: per-call scope, fail closed
async function handleTool(args: unknown, ctx: InvocationContext) {
  const parsed = ToolSchema.safeParse(args);
  if (!parsed.success) throw new McpError(InvalidParams, "invalid arguments");

  if (!ctx.authorizer.may(ctx.caller, "tool:read-records", parsed.data.scope))
    throw new McpError(PermissionDenied, "insufficient scope for this call");

  const result = await executeWithTimeout(parsed.data, { timeoutMs: ctx.limits.timeout });
  return sanitizeForAgent(result);
}
```

### Step 4 — Structured audit logging

Emit **one structured event per tool invocation** before returning to the caller:

| Field | Purpose |
|-------|---------|
| `timestamp` | ISO-8601 UTC |
| `event_type` | e.g. `mcp.tool.invoke`, `mcp.tool.result` |
| `tool_name` | Registered tool identifier |
| `caller_identity` | Agent/user/service principal |
| `authorization_scope` | Scope granted for this call only |
| `params_fingerprint` | Hash of parameters (not raw secrets) |
| `result_status` | success / denied / error |
| `result_bytes` | Size; hash or redacted sample — log full output only when policy allows |
| `session_id` / `correlation_id` | Trace across gateway and server |

Logs MUST be machine-parseable (JSON lines) and suitable for SIEM ingestion. Prefer signed or hash-chained entries when infrastructure supports it.

### Step 5 — Tool inventory pinning

Prevent rug-pull / definition-drift attacks:

- Version tool definitions (`tool_name@1` or explicit `version` in descriptor)
- Fingerprint each tool's name + description + parameter schema
- Reject or flag runtime schema changes without operator approval
- Document tools in server metadata; keep definitions stable across releases unless intentionally bumped

### Step 6 — OS-level sandboxing

Run each MCP server in **per-server isolation**, not shared session context:

- Container per server (preferred) or equivalent VM/isolation
- Drop Linux capabilities; use **seccomp**, **network namespaces**, and **Landlock** (or platform equivalent) where available
- Deny network egress except explicitly allowlisted endpoints
- Read-only filesystem except required temp paths
- Non-root user inside container
- Resource limits (CPU, memory, file descriptors, subprocess count)

Follow [docker](../docker/SKILL.md) for containerized builds and tests when applicable.

### Step 7 — Message integrity (protocol layer)

TLS protects the channel, not message content at intermediaries. Plan for:

- Signing outbound server messages and verifying inbound client/gateway messages
- Expiration timestamps, nonces, and replay protection on signed messages
- Document key distribution and rotation

**Ecosystem note:** Per-message MCP signing is not yet universal. Implement verification hooks, document the gap, and do not treat TLS alone as sufficient for high-assurance deployments.

### Step 8 — Local discovery and operations

Operators must know what MCP endpoints exist:

- Bind to explicit interfaces (not `0.0.0.0` unless required and firewalled)
- Document ports, transport (stdio vs HTTP/SSE), and auth requirements in deployment docs
- Support inventory scans or health endpoints that list active tool registrations

## Nine NSA Requirements Checklist

Use during design review and before merge:

| # | Requirement | Server implementer actions |
|---|-------------|---------------------------|
| 1 | Filtering proxy with DLP | Require gateway; no direct production agent access |
| 2 | Content controls | Schema validation, size caps, rate-limit-friendly handlers |
| 3 | Indirect prompt-injection detection | Sanitize tool output; avoid executable instructions in responses |
| 4 | Output logging | Log tool output (or hash/redacted form) before agent handoff |
| 5 | Tool inventory pinning | Versioned, fingerprinted tool definitions |
| 6 | SIEM-ready audit | Structured JSONL events with correlation IDs |
| 7 | OS sandboxing | Container + seccomp/namespace; least-privilege process |
| 8 | Per-message signing | Sign/verify hooks; replay protection design |
| 9 | Local MCP discovery | Documented bind addresses; inventory/health surface |

Detailed mapping and threat context: [reference.md](reference.md)

## Code Review Gates

Before marking MCP server work complete:

- [ ] No secrets in tool responses, logs, or error messages
- [ ] No ambient authority — permissions checked per invocation
- [ ] All tools have JSON Schema validation and documented scope
- [ ] Audit events cover allow, deny, and error paths
- [ ] Server fails closed on auth/validation/policy errors
- [ ] Sandbox/network policy documented in deployment config
- [ ] Threat model updated if new tools touch sensitive data or external systems

For security-focused diff review, also use the `review-security` skill when available, or [security-audit](../security-audit/SKILL.md) for full-surface audits.

## Execution Order

```
1. Threat model + trust boundaries
2. Tool schemas + least-privilege auth design
3. Handler implementation with validation and sanitization
4. Structured audit logging
5. Sandbox/container deployment config
6. Gateway integration assumptions documented
7. Tests for auth denial, schema rejection, output redaction
8. Lint / test skills → then commit
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Long-lived admin token for all tool calls | Per-call scoped credentials |
| Trusting TLS alone for integrity | Plan protocol-layer signing |
| Returning raw DB/API dumps to the agent | Schema-bound, redacted responses |
| Silent fallback on auth failure | Fail closed with audit event |
| Mutable tool definitions without versioning | Pin and fingerprint tools |
| Shared process for multiple MCP servers | One sandboxed server instance per service |
| Logging only "tool called" | Log identity, scope, params fingerprint, result metadata |

## Additional Resources

- Full NSA requirement breakdown: [reference.md](reference.md)
- Implementation patterns by transport and language: [examples.md](examples.md)
