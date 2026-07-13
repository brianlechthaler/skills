# Toonify — Examples

## Example 1: API response in a prompt

**Situation:** A REST call returns 200 product records as JSON (~8k tokens).

```
1. Save or hold parsed dict in memory
2. toon_payload = encode(data)
3. toon products.json --stats   # optional CLI check
4. Prompt: "Analyze pricing outliers in this TOON catalog:\n{toon_payload}"
5. decode() only if writing fixes back to JSON APIs
```

**Result:** ~50–60% fewer input tokens vs pretty-printed JSON; same analytical accuracy for tabular data.

## Example 2: Structured extraction without example rows

**Situation:** Extract security findings from a report; avoid shipping sample JSON in the prompt.

```python
from toon import generate_structure

schema = {
    "findings": [{
        "rule": "rule identifier",
        "file": "path",
        "line": "line number",
        "message": "description",
    }]
}
template = generate_structure(schema)

prompt = f"""Audit the diff below. Return findings in TOON format:

{template}
"""
```

**Result:** Format spec in ~10 lines instead of a multi-record JSON example.

## Example 3: Shell pipeline before agent handoff

**Situation:** `curl` returns JSON; agent should reason over compact form.

```bash
curl -s https://api.example.com/v1/users | toon -e --stats > users.toon
```

Agent reads `users.toon` instead of raw JSON.

## Example 4: Pydantic round-trip

**Situation:** Service uses Pydantic models; LLM fills a TOON template.

```python
from pydantic import BaseModel, Field
from toon import generate_structure_from_pydantic, decode_to_pydantic

class Issue(BaseModel):
    id: int = Field(description="GitHub issue number")
    title: str = Field(description="issue title")

structure = generate_structure_from_pydantic(Issue)
# ... send structure in prompt, get TOON back ...
issue = decode_to_pydantic(llm_output, Issue)
```

## Example 5: When not to use TOON

**Situation:** Single deeply nested config with mixed types and few repeated keys.

```
1. Estimate: toon config.json --stats
2. If savings < ~20%, keep JSON or summarize key fields in prose
3. For 10k-line test log (unstructured), use headroom instead
```

## Example 6: TOON + Headroom together

**Situation:** CI outputs JSON lines mixed with prose (~12k tokens total).

```
1. Split log: prose block vs JSON lines
2. headroom_compress(prose_block) for narrative section
3. encode(parsed_json_records) for structured failure rows
4. Reason on compressed prose + TOON table
5. headroom_retrieve only for exact stack trace lines
```
