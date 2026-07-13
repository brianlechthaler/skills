# LLM Backend Select — Examples

## Example 1: User wants fastest decode (tok/s)

**Situation:** User has Ollama and llama.cpp; wants the fastest token generation for a coding assistant.

```
1. Ask: optimize for "Decode throughput" (confirm model Qwen2.5-Coder-7B or equivalent)
2. ollama pull qwen2.5-coder:7b-instruct-q4_K_M   # or closest tag
3. Download same GGUF for llama.cpp
4. For each backend (one at a time):
   - Start server with -c 4096, full GPU layers
   - Warm-up: 200-token prompt, max_tokens 32
   - Run decode benchmark 3× (see harness below)
   - Record median decode tok/s + peak nvidia-smi memory
5. Rank by decode tok/s; recommend winner with serve command
```

## Example 2: User needs longest context (KV cache)

**Situation:** RAG with 32k+ tokens; user asks "which backend fits the biggest context?"

```
1. Ask: optimize for "KV cache / max context"
2. Pick one 7B Q4 model available on all backends
3. Context sweep: 4096 → 8192 → 16384 → 32768 → 65536
   - At each step: warm-up completion (16 tokens out)
   - On OOM/error: last successful size is max for that backend
4. Record peak VRAM at max stable context
5. Recommend backend with highest stable context; note VRAM at that size
```

## Example 3: Interactive chat — optimize TTFT

**Situation:** User cares about snappy first reply, not bulk throughput.

```
1. Ask: optimize for "Time to first token (TTFT)"
2. Benchmark short prompt (~50 tok) and long prompt (~2000 tok), max_tokens 1, stream on
3. Median TTFT per backend per case
4. Winner = lowest median TTFT on the case that matches user's typical prompt size
```

## Example 4: Only Ollama installed

**Situation:** User asks for vLLM vs Ollama but vLLM is missing.

```
1. Report: vLLM not installed — benchmark Ollama only
2. Offer to install llama.cpp or vLLM if user wants full comparison
3. Run single-backend baseline so user has numbers for later comparison
```

## Example 5: llmfit already running Ollama

**Situation:** Ollama serves models; user wants to add llama.cpp comparison.

```
1. llmfit system --json
2. llmfit bench --json                    # Ollama baseline
3. Stop Ollama; run llama-server harness  # fair VRAM
4. Compare llmfit bench tok/s vs harness decode tok/s; prefer harness for final table
```

---

## Unified API benchmark harness (bash)

Save as `bench_decode.sh` (adjust `BASE_URL`, `MODEL`, `API_KEY` per backend):

```bash
#!/usr/bin/env bash
# Usage: BASE_URL=http://127.0.0.1:11434/v1 MODEL=qwen2.5-coder:7b-instruct ./bench_decode.sh
set -euo pipefail
BASE_URL="${BASE_URL:-http://127.0.0.1:11434/v1}"
MODEL="${MODEL:-qwen2.5-coder:7b-instruct}"
RUNS="${RUNS:-3}"
MAX_TOKENS="${MAX_TOKENS:-256}"

PROMPT='You are a helpful assistant. Explain in detail how a binary search tree implements insert, delete, and search, including time complexity and edge cases for duplicate keys.'

for i in $(seq 1 "$RUNS"); do
  START=$(date +%s.%N)
  RESP=$(curl -sS "$BASE_URL/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "$(jq -n --arg m "$MODEL" --arg p "$PROMPT" --argjson mt "$MAX_TOKENS" \
      '{model:$m,messages:[{role:"user",content:$p}],max_tokens:$mt,temperature:0}')")
  END=$(date +%s.%N)
  COMP=$(echo "$RESP" | jq -r '.usage.completion_tokens // 0')
  WALL=$(echo "$END - $START" | bc -l)
  TPS=$(echo "scale=2; $COMP / $WALL" | bc -l)
  echo "run=$i completion_tokens=$COMP wall_s=$WALL decode_tok_s=$TPS"
done
```

