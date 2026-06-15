# MCP Security Examples

Patterns referenced from [SKILL.md](SKILL.md). Adapt to your language and MCP SDK.

## Structured Audit Event

```json
{
  "timestamp": "2026-06-15T14:32:01.123Z",
  "event_type": "mcp.tool.result",
  "correlation_id": "req-8f3a2b1c",
  "session_id": "sess-0042",
  "server_id": "acme-records-mcp",
  "tool_name": "search_records",
  "tool_version": "1.2.0",
  "caller_identity": "agent:cursor-host/user:alice",
  "authorization_scope": "records:read:team-alpha",
  "params_fingerprint": "sha256:ab12…",
  "result_status": "success",
  "result_bytes": 2048,
  "result_hash": "sha256:cd34…",
  "duration_ms": 87
}
```

Emit on allow, deny, and error. Never log raw secrets or full PII unless policy explicitly requires it.

## Tool Definition Pinning

```typescript
export const searchRecordsTool = {
  name: "search_records",
  version: "1.2.0",
  description: "Search customer records by team scope.",
  inputSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      query: { type: "string", maxLength: 256 },
      scope: { type: "string", enum: ["team-alpha", "team-beta"] },
    },
    required: ["query", "scope"],
  },
} as const;

export function toolFingerprint(tool: typeof searchRecordsTool): string {
  return sha256(JSON.stringify({
    name: tool.name,
    version: tool.version,
    description: tool.description,
    inputSchema: tool.inputSchema,
  }));
}
```

Bump `version` when schema or semantics change. Expose fingerprints via `/health` or MCP server metadata.

## Output Sanitization

```python
MAX_TOOL_RESPONSE_BYTES = 64 * 1024
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),          # AWS key prefix
    re.compile(r"-----BEGIN [A-Z ]+ KEY-----"),
]

def sanitize_for_agent(data: dict) -> dict:
    text = json.dumps(data)
    if len(text) > MAX_TOOL_RESPONSE_BYTES:
        raise ToolError("response exceeds size limit")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ToolError("response contains forbidden material")
    # Strip fields that could steer agent behavior unexpectedly
    data.pop("_internal_instructions", None)
    return data
```

## Docker Sandbox (per-server isolation)

```yaml
# compose.yaml excerpt — one service per MCP server
services:
  mcp-records:
    build: ./servers/records
    read_only: true
    user: "65534:65534"
    cap_drop: [ALL]
    security_opt:
      - no-new-privileges:true
      - seccomp:./seccomp-mcp.json
    networks: [mcp-internal]
    tmpfs:
      - /tmp:size=64m,noexec
    environment:
      MCP_BIND: "0.0.0.0:8080"
      MCP_ALLOWED_CALLERS: "gateway.internal"
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
```

Gateway sits on the edge network; MCP servers on an internal network with no public ingress.

## seccomp Profile Sketch

Restrict syscalls to those required by your runtime. Example approach:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    { "names": ["read", "write", "exit", "exit_group", "futex", "clock_gettime"], "action": "SCMP_ACT_ALLOW" },
    { "names": ["connect"], "action": "SCMP_ACT_ALLOW", "comment": "only if egress needed — prefer gateway-side calls" }
  ]
}
```

Prefer keeping secrets and upstream API calls in a separate sidecar or gateway so the MCP server process needs minimal syscalls and no outbound network.

## Per-Call Authorization

```typescript
interface InvocationContext {
  caller: string;
  scopes: string[];       // granted for THIS call only
  limits: { timeoutMs: number; maxRows: number };
}

function authorizeTool(ctx: InvocationContext, tool: string, args: Record<string, unknown>): void {
  const required = `${tool}:${args.scope}`;
  if (!ctx.scopes.includes(required) && !ctx.scopes.includes(`${tool}:*`)) {
    audit.log({ event_type: "mcp.tool.denied", tool, caller: ctx.caller, required });
    throw new McpError(PermissionDenied, "scope insufficient for this invocation");
  }
}
```

Do not reuse a broad session token across unrelated tools.

## Message Signing Hook (protocol-layer prep)

```typescript
interface SignedMcpEnvelope {
  payload: string;          // canonical JSON-RPC body
  signature: string;        // base64
  key_id: string;
  nonce: string;
  expires_at: string;       // ISO-8601
}

function verifyInbound(envelope: SignedMcpEnvelope): void {
  if (new Date(envelope.expires_at) <= new Date())
    throw new SecurityError("message expired");
  if (replayCache.has(envelope.nonce))
    throw new SecurityError("replay detected");
  if (!crypto.verify(envelope.payload, envelope.signature, resolveKey(envelope.key_id)))
    throw new SecurityError("invalid signature");
  replayCache.add(envelope.nonce);
}
```

Wire this at the gateway first; MCP servers verify before executing handlers.

## Fail-Closed Handler Template

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request, extra) => {
  const ctx = extractInvocationContext(extra); // scopes, caller, correlation_id
  try {
    authorizeTool(ctx, request.params.name, request.params.arguments ?? {});
    const validated = validateToolInput(request.params.name, request.params.arguments);
    const raw = await runTool(request.params.name, validated, ctx);
    const safe = sanitizeForAgent(raw);
    audit.emit({ event_type: "mcp.tool.result", ...ctx, tool: request.params.name, status: "success" });
    return { content: [{ type: "text", text: JSON.stringify(safe) }] };
  } catch (err) {
    audit.emit({ event_type: "mcp.tool.result", ...ctx, tool: request.params.name, status: "error", error: String(err) });
    throw err; // never return partial success with elevated behavior
  }
});
```

## Health / Inventory Endpoint

```json
GET /health

{
  "server_id": "acme-records-mcp",
  "transport": "streamable-http",
  "tools": [
    { "name": "search_records", "version": "1.2.0", "fingerprint": "sha256:…" }
  ],
  "bind": "mcp-internal:8080",
  "sandbox": { "seccomp": true, "read_only_root": true, "egress": "deny" }
}
```

Supports operator discovery (Requirement 9) and inventory pinning (Requirement 5).
