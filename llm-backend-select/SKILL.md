---
name: llm-backend-select
description: >-
  Empirically benchmark local LLM inference backends (Ollama, llama.cpp, vLLM)
  on the user's system and recommend the best runtime for a chosen metric —
  decode throughput, prefill speed, time-to-first-token, KV cache capacity,
  memory footprint, or concurrent throughput. Use when choosing between Ollama,
  llama.cpp, or vLLM, comparing inference runtimes, or optimizing local LLM
  serving performance.
---

# LLM Backend Select — Benchmark and Pick the Best Runtime

Run **fair, measured benchmarks** across every installed local inference backend (Ollama, llama.cpp, vLLM), then recommend the winner for the **metric the user chooses**. Do not guess from blog posts or defaults — collect numbers on this machine with the same model, quantization, and context settings.

For **which model** fits the hardware, use [llmfit](../llmfit/SKILL.md) first. Use this skill when the model (or a close equivalent) is settled and the question is **which runtime serves it best**.

## When This Applies

| Use this skill | Skip this skill |
|----------------|-----------------|
| User asks Ollama vs llama.cpp vs vLLM | Cloud-only APIs (OpenAI, Anthropic, etc.) |
| Choosing a local inference server/runtime | Picking which model to download (use llmfit) |
| Optimizing tok/s, TTFT, KV cache, or VRAM on-device | Single backend already chosen — only need install steps |
| Comparing backends after hardware change | Theoretical leaderboard comparisons without running locally |
| User says "fastest backend", "most context", "lowest latency" | |

Default to this skill when the user wants a **local** backend recommendation and has not specified one, or when performance tradeoffs depend on measured runtime behavior.

## Prerequisites

1. **At least one backend installed or installable** — Ollama, llama.cpp (`llama-server` / `llama-bench`), or vLLM
2. **A test model agreed or auto-selected** — same weights and quantization across backends when possible (e.g. `Qwen2.5-7B-Instruct-Q4_K_M`)
3. **GPU/CPU visibility** — `nvidia-smi`, `rocm-smi`, or CPU-only path confirmed; note VM/container passthrough limits
4. **Optional:** [llmfit](../llmfit/SKILL.md) for `llmfit bench` and hardware JSON
5. **Optional:** [hardware-metrics](../hardware-metrics/SKILL.md) when thermal throttling or VRAM pressure may skew results

Verify backends:

```bash
command -v ollama && ollama --version
command -v llama-server llama-bench 2>/dev/null; llama-server --version 2>/dev/null || true
python3 -c "import vllm; print('vllm', vllm.__version__)" 2>/dev/null || true
nvidia-smi -L 2>/dev/null || echo "no NVIDIA GPU detected"
```

## Core Workflow

Copy and track:

```
LLM backend select:
- [ ] Step 0: Ask user which metric to optimize for
- [ ] Step 1: Recon — hardware, backends available, test model
- [ ] Step 2: Normalize test config (model, quant, context, batch)
- [ ] Step 3: Start each backend with identical settings
- [ ] Step 4: Warm up, then run metric-specific benchmarks (≥3 samples)
- [ ] Step 5: Optional — KV cache / max-context sweep if that metric was chosen
- [ ] Step 6: Rank backends and deliver recommendation with evidence
```

Run steps **in order**. Do not declare a winner from a single cold run or mismatched models.

### Step 0 — Ask which metric to optimize (required)

**Always ask** before benchmarking unless the user already named one clearly.

Use AskQuestion when available; otherwise ask in chat. Present these options (adapt wording to context):

| Option | Optimizes for | Primary measurements |
|--------|---------------|----------------------|
| **Decode throughput** | Fastest token generation after prefill | Output tok/s (median of steady decode) |
| **Prefill throughput** | Fastest prompt ingestion | Input/prefill tok/s on a long prompt |
| **Time to first token (TTFT)** | Lowest latency to first output token | TTFT ms on short + long prompts |
| **KV cache / max context** | Longest context or largest KV footprint that fits | Max stable context before OOM; VRAM at context N |
| **Memory efficiency** | Smallest VRAM/RAM for the same model+context | Peak GPU memory at fixed context and batch |
| **Concurrent throughput** | Best total tok/s under parallel requests | Aggregate tok/s at concurrency 2–8 |

If the user picks multiple metrics, ask which is **primary** for the final ranking; report secondary metrics in the comparison table.

Also confirm or infer:

- **Model** — user-supplied, or pick one all backends can run (see Step 2)
- **Context length** for throughput tests — default **4096** unless user specifies
- **Quantization** — prefer **Q4_K_M** or the closest match all backends support

### Step 1 — Recon

Record before benchmarking:

- OS, CPU, RAM, GPU(s), driver — `llmfit system --json` if available, else `lscpu`, `free -h`, `nvidia-smi`
- Which backends are installed and their versions
- Whether a backend is already serving the test model (avoid port conflicts)
- Docker vs bare metal (note overhead)

List backends to benchmark. Skip missing backends; note in the report that they were unavailable.

### Step 2 — Normalize test configuration

Fair comparison requires **the same logical model** on every backend:

| Backend | Typical serve command | Default API port |
|---------|----------------------|------------------|
| Ollama | `ollama serve` (often already running) | `11434` |
| llama.cpp | `llama-server -m <gguf> -c <ctx> --host 127.0.0.1 -p 8080` | `8080` |
| vLLM | `python -m vllm.entrypoints.openai.api_server --model <path> --max-model-len <ctx>` | `8000` |

