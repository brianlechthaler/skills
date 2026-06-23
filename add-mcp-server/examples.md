# Add MCP Server Examples

Patterns referenced from [SKILL.md](SKILL.md). Adapt names and paths to the project.

## Example 1 — PostgreSQL database (TypeScript)

**Context:** App added Postgres with tables `users`, `orders`, `products`. Agents need schema discovery and safe reads.

**Tools:**

| Tool | Input | Behavior |
|------|-------|----------|
| `list_tables` | — | Returns allowlisted table names |
| `describe_table` | `table` (enum) | Column names, types, nullable |
| `query_table` | `table`, `where` (optional object), `limit` (max 100) | Parameterized SELECT |

**Allowlist in code:**

```typescript
const ALLOWED_TABLES = ["users", "orders", "products"] as const;

function assertTable(table: string): asserts table is (typeof ALLOWED_TABLES)[number] {
  if (!ALLOWED_TABLES.includes(table as any)) {
    throw new Error(`Table not allowed: ${table}`);
  }
}
```

**`.cursor/mcp.json`:**

```json
{
  "mcpServers": {
    "acme-db": {
      "command": "npm",
      "args": ["run", "mcp:db", "--prefix", "mcp/acme-db"],
      "env": {
        "DATABASE_URL": "${env:DATABASE_URL}"
      }
    }
  }
}
```

**`package.json` script (project root or mcp package):**

```json
"mcp:db": "node mcp/acme-db/dist/index.js"
```

**`.env.example`:**

```
DATABASE_URL=postgresql://user:pass@localhost:5432/acme_dev
```

---

## Example 2 — SQLite embedded database (Python)

**Context:** CLI tool uses local `data/app.db`. Agents need read-only inspection.

**Tools:** `list_tables`, `describe_table`, `query_table` (same as above)

**Server entry (`mcp/app-db/server.py`):**

```python
import os
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("app-db")
DB_PATH = os.environ["SQLITE_PATH"]

@mcp.tool()
def list_tables() -> list[str]:
    """List tables in the application database."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [r[0] for r in rows]
```

**`.cursor/mcp.json`:**

```json
{
  "mcpServers": {
    "app-db": {
      "command": "uv",
      "args": ["run", "mcp/app-db/server.py"],
      "env": {
        "SQLITE_PATH": "${workspaceFolder}/data/app.db"
      }
    }
  }
}
```

---

## Example 3 — Internal REST API

**Context:** Service exposes `GET /api/v1/customers`, `GET /api/v1/customers/:id`. Agents should search customers.

**Tools:**

| Tool | Input | Behavior |
|------|-------|----------|
| `search_customers` | `query`, `limit` | Proxies to API with validated params |
| `get_customer` | `customer_id` (UUID) | Single record |

**Env:**

```
API_BASE_URL=http://localhost:8080
API_TOKEN=           # service account; never commit
```

Use `fetch` with timeout; return JSON text content. Map 404 to a clear tool error, not a stack trace.

---

## Example 4 — After creating a new database in Docker Compose

**Workflow:**

1. Database service added to `compose.yaml` (e.g. `postgres:16`)
2. App migrations run; schema exists
3. Create `mcp/<name>/` server with read tools
4. Point `DATABASE_URL` at the compose service hostname (`postgres:5432` from app network; `localhost:5432` from host)
5. Add `.cursor/mcp.json` with env from shell or compose env file
6. Document in `docs/mcp.md`: start stack with `docker compose up -d postgres`, then reload MCP

---

## Example 5 — Verify tools in Cursor

After config reload:

1. List MCP tools for the new server (read schemas first)
2. Call `list_tables` — expect known tables
3. Call `query_table` with `limit: 5` — expect truncated JSON
4. Call with invalid `table` — expect permission/validation error, not a crash
5. Confirm no credentials appear in tool output

---

## Example 6 — When NOT to build a custom server

| Situation | Alternative |
|-----------|-------------|
| Postgres + only need ad-hoc SQL in dev | Existing community Postgres MCP (if policy allows) |
| GitHub issues/PRs | Use GitHub MCP or `gh` CLI skill |
| Generic filesystem | Only if path allowlisting is enforced; prefer domain-specific tools |

Custom project MCP servers shine when tools must enforce **project-specific** rules (table allowlists, business validation, audit).
