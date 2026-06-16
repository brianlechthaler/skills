# skills

Personal [Cursor Agent Skills](https://cursor.com/docs/context/skills) — reusable instructions that teach the agent specialized workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [docker](docker/SKILL.md) | Run all builds, tests, and tooling inside Docker containers. Nothing installed on the host except Docker. Credentials and SSH keys are mounted read-only from the host. |
| [document-project](document-project/SKILL.md) | Document projects with a short README linked to `docs/`, per-feature docs, diagrams, and screenshots. |
| [github-publish](github-publish/SKILL.md) | Track changes in git, publish to public GitHub repos with `gh`, and open draft PRs with completed checklist items when work is done. |
| [github-workflows](github-workflows/SKILL.md) | Create GitHub Actions workflows for unit tests, linters, and container builds with GHCR publish. |
| [ci-optimize](ci-optimize/SKILL.md) | Aggressively optimize CI for fastest completion: baseline, iterate on caching, parallelization, and path filters until gains plateau. |
| [test](test/SKILL.md) | Enforce TDD and 100% test coverage on generated code before commits. |
| [lint](lint/SKILL.md) | Enforce linting and formatting before commits. |
| [browser-test](browser-test/SKILL.md) | Test web apps in the browser with real UI interaction and verification before marking UI work complete. |
| [mcp-security](mcp-security/SKILL.md) | Implement and harden MCP servers using NSA AISC security design considerations (CSI PP-26-1834). |
| [security-audit](security-audit/SKILL.md) | Perform aggressive full-surface security audits with optional auto-remediation of discovered vulnerabilities. |

## Installation

Install skills into Cursor, Claude Code, OpenCode, Codex, Windsurf, and other supported tools:

```bash
# From a clone of this repo
./install.sh --list
./install.sh --all                          # auto-detect installed tools
./install.sh --all -g -y                    # global install, no prompts
./install.sh -s docker -a cursor -a claude-code -a opencode

# Install as always-on / intelligently-applied rules instead of skills
./install.sh -s test -a cursor --as-rule
./install.sh --all -a claude-code -a windsurf --as-rule -g -y

# One-liner (downloads and runs the installer)
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.sh | bash -s -- --all -y
```

**Windows (PowerShell):**

```powershell
# From a clone of this repo
.\install.ps1 --list
.\install.ps1 --all -y
.\install.ps1 -s docker -a cursor -a claude-code
.\install.ps1 -s test -a cursor --as-rule

# Download and run
irm https://raw.githubusercontent.com/brianlechthaler/skills/main/install.ps1 -OutFile install.ps1
.\install.ps1 --all -y
```

Options:

| Flag | Description |
|------|-------------|
| `--list` | Show skills in this repo |
| `--list-agents` | Show supported tools and install paths |
| `-s, --skill NAME` | Install specific skill(s) |
| `--all` | Install every skill |
| `-a, --agent NAME` | Target tool (`cursor`, `claude-code`, `opencode`, `codex`, `windsurf`, … or `all`) |
| `-g, --global` | Install to user home dirs instead of the current project |
| `--copy` | Copy files instead of symlinking (default: symlink to this repo) |
| `--as-rule` | Install as AI rules instead of skills (Cursor `.mdc`, Claude `.claude/rules/`, Windsurf, `AGENTS.md`, etc.) |
| `-y, --yes` | Skip confirmation prompts |

By default the script symlinks skills from this repo so updates here are picked up immediately. Use `--copy` when installing globally without keeping a local clone.

Use `--as-rule` when a tool should load skill instructions as persistent rules instead of on-demand skills. Cursor rules are written as `.cursor/rules/<skill>.mdc` with intelligent activation; Claude Code uses `.claude/rules/<skill>.md`; Windsurf uses `.windsurf/rules/<skill>.md`; OpenCode and Codex append sections to `AGENTS.md`; and other agents use their documented rules directories (see `./install.sh --list-agents`). Re-running `--as-rule` updates existing rule sections safely.

Each skill is a directory containing a `SKILL.md` file. Cursor discovers skills from `~/.cursor/skills/` (personal) and `.cursor/skills/` (project).

## Usage

See **[USAGE.md](USAGE.md)** for a per-tool guide covering Cursor, Claude Code, OpenCode, Codex, Windsurf, GitHub Copilot, Gemini CLI, and more — including how to use skills vs rules (`--as-rule`), verify installs, and update or remove them.

## Adding a Skill

1. Create a directory named after the skill (lowercase, hyphens).
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.
3. Update this README with a row in the skills table.

See [Cursor's skill documentation](https://cursor.com/docs/context/skills) for authoring guidelines.

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