**Backend endpoints:**

| Backend | `BASE_URL` | `MODEL` example |
|---------|------------|-----------------|
| Ollama | `http://127.0.0.1:11434/v1` | `qwen2.5-coder:7b-instruct` |
| llama.cpp | `http://127.0.0.1:8080/v1` | model alias from server |
| vLLM | `http://127.0.0.1:8000/v1` | HuggingFace path or local dir |

## TTFT with streaming (bash snippet)

```bash
curl -sS -N "$BASE_URL/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{"model":"'"$MODEL"'","messages":[{"role":"user","content":"Hi"}],"max_tokens":1,"stream":true}' \
  | while IFS= read -r line; do
      case "$line" in
        data:\ *) echo "$line" | head -1; break ;;
      esac
    done
```

Measure wall time from curl start to first `data:` line (exclude `data: [DONE]`). Run ≥3 times; report median ms.

## Prefill-heavy prompt

Use a fixed long context file so prompt token count is stable:

```bash
# Generate ~2000-token prompt once
python3 -c "print('The quick brown fox jumps over the lazy dog. ' * 400)" > /tmp/prefill_prompt.txt
PROMPT=$(jq -Rs . /tmp/prefill_prompt.txt)
curl -sS "$BASE_URL/chat/completions" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":$PROMPT}],\"max_tokens\":1,\"temperature\":0}"
```

## Context sweep (KV cache max)

Pseudocode loop — adapt per backend CLI:

```bash
for CTX in 4096 8192 16384 32768 65536; do
  # restart server with -c $CTX or --max-model-len $CTX or OLLAMA_NUM_CTX=$CTX
  if curl -sf ...; then
    echo "ok ctx=$CTX vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)"
  else
    echo "fail ctx=$CTX"; break
  fi
done
```

## Concurrent throughput (Python)

```python
#!/usr/bin/env python3
"""Rough concurrent decode benchmark. pip install httpx"""
import asyncio, time, os
import httpx

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:11434/v1")
MODEL = os.environ["MODEL"]
CONCURRENCY = int(os.environ.get("CONCURRENCY", "4"))
MAX_TOKENS = 128

async def one(client, i):
    r = await client.post(
        f"{BASE}/chat/completions",
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Count from 1 to 100 slowly. Request {i}."}],
            "max_tokens": MAX_TOKENS,
            "temperature": 0,
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["usage"]["completion_tokens"]

async def main():
    async with httpx.AsyncClient() as client:
        t0 = time.perf_counter()
        tokens = await asyncio.gather(*[one(client, i) for i in range(CONCURRENCY)])
        elapsed = time.perf_counter() - t0
    print(f"total_tokens={sum(tokens)} wall_s={elapsed:.2f} aggregate_tok_s={sum(tokens)/elapsed:.2f}")

asyncio.run(main())
```

## Start commands reference

**Ollama** (often already running):

```bash
ollama serve   # if not running
export OLLAMA_NUM_CTX=4096   # when testing context — model-dependent
ollama run <model> --verbose  # one-off; shows eval rate in logs
```

**llama.cpp:**

```bash
llama-server -m /path/to/model.Q4_K_M.gguf -c 4096 -ngl 99 --host 127.0.0.1 -p 8080
# Optional built-in bench (model-only, no server):
llama-bench -m /path/to/model.Q4_K_M.gguf -p 512 -n 128
```

**vLLM:**

```bash
python -m vllm.entrypoints.openai.api_server \
  --model /path/to/model \
  --max-model-len 4096 \
  --host 127.0.0.1 --port 8000
```

## Peak VRAM during a run

```bash
# Sample every second in background while benchmark runs
nvidia-smi dmon -s mu -d 1 -c 60 &
DMON_PID=$!
./bench_decode.sh
kill $DMON_PID 2>/dev/null || true
nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
```

On Apple Silicon or CPU-only, substitute `vm_stat` / `ps` RSS for the serving process.
