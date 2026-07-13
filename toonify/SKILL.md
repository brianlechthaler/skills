---
name: toonify
description: >-
  Reduce LLM token usage by serializing structured data as TOON (Token-Oriented
  Object Notation) instead of JSON or YAML — typically 30–60% fewer tokens with
  lossless round-trip. Use when passing API responses, configs, tabular records,
  or tool outputs to prompts; when requesting structured LLM output; or when the
  user mentions toonify, TOON format, or token-efficient data serialization.
---

# Toonify

Encode **structured data** in TOON before it enters prompts or LLM context. TOON keeps hierarchy and types while cutting redundant punctuation and repeated keys — typically **30–60% fewer tokens** than JSON for tabular and uniform records.

Source: [ScrapeGraphAI/toonify](https://github.com/ScrapeGraphAI/toonify)

## When This Applies

| Use TOON | Skip TOON (keep JSON/YAML) |
|----------|----------------------------|
| API responses, configs, DB rows, analytics tables | Interop with JSON-only tools or APIs |
| Uniform arrays of objects (users, products, logs) | Highly irregular or deeply nested one-off blobs |
| Prompt payloads where token cost matters | Payload already minimal (< ~20 lines) |
| Asking the model to return structured data | Human-facing docs meant for copy-paste as JSON |
| Response format templates without example data | Secrets that must be redacted first |

When unsure and structured data exceeds ~30 lines or ~500 tokens as JSON, **default to TOON encoding**.

**Complements other token skills:**

- Unstructured text (logs, grep, stack traces): [headroom](../headroom/SKILL.md)
- System prompt / rules prose: [prompt-conciseness](../prompt-conciseness/SKILL.md)
- User-facing replies: [terse](../terse/SKILL.md)

## Prerequisites

### Install

```bash
pip install toonify          # Python 3.8+
pip install toonify[pydantic]  # optional Pydantic helpers
```

Verify:

```bash
python -c "from toon import encode; print(encode({'ok': True}))"
toon --help
```

No MCP server is required — use the Python API or CLI from the shell.

## Core Workflow

Copy and track:

```
Toonify progress:
- [ ] Structured payload identified (JSON/dict/list)
- [ ] Encoded to TOON (or generate_structure for output schema)
- [ ] Token/size savings measured (--stats or char estimate)
- [ ] Prompt includes brief TOON format note for the model
- [ ] LLM TOON response decoded when downstream code needs JSON
```

### Step 1 — Encode before prompting

When you have Python objects, parsed JSON, or API results:

```python
import json
from toon import encode

data = json.loads(api_response)  # or dict from tool output
toon_payload = encode(data)
```

Prefer **tabular encoding** — uniform object arrays compress best:

```toon
products[3]{id,name,price}:
  101,Laptop Pro,1299
  102,Magic Mouse,79
  103,USB-C Cable,19
```

**Encoding options** (when data shape warrants):

| Option | When |
|--------|------|
| `delimiter='tab'` | Spreadsheet-like fields; fewer quote escapes |
| `delimiter='pipe'` | Values contain commas |
| `key_folding='safe'` | Deep single-key chains (`a.b.c: value`) |
| `indent=2` | Default; increase only for readability checks |

```python
toon_payload = encode(data, {"delimiter": "tab", "key_folding": "safe"})
```

### Step 2 — CLI for files and quick stats

```bash
# JSON → TOON with savings report
toon data.json --stats -o data.toon

# Pipe from other tools
cat response.json | toon -e --stats

# TOON → JSON for scripts
toon output.toon -d -o output.json
```

Use `--stats` before large prompt inserts to report byte/token reduction to the user.

### Step 3 — Response structure templates (save prompt tokens)

When you need the model to return structured data, **do not** paste full JSON examples. Generate a schema template:

```python
from toon import generate_structure

schema = {
    "issues": [{
        "id": "issue number",
        "title": "short title",
        "severity": "low|medium|high",
    }]
}
template = generate_structure(schema)
```

Include in the prompt:

```markdown
Return findings in TOON format (Token-Oriented Object Notation):
- `key: value` pairs, indentation for nesting
- Tabular arrays: `[N]{field1,field2}:`
- Match array lengths in `[N]` markers

{template}
```

With Pydantic models, use `generate_structure_from_pydantic(Model)` or `encode_pydantic` / `decode_to_pydantic` for typed round-trips.

### Step 4 — Decode model output

When downstream code or tools expect JSON/Python:

```python
from toon import decode

parsed = decode(llm_toon_response)
```

For dotted keys produced with key folding, decode with `expand_paths='safe'` when needed.

### Step 5 — Tell the model the format (one line)

Add once per task when using TOON bidirectionally:

> Data is in TOON (Token-Oriented Object Notation). Tabular blocks use `[count]{fields}:` headers; rows are delimiter-separated. Respond in TOON when asked for structured output.

## Token-Saving Patterns

| Situation | Pattern |
|-----------|---------|
| Search/API JSON in context | `encode()` → paste TOON; keep JSON file on disk if needed |
| Many similar records | Tabular TOON; verify uniform keys first |
| Structured extraction task | `generate_structure(schema)` instead of example JSON |
| Model returns TOON | `decode()` before writing JSON configs or tests |
| Mixed text + JSON log line | Extract JSON, encode slice; leave prose as-is or use headroom |
| Pydantic pipeline | `encode_pydantic` / `decode_to_pydantic` with `exclude_none=True` |

## Measuring Savings

Report to the user when conversion is non-trivial:

```bash
toon payload.json --stats
```

Or estimate: compare `len(json.dumps(data))` vs `len(encode(data))`; chars ÷ 4 ≈ tokens.

Typical benchmarks (upstream): **~54% average token reduction** vs JSON on structured datasets; up to **~73%** for uniform tables.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Pasting 500-line JSON into prompts | `encode()` or `toon file.json --stats` |
| Full JSON examples for output shape | `generate_structure` / Pydantic template |
| TOON for unstructured logs | [headroom](../headroom/SKILL.md) compress first |
| Forcing TOON on irregular nested trees | Keep JSON or summarize manually |
| Skipping decode before JSON-only consumers | `decode()` then `json.dump` |
| Embedding secrets in TOON | Redact, then encode |

## Cross-References

- Large unstructured tool output: [headroom](../headroom/SKILL.md)
- Trim instruction prose: [prompt-conciseness](../prompt-conciseness/SKILL.md)
- Short user replies: [terse](../terse/SKILL.md)

## Additional Resources

- Usage scenarios: [examples.md](examples.md)
- Upstream docs: [toonify README](https://github.com/ScrapeGraphAI/toonify#readme)
- Format spec: [toon-format/toon](https://github.com/toon-format/toon)
