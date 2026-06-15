# Using Skills and Rules

This repository ships reusable [Agent Skills](https://agentskills.io/) — portable instruction bundles that teach AI coding agents specialized workflows. The same `SKILL.md` files work across Cursor, Claude Code, OpenCode, Codex, Windsurf, and other tools that support the open standard.

Use the installer to drop skills into each tool's discovery path, or install them as **rules** when you want always-on or intelligently-applied guidance instead of on-demand loading.

## Quick start

```bash
# List skills and supported tools
./install.sh --list
./install.sh --list-agents

# Install all skills to auto-detected tools (project-local, symlinked)
./install.sh --all

# Install globally to your home directory
./install.sh --all -g -y

# Install specific skills to specific tools
./install.sh -s docker -s test -a cursor -a claude-code -a opencode

# Install as rules instead of skills
./install.sh -s test -a cursor --as-rule
./install.sh --all -a claude-code -a windsurf --as-rule -g -y
```

**Windows (PowerShell):** replace `./install.sh` with `.\install.ps1` — flags are the same.

**One-liner (no clone required):**

```bash
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.sh | bash -s -- --all -y
```

By default the installer **symlinks** skill directories to this repo so updates here are picked up immediately. Use `--copy` when you want standalone copies (recommended for global installs without keeping a local clone).

Run `./install.sh --list-agents` to see every supported tool and its install paths.

---

## What is a skill?

A skill is a directory containing a `SKILL.md` file:

```
docker/
├── SKILL.md          # required — frontmatter + instructions
├── examples.md       # optional
└── scripts/          # optional — executable helpers
```

Each `SKILL.md` starts with YAML frontmatter:

```markdown
---
name: docker
description: Run all builds, tests, and tooling inside Docker containers...
---

# Containerized Docker Workflow
...
```

Agents discover skills at startup (name + description only), then load the full body when a task matches the description. This **progressive disclosure** keeps context small while making many workflows available.

See [agentskills.io](https://agentskills.io/) for the open specification and [Cursor's skill docs](https://cursor.com/docs/context/skills) for authoring guidelines.

---

## Skills vs rules

| | Skills (default) | Rules (`--as-rule`) |
|---|---|---|
| **Loading** | On demand — agent reads `SKILL.md` when relevant | Always available or intelligently applied |
| **Context cost** | Low until triggered | Higher — rule metadata (or full text) is in scope sooner |
| **Best for** | Optional workflows (docker, publish, document) | Standards you always want enforced (lint, test, style) |
| **Install output** | Skill directories with `SKILL.md` | Tool-specific rule files or appended sections |
| **Update** | Edit `SKILL.md` in this repo (symlink picks up changes) | Re-run installer, or edit generated rule files directly |

**Use skills** when the agent should decide whether a workflow applies — for example, only run Docker commands when the user mentions containers.

**Use rules** when instructions should be persistent — for example, always run linters before commits, or always apply TDD when writing new code.

You can mix both: install `lint` and `test` as rules, and keep `docker` and `github-publish` as skills.

### How `--as-rule` converts skills

The installer reads each skill's `SKILL.md` and writes tool-specific rule files:

| Tool | Rule location | Format |
|------|---------------|--------|
| Cursor | `.cursor/rules/<skill>.mdc` | Frontmatter with `description`, `alwaysApply: false` |
| Claude Code | `.claude/rules/<skill>.md` | Frontmatter + body |
| Windsurf | `.windsurf/rules/<skill>.md` | `trigger: model_decision`, `description` |
| GitHub Copilot | `.github/copilot-instructions.md` | Appended section |
| OpenCode | `AGENTS.md` | Appended section |
| Codex | `AGENTS.md` | Appended section |
| Gemini CLI | `GEMINI.md` | Appended section |
| Cline / Roo / Continue / Trae / Universal | `.agents/rules/<skill>.md` | Plain markdown per file |

Global paths mirror project paths under your home directory (see `./install.sh --list-agents`).

**Append mode** (Copilot, OpenCode, Codex, Gemini) wraps each skill in HTML comment markers so re-running the installer updates safely:

```html
<!-- skills-install:test:begin -->
# Test
> Enforce TDD and 100% test coverage...
...
<!-- skills-install:test:end -->
```

**Per-file mode** (Cursor, Claude, Windsurf, Cline, etc.) writes one file per skill. Re-running `--as-rule` overwrites each file.

Windsurf global rules are written to `~/.codeium/windsurf/memories/global_rules.md`.

---

## Per-tool guide

### Cursor

**Skills**

| Scope | Path |
|-------|------|
| Project | `.cursor/skills/<skill>/SKILL.md` |
| Global | `~/.cursor/skills/<skill>/SKILL.md` |

Cursor also discovers skills in `.agents/skills/`, `.claude/skills/`, and `.codex/skills/` for compatibility.

**Install:**

```bash
./install.sh -s docker -a cursor          # skills
./install.sh -s test -a cursor --as-rule  # rules
```

**Using skills**

- The agent applies skills automatically when your request matches the skill description.
- Type `/` in Agent chat and search for the skill name to invoke one explicitly.
- View discovered skills: **Settings → Rules → Agent Decides**.

**Using rules** (`--as-rule`)

Rules are written to `.cursor/rules/<skill>.mdc` with `alwaysApply: false` and a description from the skill frontmatter. Cursor applies them intelligently when relevant — similar to "Apply Intelligently" project rules.

View and manage rules in **Settings → Rules**.

**Verify:** check that `.cursor/skills/` or `.cursor/rules/` contains the expected files after install.

Docs: [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills)

---

### Claude Code

**Skills**

| Scope | Path |
|-------|------|
| Project | `.claude/skills/<skill>/SKILL.md` |
| Global | `~/.claude/skills/<skill>/SKILL.md` |

Claude walks parent directories up to the repo root and discovers nested `.claude/skills/` on demand.

**Install:**

```bash
./install.sh --all -a claude-code
./install.sh -s lint -a claude-code --as-rule -g -y
```

**Using skills**

- Claude loads skill metadata at session start and invokes matching skills based on your prompt.
- Edits to existing skills take effect within the session; creating a new top-level skills directory may require restarting Claude Code.

**Using rules** (`--as-rule`)

Rules land in `.claude/rules/<skill>.md`. Claude Code treats these as project rules that apply alongside `CLAUDE.md`.

**Verify:** `ls .claude/skills/*/SKILL.md` or `ls .claude/rules/`

Docs: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

---

### OpenCode

**Skills**

| Scope | Path |
|-------|------|
| Project | `.opencode/skills/<skill>/SKILL.md` |
| Global | `~/.config/opencode/skills/<skill>/SKILL.md` |

OpenCode also reads `.claude/skills/` and `.agents/skills/` for compatibility.

**Install:**

```bash
./install.sh -s docker -a opencode
./install.sh -s test -a opencode --as-rule
```

**Using skills**

- OpenCode lists available skills in its native `skill` tool.
- The agent loads a skill on demand when a task matches or when you ask for it.
- Control access with pattern-based permissions in `opencode.json`.

**Using rules** (`--as-rule`)

Skill content is appended to `AGENTS.md` (project root or `~/.opencode/AGENTS.md`). `AGENTS.md` provides always-on project context — distinct from on-demand skills.

**Verify:** check `.opencode/skills/` or look for `<!-- skills-install:` markers in `AGENTS.md`.

Docs: [opencode.ai/docs/skills](https://opencode.ai/docs/skills)

---

### Codex

**Skills**

| Scope | Path |
|-------|------|
| Project | `.codex/skills/<skill>/SKILL.md` |
| Global | `~/.codex/skills/<skill>/SKILL.md` |

Codex also scans `.agents/skills/` up the directory tree to the repo root.

**Install:**

```bash
./install.sh --all -a codex -g -y
./install.sh -s lint -a codex --as-rule
```

**Using skills**

- Enable skills in `~/.codex/config.toml` if needed:

  ```toml
  [features]
  skills = true
  ```

- Mention a skill explicitly with `$skill-name` in the CLI, or browse with `/skills`.
- Codex also invokes skills implicitly when your prompt matches the description.

**Using rules** (`--as-rule`)

Skill content is appended to `AGENTS.md` (project root or `~/.codex/AGENTS.md`). Use `AGENTS.md` for persistent guidance; use skills for reusable workflows loaded on demand.

**Verify:** `ls ~/.codex/skills/*/SKILL.md` or inspect `AGENTS.md` for install markers.

Docs: [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)

---

### Windsurf

**Skills**

| Scope | Path |
|-------|------|
| Project | `.windsurf/skills/<skill>/SKILL.md` |
| Global | `~/.codeium/windsurf/skills/<skill>/SKILL.md` |

**Install:**

```bash
./install.sh --all -a windsurf
./install.sh -s test -a windsurf --as-rule -g -y
```

**Using skills**

- Windsurf discovers skills from its skills directory and loads them when relevant.

**Using rules** (`--as-rule`)

Project rules: `.windsurf/rules/<skill>.md` with `trigger: model_decision`.

Global rules: appended to `~/.codeium/windsurf/memories/global_rules.md`.

**Verify:** check `.windsurf/skills/` or `.windsurf/rules/`.

---

### GitHub Copilot

**Skills**

| Scope | Path |
|-------|------|
| Project | `.github/skills/<skill>/SKILL.md` |
| Global | `~/.copilot/skills/<skill>/SKILL.md` |

**Install:**

```bash
./install.sh -s docker -a github-copilot
./install.sh -s lint -a github-copilot --as-rule
```

**Using skills**

- Copilot discovers skills from `.github/skills/` and loads them on demand.

**Using rules** (`--as-rule`)

Skill content is appended to `.github/copilot-instructions.md` (or `~/.copilot/copilot-instructions.md` globally). This file provides always-on instructions to Copilot.

**Verify:** check `.github/skills/` or search for `<!-- skills-install:` in `copilot-instructions.md`.

---

### Gemini CLI

**Skills**

| Scope | Path |
|-------|------|
| Project | `.gemini/skills/<skill>/SKILL.md` |
| Global | `~/.gemini/skills/<skill>/SKILL.md` |

**Install:**

```bash
./install.sh --all -a gemini-cli
./install.sh -s test -a gemini-cli --as-rule
```

**Using rules** (`--as-rule`)

Skill content is appended to `GEMINI.md` (project root or `~/.gemini/GEMINI.md`).

---

### Cline, Roo, Continue, Trae, and Universal

These tools share the `.agents/` convention:

**Skills**

| Scope | Path |
|-------|------|
| Project | `.agents/skills/<skill>/SKILL.md` |
| Global | `~/.agents/skills/<skill>/SKILL.md` |

Tool-specific paths also exist (`.roo/skills/`, `.continue/skills/`, `.trae/skills/`). Use `./install.sh --list-agents` for the full list.

**Install:**

```bash
./install.sh --all -a cline
./install.sh -s docker -a roo -a continue
./install.sh -s lint -a universal --as-rule
```

**Using rules** (`--as-rule`)

Per-file rules in `.agents/rules/<skill>.md` (or the tool-specific rules directory).

The `universal` agent target installs to `.agents/skills` and `.agents/rules` — useful when you want one location that multiple tools can read.

---

## Manual installation

You do not need the installer if you prefer to copy files yourself.

**Skills** — symlink or copy a skill directory:

```bash
# Project-local (Cursor example)
ln -s "$(pwd)/docker" .cursor/skills/docker

# Global (Claude Code example)
ln -s "$(pwd)/test" ~/.claude/skills/test
```

**Rules** — run the installer with `--as-rule`, or create the rule file manually using the formats described in [Skills vs rules](#skills-vs-rules).

---

## Updating and removing

### Skills (symlinked)

Edit `SKILL.md` in this repo — changes are live immediately for symlinked installs.

To remove:

```bash
rm .cursor/skills/docker          # remove symlink
rm -rf ~/.claude/skills/docker    # remove global install
```

### Skills (copied)

Re-run the installer with `--copy` to refresh, or delete the copied directory and reinstall.

### Rules (per-file)

Re-run with `--as-rule` to overwrite:

```bash
./install.sh -s test -a cursor --as-rule
```

To remove, delete the rule file:

```bash
rm .cursor/rules/test.mdc
rm .claude/rules/test.md
```

### Rules (append mode)

Re-run with `--as-rule` to update the marked section in place.

To remove manually, delete the block between the HTML comment markers in `AGENTS.md`, `GEMINI.md`, or `copilot-instructions.md`:

```html
<!-- skills-install:test:begin -->
... delete this entire block ...
<!-- skills-install:test:end -->
```

---

## Tips

**Write good descriptions.** The `description` field in frontmatter is how agents decide when to load a skill. Include concrete trigger phrases ("Use when building, testing, or when the user mentions Docker") rather than vague summaries.

**Project vs global.**

- **Project** (default): skills travel with the repo via git — great for team standards.
- **Global** (`-g`): skills apply to every project on your machine — great for personal preferences.

**Symlink vs copy.**

- **Symlink** (default): one source of truth in this repo; `git pull` updates all linked tools.
- **Copy** (`--copy`): standalone files; use when you do not keep a local clone.

**Mix skills and rules.** Install enforcement skills (`lint`, `test`) as rules and workflow skills (`docker`, `github-publish`, `document-project`) as on-demand skills.

**Verify after install.**

```bash
./install.sh --list-agents    # confirm paths
ls .cursor/skills/            # project skills
ls ~/.claude/skills/          # global skills
grep skills-install AGENTS.md # appended rules
```

---

## Official documentation

| Tool | Skills | Rules / context |
|------|--------|-----------------|
| Agent Skills (open standard) | [agentskills.io](https://agentskills.io/) | — |
| Cursor | [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills) | [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules) |
| Claude Code | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) | [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) |
| OpenCode | [opencode.ai/docs/skills](https://opencode.ai/docs/skills) | [opencode.ai/docs/rules](https://opencode.ai/docs/rules) |
| Codex | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) | [developers.openai.com/codex/concepts/customization](https://developers.openai.com/codex/concepts/customization) |
