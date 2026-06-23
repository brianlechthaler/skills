# Add MCP Server Reference

Reference for [SKILL.md](SKILL.md). Read only when implementing.

## Official SDKs

| Language | Package | Docs |
|----------|---------|------|
| TypeScript | `@modelcontextprotocol/sdk` | https://modelcontextprotocol.io |
| Python | `mcp` (FastMCP) | https://github.com/modelcontextprotocol/python-sdk |

Install in the `mcp/<service-name>/` package, not necessarily the app root — keeps dependencies isolated.

## TypeScript project bootstrap

```bash
mkdir -p mcp/my-db/src
cd mcp/my-db
npm init -y
npm install @modelcontextprotocol/sdk zod pg
npm install -D typescript @types/node
```

`tsconfig.json` — target ES2022, `moduleResolution: NodeNext`, `outDir: dist`.

`package.json`:

```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

## Python project bootstrap

```bash
mkdir -p mcp/my-db
cd mcp/my-db
uv init
uv add mcp psycopg[binary]
```

Or `pip install mcp` in a `requirements.txt` if the project does not use uv.

## Tool response shape

MCP tools return **content** arrays. Prefer JSON text:

```typescript
return {
  content: [{ type: "text", text: JSON.stringify({ rows, truncated: false }, null, 2) }],
};
```

Cap payload size (~50–100 KB). When truncating:

```json
{ "rows": [...], "truncated": true, "message": "Showing first 50 of 1200 rows" }
```

## Parameterized SQL pattern

Never interpolate user input into SQL strings.

```typescript
const QuerySchema = z.object({
  table: z.enum(["users", "orders"]),
  limit: z.number().int().min(1).max(100).default(20),
});

// For filters, use a fixed map of column → value with column allowlist
const ALLOWED_FILTER_COLUMNS: Record<string, readonly string[]> = {
  users: ["email", "status"],
  orders: ["status", "customer_id"],
};
```

Use driver parameterized queries (`$1`, `?`) for all dynamic values.

## Cursor MCP config locations

| Scope | Path |
|-------|------|
| Project (commit this) | `.cursor/mcp.json` |
| User global | `~/.cursor/mcp.json` |

Project config is preferred so the MCP server ships with the repo. Use `${workspaceFolder}` and `${env:VAR}` interpolation per Cursor docs.

Server identifier in agent sessions is typically prefixed (e.g. `user-<name>` for user-global; project servers use the key from `mcpServers`).

## npm / Makefile convenience targets

Expose one command the MCP config can call:

```makefile
mcp-db:
	cd mcp/acme-db && npm run build && npm start
```

```json
"scripts": {
  "mcp:db": "npm run build --prefix mcp/acme-db && node mcp/acme-db/dist/index.js"
}
```

## Testing without Cursor

**TypeScript** — run server and send JSON-RPC over stdio (or use SDK test helpers).

**Python:**

```bash
DATABASE_URL=... uv run mcp/my-db/server.py
# Server blocks on stdio; use MCP inspector or Cursor for full integration
```

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) is useful for local tool debugging.

## Security cross-reference

Before production or shared environments, complete [mcp-security/SKILL.md](../mcp-security/SKILL.md):

- Gateway placement for non-local deployments
- Audit events for tool invoke/result
- Container isolation per server
- Tool definition versioning

## File checklist (copy per server)

```
mcp/<service-name>/
├── SKILL.md              # optional; project may link to docs/mcp.md instead
├── README.md             # required
├── .env.example          # required
├── src/ or server.py
├── package.json or pyproject.toml
└── (tests/)              # when project has test harness
.cursor/mcp.json            # at repo root — MCP registration
```
