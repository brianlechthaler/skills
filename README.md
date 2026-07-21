# skills

<!-- skill-count:47 -->
Portable [Agent Skills](https://agentskills.io/) for **any AI coding agent** — **47** reusable instruction bundles that teach agents specialized workflows.

These skills are **not Cursor-specific**. Each skill is a standard `SKILL.md` directory that works with Cursor, Claude Code, OpenCode, Codex, Windsurf, GitHub Copilot, and **14 other tools** supported by the installer. Install to one agent or many with a single command.

## Quick start

Requires Python 3.10+. See [Getting started](docs/getting-started.md) for full setup, verify, and uninstall steps.

```bash
python3 install.py --list
python3 install.py --all -y                    # auto-detect installed tools
python3 install.py -s docker -a cursor -a claude-code -y
```

Windows: use `python install.py` instead of `python3 install.py`.

One-liner without cloning:

```bash
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.py -o install.py
python3 install.py --all -y
```

## Documentation

- [Skills catalog](docs/features/skills-catalog.md) — all 47 skills by category
- [Getting started](docs/getting-started.md) — install, verify, uninstall
- [Installer](docs/features/installer.md) — `install.py` flags, flows, troubleshooting
- [Supported coding tools](docs/features/supported-tools.md) — 19 agents, paths, rule formats
- [Skill authoring](docs/features/skill-authoring.md) — add a new skill to this repo
- [Skill testing](docs/features/skill-testing.md) — CI validation and local test commands
- [Architecture](docs/architecture.md) — repository layout and install/uninstall flow
- [Documentation index](docs/index.md) — map of all project docs
- [USAGE.md](USAGE.md) — per-tool guide (skills vs rules, verify, update, remove)

## Requirements

- Python 3.10 or newer
- A supported AI coding tool (optional for browsing; required to use installed skills)

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
