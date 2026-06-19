---
name: codebase-memory
description: >-
  Reduce token usage during codebase exploration by querying a persistent
  knowledge graph instead of reading whole files or running broad grep. Uses the
  codebase-memory MCP server for graph search, architecture overviews, call-path
  tracing, and targeted snippet retrieval. Use when exploring unfamiliar code,
  finding definitions or callers, mapping architecture, or when the user mentions
  codebase-memory, code intelligence, or token-efficient code search.
---

# Codebase Memory

Query a **pre-indexed knowledge graph** instead of loading entire files into context. Search returns signatures and metadata by default; pull full source only for symbols you will edit.

Source: [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)

## When This Applies

| Use codebase-memory | Skip codebase-memory |
|---------------------|----------------------|
| Finding functions, classes, routes, callers | Single known file path to edit |
| Architecture or dependency overview | Trivial one-line lookup |
| Impact analysis (who calls X?) | Repo not indexed and indexing blocked |
| Token-efficient exploration of large repos | User explicitly wants raw grep/read |

When unsure on an unfamiliar or large codebase, **prefer graph search over blanket file reads**.

## Prerequisites — MCP Ready

### 1. Install the MCP server

```bash
# Recommended — auto-configures supported agents
codebase-memory-mcp install -y

# Or download the static binary manually from GitHub releases
# and place it on PATH (e.g. ~/.local/bin/codebase-memory-mcp)
```

Verify:

```bash
codebase-memory-mcp --version
codebase-memory-mcp --help
```

### 2. Configure Cursor MCP

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "/home/<user>/.local/bin/codebase-memory-mcp"
    }
  }
}
```

Restart Cursor or reload MCP. Server identifier: **`user-codebase-memory-mcp`**.

### 3. Index the workspace

Before searching, index the repository:

```
index_repository(repo_path=<absolute workspace path>, mode="fast")
```

Modes:

| Mode | Use when |
|------|----------|
| `fast` | Quick exploration; no semantic edges |
| `moderate` | Balanced; filtered files + semantic |
| `full` | Deep analysis; all files + similarity edges |

Check progress with **`index_status(project=<name>)`**. Project name is typically the repo directory name — confirm with **`list_projects`**.

Re-index after large structural changes via **`detect_changes`** or a fresh **`index_repository`**.

## Core Workflow

Copy and track:

```
Codebase memory progress:
- [ ] MCP server installed and responding
- [ ] Project indexed (index_status green)
- [ ] search_graph / search_code used before bulk file reads
- [ ] get_code_snippet only for symbols being edited
- [ ] Pagination respected when has_more / truncation flags set
```

### Step 1 — Discover before reading

Use graph tools **instead of** grep/glob/read for discovery:

| Goal | Tool | Token-efficient defaults |
|------|------|--------------------------|
| Find definitions by name/keyword | `search_graph` | `query="auth middleware"`, `limit=20` |
| Text pattern with graph ranking | `search_code` | `mode="compact"`, `limit=10` |
| Architecture overview | `get_architecture` | Start without `full` source |
| Callers / callees / impact | `trace_path` | `depth=3`, `include_tests=false` |
| Complex graph queries | `query_graph` | Add `LIMIT` in Cypher |

Always read MCP tool schemas under `user-codebase-memory-mcp` before calling.

### Step 2 — Paginate and detect truncation

Responses include truncation signals — respect them:

| Tool | Truncation signals | Action |
|------|-------------------|--------|
| `search_graph` | `has_more`, `total` | Increase `offset` by `limit` while `has_more` |
| `search_code` | `total_grep_matches` vs `limit` | Raise `limit` or narrow `file_pattern` / `path_filter` |
| `query_graph` | 100k row ceiling | Add `LIMIT` in Cypher or narrow query |

Do **not** assume the first page is complete when `has_more` is true.

### Step 3 — Fetch source surgically

1. **`search_graph`** → get exact `qualified_name`
2. **`get_code_snippet(qualified_name, project)`** → read only that symbol
3. Use **`include_neighbors=true`** only when call context is required

Never read entire directories when graph search can identify the target symbol.

### Step 4 — Cross-repo and maintenance

| Task | Tool |
|------|------|
| List indexed repos | `list_projects` |
| Schema / labels | `get_graph_schema` |
| ADR notes | `manage_adr` |
| Runtime traces | `ingest_traces` |
| Remove stale index | `delete_project` |

## MCP Tools (Quick Reference)

| Tool | Purpose |
|------|---------|
| `index_repository` | Index or re-index a repo |
| `index_status` | Indexing progress |
| `list_projects` | All indexed projects |
| `search_graph` | BM25 / regex / semantic graph search |
| `search_code` | Grep + graph-enriched, ranked results |
| `get_code_snippet` | Source for one symbol (after search_graph) |
| `trace_path` | Callers, callees, data flow, cross-service |
| `get_architecture` | Packages, clusters, high-level structure |
| `query_graph` | Custom Cypher queries |
| `detect_changes` | Incremental re-index hints |
| `get_graph_schema` | Node/relationship schema |

## Token-Saving Patterns

| Instead of | Do |
|------------|-----|
| `Read` entire 2000-line file | `search_graph` → `get_code_snippet` |
| Broad grep across repo | `search_code` with `mode="compact"` |
| Reading all test files for examples | `trace_path` inbound to function |
| Loading full module tree | `get_architecture` overview first |
| Re-reading unchanged files | Check `index_status` / `detect_changes` |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Reading files before searching | Index → search_graph → snippet |
| `search_code mode="full"` for discovery | `compact` first; full only when editing |
| Ignoring `has_more` | Paginate or narrow query |
| Guessing `qualified_name` | Always from `search_graph` results |
| Skipping index step | `index_repository` before first search |
| Mass `query_graph` without LIMIT | Add LIMIT; use search_graph for browsing |

## Additional Resources

- Usage scenarios: [examples.md](examples.md)
