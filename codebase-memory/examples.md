# Codebase Memory Examples

## Example 1: Find who calls a function

**User:** "What calls `processPayment`?"

```
1. list_projects() → project = "my-app"
2. search_graph({ project: "my-app", query: "processPayment", label: "Function" })
3. trace_path({ project: "my-app", function_name: "processPayment", direction: "inbound", depth: 3 })
4. get_code_snippet for top caller only if editing
```

Skip reading entire payment module into context.

## Example 2: Explore unfamiliar service

**User:** "How does auth work in this repo?"

```
1. index_status({ project: "my-app" }) — index if missing
2. get_architecture({ project: "my-app" })
3. search_graph({ project: "my-app", query: "authentication middleware", label: "Function" })
4. trace_path on entry middleware (outbound, depth 2)
5. get_code_snippet for 1–2 symbols; Read only files being changed
```

## Example 3: Text search without flooding context

**User:** "Find all TODO comments in Go files"

```
search_code({
  project: "my-app",
  pattern: "TODO",
  file_pattern: "*.go",
  mode: "compact",
  limit: 20
})
```

Use `mode: "files"` first if you only need paths; `full` only for specific matches.

## Example 4: After a large refactor

```
1. detect_changes({ project: "my-app", depth: 2 })
2. If many affected symbols outside diff → index_repository({ repo_path: "/abs/path", mode: "moderate" })
3. Resume feature work with search_graph
```

## Example 5: MCP not installed

```
1. curl -fsSL .../install.sh | bash
2. Add mcp.json entry with absolute binary path
3. User restarts Cursor
4. list_projects() → index_repository({ repo_path: "<workspace>" })
5. Continue with graph queries
```

## Example 6: When NOT to use

**User:** "Fix the typo on line 42 of `README.md`"

Use `Read` on that one file — no indexing or graph query needed.
