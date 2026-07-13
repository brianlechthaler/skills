---
name: llmfit
description: >-
  Pick the best local LLM for the user's hardware using llmfit — detect RAM,
  CPU, and GPU, score models for fit/speed/quality/context, and recommend
  runnable options. Use when choosing a local model, running LLMs on-device,
  Ollama/llama.cpp/MLX setup, hardware-constrained inference, or the user
  mentions llmfit, local model fit, or what model runs on this machine.
---

# llmfit — Pick Local Models for Your Hardware

Use [llmfit](https://github.com/AlexsJones/llmfit) to detect system specs and rank hundreds of models by memory fit, estimated speed, quality, and context — then recommend what will actually run well locally.

## When This Applies

| Use llmfit | Skip llmfit |
|------------|-------------|
| User asks which local model fits their machine | Cloud-only API models (no local inference) |
| Setting up Ollama, llama.cpp, MLX, LM Studio, or Docker Model Runner | Model choice unrelated to hardware (e.g. benchmark leaderboard only) |
| Hardware is limited (laptop GPU, unified memory, low RAM) | User already named a specific model and only needs install steps |
| Comparing quantizations or context sizes for one model | Remote/cluster scheduling where node hardware is unknown |
| Verifying whether a named model will run before download | |

Default to llmfit when the user wants a **local** model but has not specified one, or when fit/speed tradeoffs depend on detected hardware.

## Prerequisites — llmfit Installed

Confirm the CLI is available before recommending models.

### Install (pick one)

```bash
# macOS / Linux — prebuilt binary (recommended)
brew install AlexsJones/llmfit/llmfit

# macOS / Linux — no sudo (~/.local/bin)
curl -fsSL https://llmfit.axjns.dev/install.sh | sh -s -- --local

# Python / uv
uv tool install -U llmfit

# Run without installing
uvx llmfit --help

# Windows
scoop install llmfit

# Docker (JSON output, no host install)
docker run ghcr.io/alexsjones/llmfit recommend --json
```

Verify:

```bash
command -v llmfit && llmfit --version
llmfit doctor          # paste into issues if detection looks wrong
llmfit system --json   # RAM, CPU, GPU as JSON
```

If autodetection is wrong (VM, passthrough, broken `nvidia-smi`), override hardware for the session:

```bash
llmfit --memory=24G --ram=64G --cpu-cores=8 system --json
```

## Core Workflow

Copy and track:

```
llmfit progress:
- [ ] llmfit installed and `system --json` looks correct
- [ ] Use case identified (coding, chat, reasoning, multimodal, embedding)
- [ ] Context budget set (--max-context if not default)
- [ ] Recommendations fetched (recommend --json or fit)
- [ ] Top pick validated (info on chosen model)
- [ ] Optional: bench for measured tok/s on running provider
- [ ] User told how to pull/run with their runtime (Ollama, MLX, etc.)
```

### Step 1 — Capture hardware and constraints

1. Run `llmfit system --json` and note RAM, VRAM, GPU backend, and CPU cores.
2. Ask or infer **use case**: `general`, `coding`, `reasoning`, `chat`, `multimodal`, `embedding`.
3. Set **context cap** when the user needs a fixed window (e.g. 8k RAG):

```bash
llmfit --max-context 8192 system --json
```

Use `llmfit doctor` when specs look off; include its output if filing upstream issues.

### Step 2 — Get ranked recommendations (agent-friendly)

Prefer JSON for parsing; use tables when explaining to the user.

```bash
# Top picks (default limit 5)
llmfit recommend --json

# Filtered by task
llmfit recommend --json --use-case coding --limit 3

# Only models that fit comfortably
llmfit fit --perfect -n 10 --json

# Full ranked table (human-readable)
llmfit fit -n 20

# Force a runtime when user already uses one backend
llmfit recommend --json --force-runtime llamacpp --use-case coding --limit 5
llmfit recommend --json --force-runtime mlx --limit 5
```

On machines without a host install:

```bash
docker run --rm ghcr.io/alexsjones/llmfit recommend --json --use-case coding --limit 5
```

Parse the JSON `models` array. Present the user: **name**, **fit tier**, **estimated tok/s**, **VRAM/RAM**, **context**, and **provider/runtime**.

### Step 3 — Deep-dive one model

Before suggesting a download, inspect fit assumptions:

```bash
llmfit info "Qwen2.5-Coder-7B"
llmfit search "llama 8b"
llmfit plan "Qwen/Qwen3-4B-MLX-4bit" --context 8192 --json
```

`info` shows estimate basis and verify commands. `plan` answers “what hardware do I need for this model at N context?”

### Step 4 — Optional: measure real speed

When a local provider is already running (Ollama, vLLM, MLX, llama-server):

```bash
llmfit bench                  # measure against discovered provider
llmfit bench --all            # all discovered models
```

Measured tok/s replaces estimates in later `fit`/`recommend` output for that hardware. Use `llmfit bench --share` only when the user explicitly wants to contribute benchmarks.

### Step 5 — Deliver a clear recommendation

Summarize for the user:

1. **Hardware snapshot** — from `system --json`
2. **Top 1–3 models** — fit score, speed estimate, memory, context
3. **Why** — use-case match, headroom vs marginal fit
4. **Next steps** — pull command for their runtime (Ollama tag, MLX path, etc.)
5. **Caveats** — marginal fit, CPU offload, or lower context if tight on VRAM

Interactive exploration: `llmfit` (TUI) or `llmfit --tui` in Docker.

## Command Reference

| Command | Purpose |
|---------|---------|
| `llmfit system --json` | Detected hardware |
| `llmfit doctor` | Diagnostic report for bad detection |
| `llmfit recommend --json` | Top model picks for agents/scripts |
| `llmfit fit --json -n N` | Full ranked list, JSON or table |
| `llmfit info "<model>"` | Single-model fit analysis |
| `llmfit search "<query>"` | Find models by name/size/provider |
| `llmfit plan "<model>" --context N --json` | Hardware required for a configuration |
| `llmfit list` | Catalog listing |
| `llmfit bench` | Real tok/s against running provider |
| `llmfit serve` | REST API on `:8787` for automation |

### REST API (optional automation)

```bash
llmfit serve --host 127.0.0.1 --port 8787

curl http://127.0.0.1:8787/api/v1/system
curl "http://127.0.0.1:8787/api/v1/models/top?limit=5&min_fit=good&use_case=coding"
```

## Use-Case → Flag Mapping

| User intent | llmfit flags |
|-------------|--------------|
| Code assistant | `--use-case coding` |
| General chat | `--use-case chat` or `general` |
| Chain-of-thought / math | `--use-case reasoning` |
| Vision | `--use-case multimodal` |
| RAG embeddings | `--use-case embedding` |
| Tight VRAM | `fit --perfect` or `min_fit=good` via API |
| Fixed context window | `--max-context <tokens>` |
| Apple Silicon / MLX | default; or `--force-runtime mlx` |
| llama.cpp / Ollama | `--force-runtime llamacpp` |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Guessing model size from parameter count alone | Run `llmfit recommend` or `info` with detected VRAM |
| Recommending 70B+ on 8 GB VRAM | Use `fit --perfect` and explain tradeoffs |
| Ignoring use case | Pass `--use-case coding` (etc.) |
| Skipping install check | `command -v llmfit` or Docker one-liner |
| Treating estimates as gospel | Use `bench` when provider is running; cite estimate basis from `info` |
| Wrong hardware detection | `doctor` + `--memory` / `--ram` overrides |

## Additional Resources

- Scenario walkthroughs: [examples.md](examples.md)
- Upstream CLI reference: [docs/cli.md](https://github.com/AlexsJones/llmfit/blob/main/docs/cli.md)
- How scoring works: [docs/how-it-works.md](https://github.com/AlexsJones/llmfit/blob/main/docs/how-it-works.md)
- Runtime providers: [docs/providers.md](https://github.com/AlexsJones/llmfit/blob/main/docs/providers.md)
