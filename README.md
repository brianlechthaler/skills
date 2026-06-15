# skills

Personal [Cursor Agent Skills](https://cursor.com/docs/context/skills) — reusable instructions that teach the agent specialized workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [docker](docker/SKILL.md) | Run all builds, tests, and tooling inside Docker containers. Nothing installed on the host except Docker. Credentials and SSH keys are mounted read-only from the host. |
| [github-publish](github-publish/SKILL.md) | Track changes in git, publish to public GitHub repos with `gh`, and open draft PRs with completed checklist items when work is done. |
| [github-workflows](github-workflows/SKILL.md) | Create GitHub Actions workflows for unit tests, linters, and container builds with GHCR publish. |
| [test](test/SKILL.md) | Enforce TDD and 100% test coverage on generated code before commits. |
| [lint](lint/SKILL.md) | Enforce linting and formatting before commits. |

## Installation

Install skills into Cursor, Claude Code, OpenCode, Codex, Windsurf, and other supported tools:

```bash
# From a clone of this repo
./install.sh --list
./install.sh --all                          # auto-detect installed tools
./install.sh --all -g -y                    # global install, no prompts
./install.sh -s docker -a cursor -a claude-code -a opencode

# One-liner (downloads and runs the installer)
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.sh | bash -s -- --all -y
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
| `-y, --yes` | Skip confirmation prompts |

By default the script symlinks skills from this repo so updates here are picked up immediately. Use `--copy` when installing globally without keeping a local clone.

Each skill is a directory containing a `SKILL.md` file. Cursor discovers skills from `~/.cursor/skills/` (personal) and `.cursor/skills/` (project).

## Adding a Skill

1. Create a directory named after the skill (lowercase, hyphens).
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.
3. Update this README with a row in the skills table.

See [Cursor's skill documentation](https://cursor.com/docs/context/skills) for authoring guidelines.

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
