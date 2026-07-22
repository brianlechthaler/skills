---
name: opencode-setup
description: >-
  Configure OpenCode with a specified provider and model, writing opencode.json
  and .env.example with a placeholder API key the user must fill in. Use when
  setting up OpenCode, configuring LLM providers, choosing a default model, or
  when the user mentions opencode.json, OpenCode provider setup, or API key
  configuration.
---

# OpenCode Setup

Configure [OpenCode](https://opencode.ai) with a **provider** and **model** the user specifies. Write config files with a **placeholder API key** and tell the user exactly where to replace it.

Pair with [github-publish](../github-publish/SKILL.md) when committing project config to a repo.

## Required inputs

Collect before writing files (ask if missing):

| Input | Example | Notes |
|-------|---------|-------|
| **provider** | `anthropic`, `openai`, `openrouter`, `my-gateway` | OpenCode provider ID — lowercase, matches `/connect` and config keys |
| **model** | `claude-sonnet-4-5`, `gpt-4.1`, `moonshotai/kimi-k2` | Model ID within that provider |
| **scope** | `project` (default) or `global` | Project → `./opencode.json`; global → `~/.config/opencode/opencode.json` |

Optional (custom / proxy providers only):

| Input | When needed |
|-------|-------------|
| **baseURL** | OpenAI-compatible or proxy endpoint (e.g. `https://api.myprovider.com/v1`) |
| **npm** | AI SDK package; default `@ai-sdk/openai-compatible`; use `@ai-sdk/openai` for `/v1/responses` models |
| **display name** | Human-readable provider label in the TUI |

## Workflow

Copy and track:

```
OpenCode setup progress:
- [ ] Provider and model confirmed
- [ ] Scope chosen (project vs global)
- [ ] Existing opencode.json merged (not overwritten blindly)
- [ ] opencode.json written with model and provider block
- [ ] .env.example written with YOUR_API_KEY_HERE placeholder
- [ ] User instructed to copy .env.example → .env and fill in key
- [ ] .env added to .gitignore (project scope only)
- [ ] Setup verified (config valid, opencode sees model)
```

## Step 1 — Resolve provider type

**Built-in provider** — OpenCode ships support via Models.dev (anthropic, openai, openrouter, groq, deepseek, xai, together, …). Config needs only `provider.<id>.options.apiKey` and `model`.

**Custom / proxy provider** — Any OpenAI-compatible API or provider not in Models.dev. Config must include `npm`, `name`, `options.baseURL`, and `models.<model-id>`.

When unsure, check [OpenCode providers docs](https://opencode.ai/docs/providers/) or treat as custom with `@ai-sdk/openai-compatible`.

## Step 2 — Derive env var name

Use the provider's conventional env var when known:

| Provider ID | Env var |
|-------------|---------|
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openai` | `OPENAI_API_KEY` |
| `openrouter` | `OPENROUTER_API_KEY` |
| `groq` | `GROQ_API_KEY` |
| `deepseek` | `DEEPSEEK_API_KEY` |
| `xai` | `XAI_API_KEY` |
| `google` | `GOOGLE_GENERATIVE_AI_API_KEY` |
| `mistral` | `MISTRAL_API_KEY` |
| `together` | `TOGETHER_AI_API_KEY` |
| `fireworks` | `FIREWORKS_API_KEY` |
| `cerebras` | `CEREBRAS_API_KEY` |
| `opencode` (Zen/Go) | `OPENCODE_API_KEY` |

For unknown providers: `{PROVIDER_ID}` → uppercase, non-alphanumeric → `_`, suffix `_API_KEY` (e.g. `my-gateway` → `MY_GATEWAY_API_KEY`).

Reference env var in config as `{env:VAR_NAME}` — never commit real keys.

## Step 3 — Write opencode.json

**Target path**

- Project: `opencode.json` in repo root (or nearest git root)
- Global: `~/.config/opencode/opencode.json` (create directory if missing)

**Merge rule**: If the file exists, read and merge — set `model`, update `provider.<id>`, preserve unrelated keys (`permission`, `mcp`, `agent`, etc.).

### Built-in provider template

Replace `<provider>`, `<model>`, and `<ENV_VAR>`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "<provider>/<model>",
  "provider": {
    "<provider>": {
      "options": {
        "apiKey": "{env:<ENV_VAR>}"
      }
    }
  }
}
```

### Custom provider template

Replace placeholders; set `baseURL` from user or provider docs:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "<provider>/<model>",
  "provider": {
    "<provider>": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "<Display Name>",
      "options": {
        "baseURL": "<https://api.example.com/v1>",
        "apiKey": "{env:<ENV_VAR>}"
      },
      "models": {
        "<model>": {
          "name": "<Model Display Name>"
        }
      }
    }
  }
}
```

Model format is always `provider_id/model_id` (e.g. `anthropic/claude-sonnet-4-5`).

## Step 4 — Placeholder API key files

**`.env.example`** (project scope — commit this):

```bash
# OpenCode — replace YOUR_API_KEY_HERE with your real key, then copy to .env
<ENV_VAR>=YOUR_API_KEY_HERE
```

**User instructions** (always include in your reply):

1. Copy `.env.example` to `.env` (or export the var in your shell profile for global scope).
2. Replace `YOUR_API_KEY_HERE` with your API key from the provider's dashboard.
3. Never commit `.env` — ensure `.gitignore` contains `.env`.

For global scope, tell the user to export the var or add it to `~/.config/opencode/.env` and load it before running `opencode`.

Alternative: user can run `/connect` in the OpenCode TUI and paste the key (stored in `~/.local/share/opencode/auth.json`) instead of env vars — mention this as an option, but still ship `.env.example` for declarative setup.

## Step 5 — Verify

```bash
# Config present
test -f opencode.json || test -f ~/.config/opencode/opencode.json

# Optional: list stored credentials
opencode auth list

# Start OpenCode and confirm model
opencode
# then: /models  — selected provider/model should appear
```

If the provider requires `baseURL` and requests fail, confirm endpoint and npm package (`@ai-sdk/openai-compatible` vs `@ai-sdk/openai`).

## Anti-patterns

| Avoid | Do instead |
|-------|------------|
| Hardcoding real API keys in `opencode.json` | `{env:VAR}` + `.env.example` placeholder |
| Overwriting existing `opencode.json` | Merge; preserve unrelated settings |
| Committing `.env` | `.env.example` only; `.env` in `.gitignore` |
| Mismatched provider ID in `/connect` vs config | Same `<provider>` string everywhere |
| Custom provider without `models` entry | Register model under `provider.<id>.models` |

## Additional resources

- Provider-specific examples: [examples.md](examples.md)
- Env var table and npm package notes: [reference.md](reference.md)