Rules:

1. **Same parameter count and quant** — e.g. 7B Q4_K_M GGUF everywhere; map Ollama tags to equivalent GGUF names
2. **Same context window** (`-c` / `--max-model-len` / Ollama `num_ctx`) for throughput tests
3. **Same GPU layers** when tunable — full GPU offload unless testing CPU-only
4. **Stop other backends** during each run to avoid VRAM contention
5. Document any unavoidable mismatch (e.g. only Ollama has a given tag)

Pull or download the model once per backend before timing.

### Step 3 — Benchmark protocol (all metrics)

For **each backend**, in isolation:

1. **Start server** with normalized config; wait until healthy (`/api/tags`, `/health`, or `/v1/models`)
2. **Warm-up** — one completion with a ~200-token prompt (discard timings)
3. **Measure** — run the metric-specific harness (Step 4) **at least 3 times**
4. **Record** — median and spread; capture `nvidia-smi` peak memory during the run
5. **Tear down** — stop server before the next backend

Use the **OpenAI-compatible** `POST /v1/chat/completions` or `POST /v1/completions` when the backend supports it (all three do). Parse:

- `usage.prompt_tokens`, `usage.completion_tokens`
- `timings` fields when present (llama.cpp server JSON)
- Wall time from `curl` or a small script when usage metadata is enough

Prefer a small reproducible harness (see [examples.md](examples.md)) over hand-timed typing in a chat UI.

**llmfit shortcut** — when Ollama or another discovered provider is running:

```bash
llmfit bench --json
```

Use measured tok/s from llmfit as one data point; still run the unified API harness for apples-to-apples comparison across backends.

### Step 4 — Metric-specific benchmarks

#### Decode throughput (default)

- **Prompt:** short system message + ~50-token user message
- **Generation:** `max_tokens` **256** (steady decode)
- **Score:** `completion_tokens / wall_seconds` — median of ≥3 runs
- **Report:** decode tok/s; note prefill separately if split timings exist

#### Prefill throughput

- **Prompt:** load or generate **≥2000 tokens** (fixed file or repeated paragraph)
- **Generation:** `max_tokens` **1**
- **Score:** `prompt_tokens / prefill_seconds` when timings available; else approximate from total minus decode

#### Time to first token (TTFT)

- **Cases:** (a) short prompt ~50 tokens, (b) long prompt ~2000 tokens
- **Generation:** `max_tokens` **1**, stream enabled
- **Score:** milliseconds from request start to first streamed chunk
- **Report:** both cases; backends with slow prefill lose on long-context chat

#### KV cache / max context

1. Fix generation to **16 tokens**; increase `context` / `num_ctx` / `--max-model-len` in steps (4k → 8k → 16k → 32k → …)
2. For each size: warm-up completion; if success, record peak VRAM and run; on OOM or error, last good size is the ceiling
3. **Score:** highest context length with stable completion; tie-break by lower peak VRAM at that context
4. Optionally estimate KV bytes: scales with `context × layers × head_dim × num_kv_heads × dtype` — cite **measured** max context, not theory alone

#### Memory efficiency

- **Fixed** model, context (e.g. 4096), batch 1
- **Score:** peak GPU memory (MB) from `nvidia-smi` during generation; lower is better
- Note CPU RAM if GPU unified memory (Apple Silicon) or full CPU offload

#### Concurrent throughput

- **Load:** N parallel clients (start with N=4), same short prompt, `max_tokens` 128 each
- **Score:** sum of all completion tokens / wall clock for the batch
- Only compare backends with stable error rates; reduce N if one backend queues badly

### Step 5 — Rank and recommend

Build a comparison table — example:

| Backend | Decode tok/s | TTFT (ms) | Max context | Peak VRAM (MB) | Notes |
|---------|--------------|-----------|-------------|----------------|-------|
| Ollama | | | | | |
| llama.cpp | | | | | |
| vLLM | | | | | |

**Winner** = best value on the **user's chosen primary metric**. Mention tradeoffs on secondary metrics.

Deliver:

1. **Primary metric** and why it matters for their use case
2. **Hardware snapshot** (one line)
3. **Test configuration** — model, quant, context, concurrency
4. **Results table** with medians
5. **Recommendation** — backend name, how to install/serve, tunings that helped
6. **Caveats** — mismatched quants, thermal throttle, only one GPU, backend version differences
7. **Next steps** — production flags, systemd/Docker, or [llmfit](../llmfit/SKILL.md) for model changes

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Recommending from reputation ("vLLM is always fastest") | Run the harness on this system |
| Different models per backend (7B vs 8B) | Same weights + quant; document exceptions |
| Single timed run | Warm-up + ≥3 samples; report median |
| All backends running simultaneously | One backend at a time; clear VRAM between |
| Ignoring TTFT when user cares about chat UX | Ask metric first; include TTFT case |
| Max context from docs only | Empirical context sweep until failure |
| Skipping install check | `command -v` / import test each backend |
| CPU vs GPU mismatch | Same `-ngl` / GPU policy across backends |

## Additional Resources

- Backend-specific commands and harness: [examples.md](examples.md)
- Model fit and `llmfit bench`: [llmfit](../llmfit/SKILL.md)
- GPU/thermal context during long sweeps: [hardware-metrics](../hardware-metrics/SKILL.md)
