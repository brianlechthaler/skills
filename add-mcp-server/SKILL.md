---
name: add-mcp-server
description: >-
  Add a Model Context Protocol (MCP) server to a project so agents can interact
  with project resources — databases, APIs, file stores, CLIs, or internal
  services. Use when creating or exposing a database, API, or service that
  agents should query or control; when the user asks for an MCP server, MCP
  tools, or agent access to project data; or after building infrastructure
  that lacks an agent-facing interface.
---

# Add MCP Server to a Project

When a project gains a resource agents should use (database, REST API, queue, filesystem, CLI), **add a project-local MCP server** that exposes safe, typed tools — then wire it into Cursor (and document it).

## When to Apply

| Apply | Skip |
|-------|------|
| New database, API, or service agents should query/update | Consuming a third-party MCP server only (no server code in repo) |
| User asks for MCP tools or agent access to project data | Pure UI work with no agent integration |
| Internal CLI or script that agents should invoke | One-off SQL in a migration with no ongoing agent use |

Pair with [mcp-security](../mcp-security/SKILL.md) for every server you ship. Use [github-publish](../github-publish/SKILL.md) when committing the server to the repo.

## Workflow

Copy and track:

```
MCP server progress:
- [ ] Domain mapped (entities, operations, blast radius)
- [ ] Tools designed (least privilege, typed schemas)
- [ ] Server implemented in mcp/<name>/
- [ ] Env/config documented (.env.example, no secrets committed)
- [ ] Cursor MCP config added (.cursor/mcp.json)
- [ ] Server starts and tools respond to smoke calls
- [ ] Project docs updated (README or docs/mcp.md)
- [ ] mcp-security checklist applied
```

### Step 1 — Map the domain

Before writing code, list what agents need:

1. **Resources** — tables, collections, endpoints, paths
2. **Operations** — read schema, search, insert, run migration-safe query, call endpoint
3. **Constraints** — read-only vs write, row limits, allowed tables, PII boundaries
4. **Connection** — how the server reaches the resource (connection string, socket, HTTP base URL)

Default to **read-only tools** unless the user explicitly needs writes. Never expose raw SQL execution without parameterization and allowlists.

### Step 2 — Design tools

Each MCP tool = one bounded capability:

| Good tool | Bad tool |
|-----------|----------|
| `list_tables` — returns table names | `run_query` — arbitrary SQL string |
| `search_users` — `query` + `limit` (max 50) | `execute` — free-form command |
| `get_order` — `order_id` required | `admin` — does everything |

Tool schema rules:

- `additionalProperties: false` on inputs
- Explicit `required` fields; enums for known sets
- `maxLength` / `maximum` on strings and arrays
- Version tools when semantics change (`version` in metadata or description)

See [examples.md](examples.md) for database and HTTP API patterns.

### Step 3 — Choose stack and layout

**Default layout** (keep server inside the project):

```
mcp/
└── <service-name>/
    ├── package.json or pyproject.toml
    ├── src/
    │   └── index.ts or server.py
    ├── README.md
    └── .env.example
```

| Factor | TypeScript (`@modelcontextprotocol/sdk`) | Python (`mcp`) |
|--------|-------------------------------------------|----------------|
| Project already Node/TS | Preferred | — |
| Project already Python | — | Preferred |
| Team preference unknown | TypeScript | Python |

**Transport:** use **stdio** for local Cursor integration unless the user needs remote/HTTP access.

### Step 4 — Implement the server

Minimal TypeScript skeleton:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "<project>-<resource>", version: "1.0.0" });

server.tool(
  "list_tables",
  "List tables the agent may query (read-only).",
  {},
  async () => {
    // connect via env DATABASE_URL; return { content: [{ type: "text", text: JSON.stringify(tables) }] }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

Minimal Python skeleton:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("<project>-<resource>")

@mcp.tool()
def list_tables() -> list[str]:
    """List tables the agent may query (read-only)."""
    ...

if __name__ == "__main__":
    mcp.run()
```

Implementation rules:

- Read `DATABASE_URL`, `API_BASE_URL`, etc. from **environment variables** — never hardcode credentials
- Validate every argument before touching the resource
- Return structured JSON as `text` content; cap response size (truncate with a clear message)
- Fail closed on auth/connection errors with actionable messages (no stack traces to the agent)

For full patterns, see [reference.md](reference.md).

### Step 5 — Configure Cursor MCP

Add **project-local** config at `.cursor/mcp.json` (committed) so the team shares the same server definition:

```json
{
  "mcpServers": {
    "<project>-<resource>": {
      "command": "node",
      "args": ["mcp/<service-name>/dist/index.js"],
      "env": {
        "DATABASE_URL": "${env:DATABASE_URL}"
      }
    }
  }
}
```

Python example:

```json
{
  "mcpServers": {
    "<project>-<resource>": {
      "command": "uv",
      "args": ["run", "mcp/<service-name>/server.py"],
      "env": {
        "DATABASE_URL": "${env:DATABASE_URL}"
      }
    }
  }
}
```

Use absolute paths only when the runtime requires them. Prefer project-relative commands (`npm run mcp`, `uv run`) via a `package.json` / `Makefile` script.

**After editing:** restart Cursor or reload MCP. Read tool schemas under the new server before calling tools in agent sessions.

### Step 6 — Verify

1. Start dependencies (database, API) — use [docker](../docker/SKILL.md) when the project is containerized
2. Run the MCP server command manually; confirm it stays alive on stdio
3. Reload MCP in Cursor; call each tool with valid and invalid inputs
4. Confirm secrets are not logged and write tools are blocked without explicit scope

Add a smoke script or `npm test` / `pytest` target when the project already has a test harness.

### Step 7 — Document

Add `mcp/<service-name>/README.md` or a section in project docs covering:

- Purpose and tool list
- Required env vars (from `.env.example`)
- How to start locally
- Read-only vs write capabilities
- Link to security notes if production-bound

Update the project README with a one-line pointer to the MCP server.

### Step 8 — Security (required)

Apply [mcp-security](../mcp-security/SKILL.md) before marking work complete. Minimum for project-local dev servers:

- Parameterized queries / validated IDs only
- Per-tool least privilege (separate read vs write tools)
- No secrets in repo or MCP config values — use env interpolation
- Structured errors without leaking connection strings

## Common Scenarios

| Scenario | Typical tools |
|----------|----------------|
| SQL database | `list_tables`, `describe_table`, `query_table` (parameterized filters), optional `insert_row` |
| REST API | `get_resource`, `list_resources`, `create_resource` (if needed) |
| Files / repo data | `list_files`, `read_file` (path allowlist), `search_content` |
| CLI wrapper | One tool per subcommand; no shell passthrough |

Detailed walkthroughs: [examples.md](examples.md).

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| One mega-tool that runs arbitrary code/SQL | Small, typed, allowlisted tools |
| Committing `.env` with real credentials | `.env.example` + env interpolation in mcp.json |
| Skipping MCP config (server exists but agent can't see it) | Commit `.cursor/mcp.json` |
| Returning unbounded result sets | Default limits + truncation notice |
| Implementing without mcp-security review | Run mcp-security checklist |

## Additional Resources

- Tool design and SDK details: [reference.md](reference.md)
- Database and API examples: [examples.md](examples.md)
- Production hardening: [mcp-security](../mcp-security/SKILL.md)
