# Documentation

Map of project documentation for the skills repository.

## Agent-agnostic by design

Skills in this repo follow the [Agent Skills open standard](https://agentskills.io/) — they are **not exclusive to Cursor** or any single product. The same `SKILL.md` files work across **19 AI coding agents**. Use `install.py` to install into any supported agent in one command (`-a <agent-id>`), or omit `-a` to auto-detect tools on your machine. See [Supported coding tools](features/supported-tools.md) for the full agent list and install paths.

## Start here

| Doc | Description |
|-----|-------------|
| [Getting started](getting-started.md) | Install, verify, and uninstall skills |
| [Skills catalog](features/skills-catalog.md) | All skills by category |
| [README.md](../README.md) | Quick start and documentation links |
| [USAGE.md](../USAGE.md) | Per-tool guide: skills vs rules, paths, tips |

## Features

| Doc | Description |
|-----|-------------|
| [Skills catalog](features/skills-catalog.md) | All 47 skills by category with links to each SKILL.md |
| [Skill authoring](features/skill-authoring.md) | Add a new skill to this repository |
| [Installer](features/installer.md) | `install.py` install/uninstall, flags, flows, troubleshooting |
| [Supported coding tools](features/supported-tools.md) | 19 tools, agent IDs, paths, auto-detection, rule formats |
| [Skill testing](features/skill-testing.md) | Automated validation in CI and local test commands |

## Architecture

| Doc | Description |
|-----|-------------|
| [Architecture](architecture.md) | Repository layout and how install/uninstall works |

## External references

- [Agent Skills open standard](https://agentskills.io/) — portable skill format used by this repo (primary reference)
- [Cursor skills docs](https://cursor.com/docs/context/skills) — one of many supported agents
- [Claude Code skills](https://code.claude.com/docs/en/skills) · [OpenCode skills](https://opencode.ai/docs/skills) · [Codex skills](https://developers.openai.com/codex/skills)
