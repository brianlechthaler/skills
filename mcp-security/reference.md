# NSA MCP Security Reference (PP-26-1834)

Reference for [mcp-security/SKILL.md](SKILL.md). Based on NSA AISC Cybersecurity Information Sheet **"Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation"** (U/OO/6030316-26, PP-26-1834, Version 1.0, May 2026).

Official source: https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf

## Why MCP Security Differs

Traditional controls (authentication, authorization, input validation) are necessary but insufficient. Agentic MCP systems introduce:

- **Dynamic tool invocation** at machine speed
- **Implicit trust** between host, agent, gateway, and servers
- **Shared context** across tools and sessions
- **Serialization risks** in JSON-RPC message flows
- **Agent misuse** via prompt injection and tool-chain pivots

Securing MCP requires treating the **agentic environment as a continuum** — misalignment at any layer compounds into exploitable conditions.

## Four Operational Principles

| Principle | What NSA requires | Implementation signal |
|-----------|-------------------|----------------------|
| Cryptographic message integrity | Sign and verify every MCP message at the protocol layer | HMAC or asymmetric signatures on JSON-RPC payloads; nonces; expiration |
| Least privilege at tool-call boundary | Minimum permissions per invocation; no ambient authority | Scoped tokens; per-tool ACLs; deny by default |
| Tamper-evident audit | Provable trail of every agent action | Structured events; hash chains or signed receipts; SIEM integration |
| Trust chains | End-to-end trust; gateway is a trust boundary | mTLS; cert pinning; gateway verifies servers; clients verify gateway |

## Nine Requirements (Detailed)

### Group A — Filtering (boundary control)

**1. Filtering outgoing proxy with DLP and content inspection**

Place a single chokepoint between agents and external MCP servers. The proxy inspects outbound and inbound MCP traffic and applies data-loss-prevention rules.

Server implications:
- Accept connections only from the gateway in production
- Design tools so responses are inspectable (structured JSON, size limits)
- Never assume the agent is the only consumer of your output — the gateway is

**2. Content controls**

Concrete proxy controls NSA expects:
- URL-length caps
- Injection-pattern detection
- Rate limiting
- Tool-level allow/deny policy

Server implications:
- Enforce input size limits in handlers (defense in depth)
- Reject malformed or oversized payloads before execution
- Make tools idempotent where rate limits may trigger retries

**3. Indirect prompt-injection detection**

Scan **tool output**, not just input, for instructions that hijack the consuming agent (tool-chain pivots).

Server implications:
- Do not embed "next step" instructions, hidden markdown, or HTML in tool results unless explicitly part of the contract
- Sanitize external data before returning it to the agent
- Flag or strip content that resembles system prompts or tool-invocation syntax

### Group B — Logging (forensics)

**4. Output logging**

Log MCP tool output **before** it is passed onward to the agent. Preserve the exact bytes returned (or a policy-approved hash/redaction).

Server implications:
- Emit `mcp.tool.result` audit events with result hash or redacted payload
- Separate audit log from debug log; protect audit sink from tampering

**5. Tool inventory pinning**

Detect tool-name collision and definition drift. Fingerprint registered tools; detect changes to previously approved definitions (rug-pull attacks).

Server implications:
- Stable tool names across minor releases
- Explicit version bumps when schema or semantics change
- Expose fingerprints in server metadata or health endpoint

**6. Detailed audit logging feeding SIEM**

Structured logs and event emission for security monitoring. Goal: **signed action receipts** for tamper-evident records.

Server implications:
- JSONL or equivalent structured format
- Standard field names for SIEM parsers
- Correlation IDs shared with gateway
- Webhook/syslog forwarding hooks where appropriate

### Group C — Isolation (containment)

**7. Sandboxing via OS-level containment**

NSA names Linux primitives: **Landlock**, **seccomp**, **network namespaces**, and per-tool execution constraints. Each MCP server's execution should be boxed to prevent lateral movement.

Server implications:
- One container/isolation unit per MCP server service
- Non-root, read-only root FS, dropped capabilities
- Egress allowlists only
- Per-tool subprocess limits and timeouts

### Group D — Integrity (trust)

**8. Per-message signing**

Cryptographic signatures on MCP messages with expiration timestamps, nonces, and replay protection. **TLS is not sufficient** — integrity must exist at the message layer.

Server implications:
- Verify inbound message signatures before processing
- Sign outbound responses
- Document key management and rotation
- Acknowledge ecosystem maturity gap; implement hooks even if full stack signing is pending

**9. Local MCP discovery scanning**

Ability to identify open local MCP listeners — you cannot secure endpoints you do not know exist.

Server implications:
- Bind explicitly; document ports and transports
- Provide health/inventory endpoint for operators
- Avoid accidental exposure on public interfaces

## Threat Scenarios to Design Against

| Scenario | Mitigation |
|----------|------------|
| Prompt injection via document/API content | Output sanitization; gateway scanning; least-privilege tools |
| Tool definition rug-pull (MCPoison-class) | Inventory pinning; versioned definitions; drift alerts |
| Message tampering at gateway | Per-message signing; signature verification |
| Compromised tool handler | OS sandbox; network egress limits; no ambient credentials |
| Over-privileged agent session | Per-call authorization scoping |
| Audit log tampering post-incident | Signed/hash-chained audit entries |
| Malicious gateway substitution | Trust chains; mTLS; cert pinning |

## Compliance Context

NSA CSI is advisory but influential for federal contractors and high-assurance environments. Related 2026 frameworks (DORA, EU AI Act transparency/logging) converge on the same operational shape: **gateway + structured audit + isolation + provable integrity**.

Federal contractor compliance expectation cited in analyses: **September 30, 2026** for demonstrating alignment with these controls.

## Ecosystem Gaps (Honest Assessment)

As of the CSI publication:

- **Per-message MCP signing** — recommended but not widely implemented in all stacks; treat as roadmap requirement
- **MCP-aware security proxies** — "limited and still maturing" (NSA acknowledgment)
- **Signed action receipts** — partially available in some gateways; not universal

Implement what is feasible now; document gaps explicitly rather than implying TLS or basic auth alone satisfies the CSI.
