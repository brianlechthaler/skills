---
name: headroom
description: >-
  Reduce LLM token usage by compressing large tool outputs, file contents,
  search results, and logs before reasoning over them, with reversible retrieval
  via the Headroom MCP server. Use when context is large, token costs matter,
  MCP tool outputs are verbose, or the user mentions headroom, context
  compression, or token reduction.
---

# Headroom

Compress bulky content **before** it enters the conversation context. Headroom stores originals locally and returns a hash so you can retrieve full details on demand — typically 60–95% fewer tokens with the same answers.

Source: [chopratejas/headroom](https://github.com/chopratejas/headroom)

## When This Applies

| Use headroom | Skip headroom |
|--------------|---------------|
| Large tool outputs (search, logs, API dumps) | Small responses that fit comfortably in context |
| Reading many files or long stack traces | Already-compressed or summary content |
| User asks to reduce tokens or context size | Content you will immediately edit in full |
| Repeated exploration of the same bulky data | Single-line answers or tiny diffs |

When unsure and content exceeds ~2k tokens or ~50 lines, **default to compressing first**.

## Prerequisites — MCP Ready

Before using Headroom tools, confirm the MCP server is installed and configured.

### 1. Install Headroom (MCP extra)

```bash
pip install "headroom-ai[mcp]"    # Python 3.10+
# or: headroom mcp install        # auto-configures supported agents
```

Verify:

```bash
command -v headroom-mcp-serve     # wrapper script
headroom mcp serve --help
```

### 2. Configure Cursor MCP

Add to `~/.cursor/mcp.json` (adjust paths):

```json
{
  "mcpServers": {
    "headroom": {
      "command": "/home/<user>/.local/bin/headroom-mcp-serve",
      "args": [],
      "cwd": "/tmp"
    }
  }
}
```

Restart Cursor or reload MCP after changes. The server identifier is **`user-headroom`** (tools appear as `headroom_compress`, etc.).

### 3. Verify MCP is available

List tool schemas under the `user-headroom` MCP server before calling tools. A successful `headroom_stats` call confirms the server is live.

## Core Workflow

Copy and track:

```
Headroom progress:
- [ ] MCP server installed and responding
- [ ] Large content identified for compression
- [ ] headroom_compress applied; hash saved
- [ ] Reasoning done on compressed text
- [ ] headroom_retrieve used only when full detail needed
```

### Step 1 — Compress before reasoning

After any tool returns bulky text (file reads, grep, test output, JSON):

1. Call **`headroom_compress`** with the full `content` string.
2. Note the returned **hash** and compressed text.
3. Use the **compressed text** for analysis, summarization, and next-step planning.

Do **not** paste multi-thousand-line outputs directly into your reasoning when Headroom is available.

### Step 2 — Retrieve on demand

When you need exact lines, full stack traces, or complete JSON:

1. Call **`headroom_retrieve`** with the stored **hash**.
2. Optionally pass **`query`** to filter items inside the stored content.
3. Work from the retrieved original — then re-compress if it will re-enter context.

Compression markers like `[N items compressed... hash=abc123]` in text also carry retrievable hashes.

### Step 3 — Monitor savings

Call **`headroom_stats`** at session end or after heavy compression batches to report tokens saved.

## MCP Tools

Always read schemas under `user-headroom` before calling.

| Tool | Purpose |
|------|---------|
| `headroom_compress` | Shrink content; returns compressed text + hash |
| `headroom_retrieve` | Restore original by hash; optional query filter |
| `headroom_stats` | Session compression stats and cost estimates |

## Token-Saving Patterns

| Situation | Pattern |
|-----------|-----------|
| Multi-file exploration | Compress each file read; retrieve one file when editing |
| Search/grep floods | Compress results; retrieve matches for the chosen file only |
| CI or test logs | Compress full log; retrieve around failure hash/query |
| JSON API responses | Compress; retrieve fields needed for the fix |
| Already compressed | Skip re-compression; use existing hash |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Pasting 10k-line logs into context | `headroom_compress` first |
| Retrieving everything after compress | Retrieve only the slice you need |
| Compressing secrets you must redact | Redact first, then compress |
| Ignoring hash in compress output | Save hash for later retrieval |
| Skipping MCP install check | Verify `headroom_stats` before heavy work |

## Additional Resources

- Usage scenarios: [examples.md](examples.md)
- Upstream docs: [headroom MCP tools](https://headroom-docs.vercel.app/docs/mcp)
