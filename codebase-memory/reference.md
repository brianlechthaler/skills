# Codebase Memory — Tool Reference

Reference for [SKILL.md](SKILL.md). Read tool schemas under `mcps/user-codebase-memory-mcp/tools/` before calling.

## Indexing

### `list_projects`

No required args. Returns all indexed projects with node/edge counts.

### `index_repository`

| Param | Required | Notes |
|-------|----------|-------|
| `repo_path` | yes | Absolute path to repository |
| `mode` | no | `full` (default), `moderate`, `fast`, `cross-repo-intelligence` |
| `target_projects` | cross-repo mode | Array of project names; `["*"]` for all |
| `persistence` | no | `true` writes `.codebase-memory/graph.db.zst` for team sharing |

### `index_status`

| Param | Required |
|-------|----------|
| `project` | yes |

### `delete_project`

| Param | Required |
|-------|----------|
| `project` | yes |

## Search

### `search_graph`

| Param | Notes |
|-------|-------|
| `project` | Required |
| `query` | BM25 natural-language search; ignores `name_pattern` when set |
| `name_pattern` | Regex on symbol names |
| `qn_pattern` | Regex on qualified names |
| `label` | `Function`, `Class`, `Route`, etc. |
| `file_pattern` | Path regex |
| `semantic_query` | **Array** of keyword strings, e.g. `["auth", "login"]` |
| `relationship`, `min_degree`, `max_degree` | Graph filters |
| `limit` / `offset` | Default limit 200; paginate while `has_more` is true |

### `search_code`

| Param | Notes |
|-------|-------|
| `pattern`, `project` | Required |
| `mode` | `compact` (default), `full`, `files` |
| `file_pattern` | Glob for grep `--include` |
| `path_filter` | Regex on result paths |
| `regex` | Default false |
| `context` | Lines around match (compact mode) |
| `limit` | Default 10; no offset — narrow query or raise limit |

## Read & Analyze

### `get_code_snippet`

| Param | Required | Notes |
|-------|----------|-------|
| `qualified_name` | yes | From `search_graph`; short names may return suggestions |
| `project` | yes | |
| `include_neighbors` | no | Default false |

### `trace_path`

| Param | Required | Notes |
|-------|----------|-------|
| `function_name`, `project` | yes | |
| `direction` | no | `inbound`, `outbound`, `both` (default) |
| `depth` | no | Default 3 (max 5) |
| `mode` | no | `calls`, `data_flow`, `cross_service` |
| `parameter_name` | data_flow | Scope to one parameter |
| `risk_labels` | no | CRITICAL/HIGH/MEDIUM/LOW by hop distance |

### `query_graph`

| Param | Required | Notes |
|-------|----------|-------|
| `query`, `project` | yes | Read-only Cypher subset |
| `max_rows` | no | Hard ceiling 100k rows |

Supported Cypher: `MATCH`, `WHERE`, `RETURN`, `ORDER BY`, `LIMIT`, `WITH`, `UNION`, aggregates. No writes (`MERGE`, `CREATE`).

### `get_architecture`

| Param | Required |
|-------|----------|
| `project` | yes |
| `aspects` | no — filter returned sections |

### `get_graph_schema`

| Param | Required |
|-------|----------|
| `project` | yes |

Run once when learning a new project's graph shape.

## Maintenance

### `detect_changes`

| Param | Required | Notes |
|-------|----------|-------|
| `project` | yes | |
| `scope` | no | |
| `depth` | no | Default 2 |
| `base_branch` | no | Default `main` |
| `since` | no | Git ref or date |

### `manage_adr`

| Param | Required | Notes |
|-------|----------|-------|
| `project` | yes | |
| `mode` | no | `get`, `update`, `sections` |
| `content` | update | ADR body |
| `sections` | sections | Section names |

### `ingest_traces`

| Param | Required |
|-------|----------|
| `traces`, `project` | yes |

Runtime traces to validate `HTTP_CALLS` edges.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `CBM_CACHE_DIR` | `~/.cache/codebase-memory-mcp` | Index storage |
| `CBM_LOG_LEVEL` | `info` | `debug`–`none` |
| `CBM_WORKERS` | auto | Parallel indexing workers |
