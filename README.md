# skills

Personal [Cursor Agent Skills](https://cursor.com/docs/context/skills) — reusable instructions that teach the agent specialized workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [docker](docker/SKILL.md) | Run all builds, tests, and tooling inside Docker containers. Nothing installed on the host except Docker. Credentials and SSH keys are mounted read-only from the host. |

## Installation

Copy a skill into your Cursor skills directory:

```bash
# Personal (available in all projects)
mkdir -p ~/.cursor/skills
cp -r docker ~/.cursor/skills/

# Or per-project
mkdir -p .cursor/skills
cp -r docker .cursor/skills/
```

Each skill is a directory containing a `SKILL.md` file. Cursor discovers skills from `~/.cursor/skills/` (personal) and `.cursor/skills/` (project).

## Adding a Skill

1. Create a directory named after the skill (lowercase, hyphens).
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.
3. Update this README with a row in the skills table.

See [Cursor's skill documentation](https://cursor.com/docs/context/skills) for authoring guidelines.

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
