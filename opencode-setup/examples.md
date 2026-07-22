# OpenCode Setup Examples

## Anthropic (project, built-in)

**Inputs:** provider `anthropic`, model `claude-sonnet-4-5`, scope `project`

**opencode.json:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

**.env.example:**

```bash
ANTHROPIC_API_KEY=YOUR_API_KEY_HERE
```

---

## OpenRouter (project, built-in + extra model)

**Inputs:** provider `openrouter`, model `moonshotai/kimi-k2`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/moonshotai/kimi-k2",
  "provider": {
    "openrouter": {
      "options": {
        "apiKey": "{env:OPENROUTER_API_KEY}"
      },
      "models": {
        "moonshotai/kimi-k2": {}
      }
    }
  }
}
```

---

## Custom OpenAI-compatible gateway

**Inputs:** provider `my-gateway`, model `gpt-4.1`, baseURL `https://gateway.example.com/v1`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "my-gateway/gpt-4.1",
  "provider": {
    "my-gateway": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Example Gateway",
      "options": {
        "baseURL": "https://gateway.example.com/v1",
        "apiKey": "{env:MY_GATEWAY_API_KEY}"
      },
      "models": {
        "gpt-4.1": {
          "name": "GPT-4.1"
        }
      }
    }
  }
}
```

**.env.example:**

```bash
MY_GATEWAY_API_KEY=YOUR_API_KEY_HERE
```

---

## Global config

Same JSON as above, written to `~/.config/opencode/opencode.json`. Tell the user to export the env var in `~/.bashrc` / `~/.zshrc` or use `/connect` in the TUI.

---

## Merging into existing config

Existing file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": { "edit": "allow" },
  "model": "openai/gpt-4o"
}
```

After setup for `anthropic` / `claude-sonnet-4-5`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": { "edit": "allow" },
  "model": "anthropic/claude-sonnet-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

`permission` preserved; only `model` and `provider.anthropic` updated.
