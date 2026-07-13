# Getting started

Install reusable [Agent Skills](https://agentskills.io/) from this repository into **any supported AI coding agent** — not just Cursor. The installer targets 19 tools (Cursor, Claude Code, OpenCode, Codex, Windsurf, GitHub Copilot, and more). Pick your agent with `-a <agent-id>`, or omit `-a` to auto-detect installed tools.

```bash
python3 install.py --list-agents   # see every supported agent and install path
```

## Requirements

- Python 3.10 or newer (`python3 --version`)
- A supported AI coding tool (see [supported tools](features/supported-tools.md))

On Windows, use `python` instead of `python3` in the examples below.

## Option A: Clone this repo

```bash
git clone https://github.com/brianlechthaler/skills.git
cd skills
python3 install.py --list
python3 install.py --all -y
```

By default the installer **symlinks** skill directories into each tool's discovery path. Edits to `SKILL.md` in this repo are picked up immediately.

## Option B: One-liner (no clone)

```bash
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.py -o install.py
python3 install.py --all -y
```

Remote installs copy skill files (symlinks would not survive outside a clone).

## Install specific skills or tools

```bash
# One skill, one tool
python3 install.py -s docker -a cursor -y

# Multiple skills and tools
python3 install.py -s docker -s test -a cursor -a claude-code -y

# Global install (applies to every project on this machine)
python3 install.py --all -g -y

# Install as always-on rules instead of on-demand skills
python3 install.py -s lint -s test -a cursor --as-rule -y
```

Omit `-a` to auto-detect tools on your machine. Run `python3 install.py --list-agents` to see all agent IDs and install paths.

## Verify

```bash
python3 install.py --list-agents
ls .cursor/skills/                  # project skills (Cursor example)
ls ~/.claude/skills/                # global skills (Claude example)
grep skills-install AGENTS.md       # appended rules (OpenCode/Codex)
```

Restart the coding tool or start a new session after installing.

## Uninstall

Remove skills or rules installed by `install.py`:

```bash
# Remove one skill from one tool
python3 install.py --uninstall -s docker -a cursor -y

# Remove multiple skills from multiple tools
python3 install.py --uninstall -s docker -s test -a cursor -a claude-code -y

# Remove every skill from this repo (global Cursor install)
python3 install.py --uninstall --all -a cursor -g -y

# Remove rules installed with --as-rule
python3 install.py --uninstall -s test -a cursor --as-rule -y
```

Match the flags you used at install time:

- `-g` for global installs
- `--as-rule` for rule-based installs
- `-a` to target specific tools (auto-detect when omitted)

See [Installer — Uninstall](features/installer.md#uninstall) for behavior details, safety checks, and troubleshooting.

## Next steps

- [USAGE.md](../USAGE.md) — skills vs rules, per-tool paths, manual install/remove
- [Supported coding tools](features/supported-tools.md) — all 19 tools with paths and examples
- [Skill testing](features/skill-testing.md) — how skills are validated in CI
- [README.md](../README.md) — full skill catalog

## Authoring a skill

1. Create `<skill>/SKILL.md` with YAML frontmatter (`name`, `description`).
2. Add the skill to `skill_categories.py`.
3. Add a row to the matching category table in `README.md`.
4. Run `pytest tests/test_skills.py` to validate.

See the [Agent Skills specification](https://agentskills.io/) for the portable format, your agent's docs (listed in [Supported coding tools](features/supported-tools.md)), and the [document-project](../document-project/SKILL.md) skill for documentation conventions.
