# OpenCode Setup Reference

## Config locations and precedence

| Scope | Path |
|-------|------|
| Project | `opencode.json` in project root (walks up to git root) |
| Global | `~/.config/opencode/opencode.json` |

Later sources override earlier ones for conflicting keys; configs merge. See [OpenCode config docs](https://opencode.ai/docs/config/).

## Credentials storage

| Method | Location |
|--------|----------|
| Env var (`{env:VAR}`) | Shell / `.env` (not committed) |
| `/connect` TUI | `~/.local/share/opencode/auth.json` |
| File ref (`{file:path}`) | User-managed secret file outside repo |

Prefer env vars for team-shared repos; `/connect` for personal machines.

## npm package selection

| API style | npm package |
|-----------|-------------|
| OpenAI-compatible `/v1/chat/completions` | `@ai-sdk/openai-compatible` |
| OpenAI `/v1/responses` | `@ai-sdk/openai` |
| Provider-specific (Cerebras, etc.) | Provider package from [OpenCode providers docs](https://opencode.ai/docs/providers/) |

Per-model override: `provider.<id>.models.<model>.npm`.

## Built-in provider env vars

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
| `opencode` | `OPENCODE_API_KEY` |

Amazon Bedrock and some cloud providers use IAM/env-based auth instead of a single API key — skip `.env.example` and point the user to provider docs.

## Troubleshooting

```bash
opencode auth list          # credentials on disk
opencode                    # TUI → /models, /connect
```

- Provider ID in config must match `/connect` selection.
- Custom providers need `baseURL` and a `models` entry for each model ID.
- 401/403 → key not loaded; confirm `.env` is sourced or `/connect` completed.
