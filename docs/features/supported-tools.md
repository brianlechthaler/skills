# Supported coding tools

The installer (`install.py`) supports **19 AI coding tools**. Each tool has a stable **agent ID** (used with `-a` / `--agent`), skill install paths, and (for most tools) rule install paths when using `--as-rule`.

Run `python3 install.py --list-agents` anytime to print the current paths from `install.py`.

## Quick reference

| Agent ID | Tool | Skill paths (project → global) | Rules (`--as-rule`) | Auto-detected |
|----------|------|--------------------------------|---------------------|---------------|
| `cursor` | [Cursor](https://cursor.com) | `.cursor/skills` → `~/.cursor/skills` | Per-file `.mdc` in `.cursor/rules` | Yes |
| `claude-code` | [Claude Code](https://code.claude.com) | `.claude/skills` → `~/.claude/skills` | Per-file `.md` in `.claude/rules` | Yes |
| `opencode` | [OpenCode](https://opencode.ai) | `.opencode/skills` → `~/.config/opencode/skills` | Append to `AGENTS.md` | Yes |
| `codex` | [OpenAI Codex](https://developers.openai.com/codex) | `.codex/skills` → `~/.codex/skills` | Append to `AGENTS.md` | Yes |
| `windsurf` | [Windsurf](https://codeium.com/windsurf) | `.windsurf/skills` → `~/.codeium/windsurf/skills` | Per-file (project) / append (global) | Yes |
| `github-copilot` | [GitHub Copilot](https://github.com/features/copilot) | `.github/skills` → `~/.copilot/skills` | Append to `copilot-instructions.md` | Yes |
| `gemini-cli` | [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `.gemini/skills` → `~/.gemini/skills` | Append to `GEMINI.md` | Yes |
| `openclaw` | [OpenClaw](https://docs.openclaw.ai) | `skills` → `~/.openclaw/skills` | Per-file in `.agents/rules` | Yes |
| `hermes-agent` | Hermes Agent | `.hermes/skills` → `~/.hermes/skills` | Per-file in `.hermes/rules` | Yes |
| `mistral-vibe` | Mistral Vibe | `.vibe/skills` → `~/.vibe/skills` | Per-file in `.vibe/rules` | Yes |
| `aider` | [Aider](https://aider.chat) | `.aider/skills` → `~/.aider/skills` | Append to `CONVENTIONS.md` | Yes |
| `kilo-code` | [Kilo Code](https://kilocode.ai) | `.kilo/skills` → `~/.kilo/skills` | Append to `AGENTS.md` (global: `~/.config/kilo/`) | Yes |
| `augment` | [Augment Code](https://www.augmentcode.com) | `.augment/skills` → `~/.augment/skills` | Per-file in `.augment/rules` | Yes |
| `antigravity` | Google Antigravity | `.agents/skills` → `~/.gemini/antigravity/skills` | Per-file in `.agents/rules` | Yes |
| `cline` | [Cline](https://cline.bot) | `.agents/skills` → `~/.agents/skills` | Per-file in `.agents/rules` | No — pass `-a cline` |
| `roo` | [Roo Code](https://roocode.com) | `.roo/skills` → `~/.roo/skills` | Per-file in `.roo/rules` | No — pass `-a roo` |
| `continue` | [Continue](https://continue.dev) | `.continue/skills` → `~/.continue/skills` | Per-file in `.continue/rules` | No — pass `-a continue` |
| `trae` | [Trae](https://www.trae.ai) | `.trae/skills` → `~/.trae/skills` | Per-file in `.trae/rules` | No — pass `-a trae` |
| `universal` | Cross-tool `.agents/` layout | `.agents/skills` → `~/.agents/skills` | Per-file in `.agents/rules` | No — pass `-a universal` |

Install to every tool at once:

```bash
python3 install.py --all -a all -y
```

---

## Skills vs rules

| Mode | Flag | Behavior |
|------|------|----------|
| **Skills** (default) | — | Copies or symlinks `<skill>/` directories containing `SKILL.md`. Agents load them on demand when a task matches the skill description. |
| **Rules** | `--as-rule` | Converts each `SKILL.md` into tool-specific rule files or appended sections for always-on or intelligently-applied guidance. |

See [USAGE.md](../../USAGE.md) for skills-vs-rules guidance, update/remove instructions, and authoring tips.

---

## Rule delivery modes

When installing with `--as-rule`, the installer uses one of two delivery strategies:

### Per-file

One rule file per skill. Re-running `--as-rule` overwrites each file.

| Agent ID | Project path | Global path | File format |
|----------|--------------|-------------|-------------|
| `cursor` | `.cursor/rules/<skill>.mdc` | `~/.cursor/rules/<skill>.mdc` | Cursor rule frontmatter (`alwaysApply: false`) |
| `claude-code` | `.claude/rules/<skill>.md` | `~/.claude/rules/<skill>.md` | Claude rule frontmatter |
| `windsurf` | `.windsurf/rules/<skill>.md` | `~/.codeium/windsurf/memories/global_rules.md` (append) | `trigger: model_decision` |
| `openclaw` | `.agents/rules/<skill>.md` | `~/.agents/rules/<skill>.md` | Plain markdown |
| `hermes-agent` | `.hermes/rules/<skill>.md` | `~/.hermes/rules/<skill>.md` | Plain markdown |
| `mistral-vibe` | `.vibe/rules/<skill>.md` | `~/.vibe/rules/<skill>.md` | Plain markdown |
| `augment` | `.augment/rules/<skill>.md` | `~/.augment/rules/<skill>.md` | Plain markdown |
| `antigravity` | `.agents/rules/<skill>.md` | `~/.agents/rules/<skill>.md` | Plain markdown |
| `cline` | `.agents/rules/<skill>.md` | `~/.agents/rules/<skill>.md` | Plain markdown |
| `roo` | `.roo/rules/<skill>.md` | `~/.roo/rules/<skill>.md` | Plain markdown |
| `continue` | `.continue/rules/<skill>.md` | `~/.continue/rules/<skill>.md` | Plain markdown |
| `trae` | `.trae/rules/<skill>.md` | `~/.trae/rules/<skill>.md` | Plain markdown |
| `universal` | `.agents/rules/<skill>.md` | `~/.agents/rules/<skill>.md` | Plain markdown |

### Append

Skill content is inserted between HTML comment markers so re-runs update safely:

```html
<!-- skills-install:<skill>:begin -->
...
<!-- skills-install:<skill>:end -->
```

| Agent ID | Project file | Global file |
|----------|--------------|-------------|
| `github-copilot` | `.github/copilot-instructions.md` | `~/.copilot/copilot-instructions.md` |
| `opencode` | `AGENTS.md` | `~/.opencode/AGENTS.md` |
| `codex` | `AGENTS.md` | `~/.codex/AGENTS.md` |
| `gemini-cli` | `GEMINI.md` | `~/.gemini/GEMINI.md` |
| `aider` | `CONVENTIONS.md` | `~/.aider/CONVENTIONS.md` |
| `kilo-code` | `AGENTS.md` | `~/.config/kilo/AGENTS.md` |

**Windsurf global rules** are special: project installs use per-file `.windsurf/rules/`, but `-g --as-rule` appends to `~/.codeium/windsurf/memories/global_rules.md`.

---

## Auto-detection

When you omit `-a` / `--agent`, the installer detects tools on your machine:

| Signal | Agent ID |
|--------|----------|
| `~/.cursor` exists, or `cursor` on `PATH` | `cursor` |
| `~/.claude` exists, or `claude` on `PATH` | `claude-code` |
| `~/.config/opencode` exists, or `opencode` on `PATH` | `opencode` |
| `~/.codex` exists, or `codex` on `PATH` | `codex` |
| `~/.codeium/windsurf` exists, or `windsurf` on `PATH` | `windsurf` |
| `~/.copilot` exists | `github-copilot` |
| `~/.gemini` exists, or `gemini` on `PATH` | `gemini-cli` |
| `~/.openclaw` exists, or `openclaw` on `PATH` | `openclaw` |
| `~/.hermes` exists, or `hermes` on `PATH` | `hermes-agent` |
| `~/.vibe` exists, or `vibe` on `PATH` | `mistral-vibe` |
| `~/.aider` exists, or `aider` on `PATH` | `aider` |
| `~/.kilo` or `~/.kilocode` exists | `kilo-code` |
| `~/.augment` exists | `augment` |
| `~/.gemini/antigravity` or `~/.gemini/antigravity-cli` exists | `antigravity` |

If nothing is detected, the installer defaults to `cursor`, `claude-code`, and `opencode`.

Tools **not** auto-detected — pass the agent ID explicitly: `cline`, `roo`, `continue`, `trae`, `universal`.

---

## Per-tool details

Paths below are relative to the project root (or `~` for global installs with `-g`). After install, each skill appears as `<path>/<skill>/SKILL.md`.

### Cursor (`cursor`)

IDE with Agent chat, skills, and project rules.

```bash
python3 install.py -s docker -a cursor
python3 install.py -s test -a cursor --as-rule
```

Cursor also discovers skills in `.agents/skills/`, `.claude/skills/`, and `.codex/skills/` for compatibility.

Docs: [Skills](https://cursor.com/docs/context/skills) · [Rules](https://cursor.com/docs/context/rules)

---

### Claude Code (`claude-code`)

Anthropic's terminal-based coding agent.

```bash
python3 install.py --all -a claude-code
python3 install.py -s lint -a claude-code --as-rule -g -y
```

Claude walks parent directories and discovers nested `.claude/skills/` on demand.

Docs: [Skills](https://code.claude.com/docs/en/skills) · [Memory / rules](https://code.claude.com/docs/en/memory)

---

### OpenCode (`opencode`)

Open-source coding agent with a native `skill` tool.

```bash
python3 install.py -s docker -a opencode
python3 install.py -s test -a opencode --as-rule
```

Also reads `.claude/skills/` and `.agents/skills/` for compatibility.

Docs: [Skills](https://opencode.ai/docs/skills) · [Rules](https://opencode.ai/docs/rules)

---

### Codex (`codex`)

OpenAI's Codex CLI agent.

```bash
python3 install.py --all -a codex -g -y
python3 install.py -s lint -a codex --as-rule
```

Enable skills in `~/.codex/config.toml` if needed (`[features] skills = true`). Also scans `.agents/skills/` up the directory tree.

Docs: [Skills](https://developers.openai.com/codex/skills) · [Customization](https://developers.openai.com/codex/concepts/customization)

---

### Windsurf (`windsurf`)

Codeium's AI IDE (Cascade).

```bash
python3 install.py --all -a windsurf
python3 install.py -s test -a windsurf --as-rule -g -y
```

Project rules use `trigger: model_decision`. Global rules append to `~/.codeium/windsurf/memories/global_rules.md`.

---

### GitHub Copilot (`github-copilot`)

GitHub's AI pair programmer (IDE extensions and Copilot CLI).

```bash
python3 install.py -s docker -a github-copilot
python3 install.py -s lint -a github-copilot --as-rule
```

Rules append to `copilot-instructions.md` for always-on Copilot guidance.

---

### Gemini CLI (`gemini-cli`)

Google's Gemini command-line agent.

```bash
python3 install.py --all -a gemini-cli
python3 install.py -s test -a gemini-cli --as-rule
```

Rules append to `GEMINI.md` (project root or `~/.gemini/GEMINI.md`).

---

### OpenClaw (`openclaw`)

Open-source agent framework. **Project skills install to `skills/` at the repo root** (not under a dot-directory). OpenClaw also reads `/.agents/skills`, `~/.agents/skills`, and bundled skills with defined precedence — see [OpenClaw skills docs](https://docs.openclaw.ai/tools/skills).

```bash
python3 install.py -s docker -a openclaw
python3 install.py -s lint -a openclaw --as-rule
```

Global skills: `~/.openclaw/skills/`. Rules use the shared `.agents/rules/` convention.

---

### Hermes Agent (`hermes-agent`)

Agent with dedicated `.hermes/` configuration layout.

```bash
python3 install.py --all -a hermes-agent -g -y
python3 install.py -s test -a hermes-agent --as-rule
```

Detected via `~/.hermes` or the `hermes` command on `PATH`.

---

### Mistral Vibe (`mistral-vibe`)

Mistral's Vibe coding agent.

```bash
python3 install.py -s docker -a mistral-vibe
python3 install.py -s lint -a mistral-vibe --as-rule
```

Uses `.vibe/skills` and `.vibe/rules`. Detected via `~/.vibe` or the `vibe` command on `PATH`.

---

### Aider (`aider`)

Terminal pair-programming tool that edits git repos.

```bash
python3 install.py -s docker -a aider
python3 install.py -s lint -a aider --as-rule
```

Rules append to `CONVENTIONS.md` — Aider's file for persistent coding conventions.

Docs: [aider.chat](https://aider.chat)

---

### Kilo Code (`kilo-code`)

VS Code extension and agent platform.

```bash
python3 install.py -s docker -a kilo-code
python3 install.py -s test -a kilo-code --as-rule
```

Global rules go to `~/.config/kilo/AGENTS.md` (not `~/.kilo/`). Detected via `~/.kilo` or `~/.kilocode`.

---

### Augment Code (`augment`)

AI coding assistant with `.augment/` project layout.

```bash
python3 install.py --all -a augment -g -y
python3 install.py -s lint -a augment --as-rule
```

Detected via `~/.augment`.

---

### Google Antigravity (`antigravity`)

Google's Antigravity agent (Gemini ecosystem). Shares the `.agents/` skill and rule paths with Cline and Universal at the project level; global skills go to `~/.gemini/antigravity/skills`.

```bash
python3 install.py -s docker -a antigravity
python3 install.py -s test -a antigravity --as-rule
```

Detected via `~/.gemini/antigravity` or `~/.gemini/antigravity-cli`.

---

### Cline (`cline`)

VS Code extension for autonomous coding. Uses the [Agent Skills](https://agentskills.io/) `.agents/` convention.

```bash
python3 install.py --all -a cline
python3 install.py -s lint -a cline --as-rule
```

Not auto-detected — always pass `-a cline`.

---

### Roo Code (`roo`)

VS Code extension (fork/evolution of Cline). Tool-specific paths under `.roo/`.

```bash
python3 install.py -s docker -a roo
python3 install.py -s test -a roo --as-rule
```

Not auto-detected — always pass `-a roo`.

---

### Continue (`continue`)

Open-source IDE extension and CLI for custom agents.

```bash
python3 install.py --all -a continue
python3 install.py -s lint -a continue --as-rule
```

Tool-specific paths under `.continue/`. Not auto-detected.

Docs: [continue.dev](https://continue.dev)

---

### Trae (`trae`)

ByteDance's AI IDE. Tool-specific paths under `.trae/`.

```bash
python3 install.py -s docker -a trae
python3 install.py -s test -a trae --as-rule
```

Not auto-detected — always pass `-a trae`.

---

### Universal (`universal`)

Install target for the shared [Agent Skills](https://agentskills.io/) `.agents/` layout. Use when multiple tools in a repo should read the same skill and rule directories.

```bash
python3 install.py --all -a universal
python3 install.py -s lint -a universal --as-rule
```

| Scope | Skills | Rules |
|-------|--------|-------|
| Project | `.agents/skills/<skill>/` | `.agents/rules/<skill>.md` |
| Global | `~/.agents/skills/<skill>/` | `~/.agents/rules/<skill>.md` |

Several tools (Cline, Antigravity, OpenClaw rules, Codex, OpenCode) also read `.agents/skills/` for cross-tool compatibility.

---

## Shared conventions

### `.agents/` compatibility

Multiple tools read `.agents/skills/` in addition to their own paths:

- **Skills at `.agents/skills/`**: Codex, OpenCode, Cursor (compat), Cline, Antigravity, Universal
- **Rules at `.agents/rules/`**: OpenClaw, Antigravity, Cline, Universal

Use `-a universal` (or `-a cline` / `-a antigravity`) when you want one install location for several tools.

### Cross-reading between tools

| Tool | Also discovers |
|------|----------------|
| Cursor | `.agents/skills/`, `.claude/skills/`, `.codex/skills/` |
| OpenCode | `.claude/skills/`, `.agents/skills/` |
| Codex | `.agents/skills/` (walks up to repo root) |

---

## Verify installation

```bash
python3 install.py --list-agents          # print all paths
ls .cursor/skills/                        # project skills (Cursor example)
ls ~/.claude/skills/                        # global skills (Claude example)
grep skills-install AGENTS.md             # appended rules (OpenCode/Codex/Kilo)
grep skills-install CONVENTIONS.md        # appended rules (Aider)
ls .agents/skills/                          # universal / shared layout
```

Restart the coding tool or start a new session after installing.

---

## Related

- [Installer](installer.md) — `install.py` usage, env vars, security
- [USAGE.md](../../USAGE.md) — skills vs rules, update/remove, authoring tips
- [Agent Skills open standard](https://agentskills.io/)
