# Headroom — Examples

## Example 1: Large grep output

**Situation:** `grep` returns 500 matches across 40 files (~15k tokens).

```
1. headroom_compress(content=<full grep output>)
   → compressed summary + hash=fa3b91
2. Identify top 3 relevant files from compressed summary
3. headroom_retrieve(hash=fa3b91, query="AuthMiddleware")
   → full lines for that symbol only
4. Edit the one file that matters
```

**Result:** ~90% fewer tokens during exploration; full detail only for the edit target.

## Example 2: Test failure log

**Situation:** `pytest -v` produces 8k lines; one assertion failed.

```
1. headroom_compress(content=<full pytest output>)
2. Read compressed output — locate failing test name and assertion
3. headroom_retrieve(hash=<hash>, query="test_user_login_invalid_password")
4. Fix the test or implementation with exact traceback in hand
```

## Example 3: Multi-file architecture review

**Situation:** Need overview of 12 service files without loading all into context.

```
1. Read each file (or batch read)
2. headroom_compress each file's content immediately after read
3. Build architecture summary from compressed versions only
4. headroom_retrieve for the one module user asks to change
5. headroom_stats at end — report tokens saved to user
```

## Example 4: MCP not installed

**Situation:** `headroom_compress` unavailable.

```
1. pip install "headroom-ai[mcp]"
2. headroom mcp install   # or manual ~/.cursor/mcp.json entry
3. Restart Cursor / reload MCP
4. headroom_stats to confirm
5. Resume compression workflow
```
