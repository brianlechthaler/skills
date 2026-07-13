# llmfit — Examples

## Example 1: “What local coding model should I use?”

**Situation:** Developer on a laptop with unknown GPU; wants a coding assistant via Ollama.

```
1. command -v llmfit || curl -fsSL https://llmfit.axjns.dev/install.sh | sh -s -- --local
2. llmfit system --json
3. llmfit recommend --json --use-case coding --limit 5
4. llmfit info "<top pick name>"
5. Tell user: model name, fit tier, est. tok/s, `ollama pull <tag>` (or their runtime)
```

**Result:** Data-driven pick instead of guessing “8B should be fine.”

## Example 2: Marginal VRAM (8 GB GPU)

**Situation:** User wants the best model that **fully** fits 8 GB VRAM at 4k context.

```
1. llmfit --max-context 4096 system --json
2. llmfit --max-context 4096 fit --perfect -n 10 --json
3. If empty: relax to fit -n 10 --json and explain marginal vs perfect
4. llmfit info on the chosen row before recommending download
```

## Example 3: User already named a model

**Situation:** “Can I run Qwen2.5-Coder-32B on this machine?”

```
1. llmfit system --json
2. llmfit info "Qwen2.5-Coder-32B"
3. llmfit plan "Qwen2.5-Coder-32B" --context 8192 --json
4. Answer: yes/no, required VRAM/RAM, suggested quant, or smaller alternative from recommend --json --use-case coding
```

## Example 4: Apple Silicon + MLX

**Situation:** MacBook with unified memory; user uses MLX.

```
1. llmfit system --json                    # note unified memory
2. llmfit recommend --json --force-runtime mlx --use-case coding --limit 3
3. Present MLX-specific artifact names from info output
```

## Example 5: No host install (CI agent / sandbox)

**Situation:** Cannot install brew/cargo; Docker available.

```
docker run --rm ghcr.io/alexsjones/llmfit system --json
docker run --rm ghcr.io/alexsjones/llmfit recommend --json --use-case general --limit 5
```

## Example 6: Bad GPU detection

**Situation:** `system --json` shows 0 VRAM but user has an NVIDIA GPU.

```
1. llmfit doctor                          # capture for debugging
2. llmfit --memory=12G --ram=32G recommend --json --use-case chat --limit 5
3. Suggest fixing drivers; use overrides until detection works
```

## Example 7: Benchmark after Ollama is running

**Situation:** Models already pulled; user wants real speed numbers.

```
1. ollama serve   # or confirm Ollama is up
2. llmfit bench
3. Re-run llmfit recommend --json — measured tok/s now appear for benched models
```
