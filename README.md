# skills

<!-- skill-count:31 -->
Personal [Cursor Agent Skills](https://cursor.com/docs/context/skills) — **31** reusable instructions that teach the agent specialized workflows.

## Skills (31)

### DevOps & CI (6)

| Skill | Description |
|-------|-------------|
| [docker](docker/SKILL.md) | Run all builds, tests, and tooling inside Docker containers. Nothing installed on the host except Docker. Credentials and SSH keys are mounted read-only from the host. |
| [compose-deploy](compose-deploy/SKILL.md) | Generate a Docker Compose deployment by detecting the project stack and backing services (Postgres, Redis, etc.). Creates compose.yaml, Dockerfiles, and .env.example. |
| [github-workflows](github-workflows/SKILL.md) | Create GitHub Actions workflows for unit tests, linters, and container builds with GHCR publish. |
| [ci-optimize](ci-optimize/SKILL.md) | Aggressively optimize CI for fastest completion: baseline, iterate on caching, parallelization, and path filters until gains plateau. |
| [ci-debug](ci-debug/SKILL.md) | Debug GitHub Actions failures — fetch logs, classify errors, reproduce locally, and optionally fix the underlying issue. |
| [dependabot-merge](dependabot-merge/SKILL.md) | Find open Dependabot PRs, verify updates are safe, fix code for new dependency versions, and merge when tests and CI pass. |

### GitHub (3)

| Skill | Description |
|-------|-------------|
| [github-publish](github-publish/SKILL.md) | Track changes in git, publish to public GitHub repos with `gh`, and open draft PRs with completed checklist items when work is done. |
| [github-issues](github-issues/SKILL.md) | Triage open GitHub issues, implement one fix per issue with its own draft PR, comment on progress, and close issues when work is complete. |
| [github-release](github-release/SKILL.md) | Create GitHub releases from the default branch with SemVer tags, Keep a Changelog-style notes, and project-specific deploy instructions. |

### Documentation (2)

| Skill | Description |
|-------|-------------|
| [document-project](document-project/SKILL.md) | Document projects with a short README linked to `docs/`, per-feature docs, diagrams, and screenshots. |
| [document-screenshots](document-screenshots/SKILL.md) | Capture browser screenshots of the running project and embed them in `docs/images/` for documentation. |

### Testing & Quality (4)

| Skill | Description |
|-------|-------------|
| [test](test/SKILL.md) | Enforce TDD and 100% test coverage on generated code before commits. |
| [lint](lint/SKILL.md) | Enforce linting and formatting before commits. |
| [browser-test](browser-test/SKILL.md) | Test web apps in the browser with real UI interaction and verification before marking UI work complete. |
| [playwright-test](playwright-test/SKILL.md) | Test web apps with Playwright for scripted browser verification, smoke checks, and E2E flows. |

### Performance (4)

| Skill | Description |
|-------|-------------|
| [web-performance](web-performance/SKILL.md) | Analyze web app performance across Core Web Vitals, bundles, network, and backend latency; recommend and optionally implement optimizations. |
| [compiled-performance](compiled-performance/SKILL.md) | Profile compiled/native applications, analyze CPU/memory/I/O bottlenecks, recommend optimizations, and optionally implement fixes with measured before/after gains. |
| [interpreted-performance](interpreted-performance/SKILL.md) | Profile Python, Node.js, Ruby, PHP, and other interpreted runtimes; analyze CPU, memory, I/O, and GC bottlenecks; recommend optimizations; optionally implement fixes with measured gains. |
| [valgrind-memcheck](valgrind-memcheck/SKILL.md) | Run Valgrind Memcheck on C/C++ binaries to detect memory leaks and heap errors, report findings in detail, and offer fixes. |

### Security (3)

| Skill | Description |
|-------|-------------|
| [security-audit](security-audit/SKILL.md) | Perform aggressive full-surface security audits with optional auto-remediation of discovered vulnerabilities. |
| [mcp-security](mcp-security/SKILL.md) | Implement and harden MCP servers using NSA AISC security design considerations (CSI PP-26-1834). |
| [prompt-security](prompt-security/SKILL.md) | Harden system prompts against leakage, injection, and override — non-disclosure, instruction hierarchy, and red-team review. |

### MCP & Integrations (4)

| Skill | Description |
|-------|-------------|
| [add-mcp-server](add-mcp-server/SKILL.md) | Add a project-local MCP server so agents can interact with databases, APIs, and other project resources. |
| [codebase-memory](codebase-memory/SKILL.md) | Explore codebases through a knowledge-graph MCP — search, trace, and fetch snippets instead of reading whole files. |
| [headroom](headroom/SKILL.md) | Compress large tool outputs and file contents via Headroom MCP to cut context tokens while keeping reversible retrieval. |
| [llmfit](llmfit/SKILL.md) | Pick the best local LLM for the user's hardware with llmfit — detect specs, score fit/speed/quality, and recommend runnable models. |

### Context & Efficiency (4)

| Skill | Description |
|-------|-------------|
| [terse](terse/SKILL.md) | Minimize tokens in user-facing prose — fewest words needed for status, results, and next steps. |
| [prompt-conciseness](prompt-conciseness/SKILL.md) | Shorten system prompts and agent instructions to save tokens while preserving every critical policy and capability. |
| [simple-code](simple-code/SKILL.md) | Write the simplest possible code with the fewest lines — no redundant logic, abstractions, or helpers. |
| [toonify](toonify/SKILL.md) | Serialize structured data as TOON instead of JSON to cut prompt tokens 30–60% with lossless encode/decode and schema templates. |

### Orchestration (1)

| Skill | Description |
|-------|-------------|
| [orchestrate](orchestrate/SKILL.md) | Plan comprehensively and run subagents in parallel by phase, respecting dependencies and avoiding race conditions. |

## Installation

Install skills into Cursor, Claude Code, OpenCode, Codex, Windsurf, and other supported tools with the cross-platform Python installer ([details](docs/features/installer.md)):

```bash
# From a clone of this repo (requires Python 3.10+)
python3 install.py --list
python3 install.py --all                          # auto-detect installed tools
python3 install.py --all -g -y                    # global install, no prompts
python3 install.py -s docker -a cursor -a claude-code -a opencode

# Install as always-on / intelligently-applied rules instead of skills
python3 install.py -s test -a cursor --as-rule
python3 install.py --all -a claude-code -a windsurf --as-rule -g -y

# One-liner (downloads and runs the installer)
curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.py -o install.py
python3 install.py --all -y
```

**Windows:** use `python install.py` instead of `python3 install.py` — flags are the same.

Options:

| Flag | Description |
|------|-------------|
| `--list` | Show skills in this repo |
| `--list-by-category` | Show skills grouped by high-level category |
| `--list-agents` | Show supported tools and install paths |
| `-s, --skill NAME` | Install specific skill(s) |
| `--all` | Install every skill |
| `-a, --agent NAME` | Target tool (`cursor`, `claude-code`, `opencode`, `codex`, `windsurf`, … or `all`) |
| `-g, --global` | Install to user home dirs instead of the current project |
| `--copy` | Copy files instead of symlinking (default: symlink to this repo) |
| `--as-rule` | Install as AI rules instead of skills (Cursor `.mdc`, Claude `.claude/rules/`, Windsurf, `AGENTS.md`, etc.) |
| `-y, --yes` | Skip confirmation prompts |

By default the script symlinks skills from this repo so updates here are picked up immediately. Use `--copy` when installing globally without keeping a local clone.

Use `--as-rule` when a tool should load skill instructions as persistent rules instead of on-demand skills. Cursor rules are written as `.cursor/rules/<skill>.mdc` with intelligent activation; Claude Code uses `.claude/rules/<skill>.md`; Windsurf uses `.windsurf/rules/<skill>.md`; OpenCode and Codex append sections to `AGENTS.md`; and other agents use their documented rules directories (see `python3 install.py --list-agents`). Re-running `--as-rule` updates existing rule sections safely.

Each skill is a directory containing a `SKILL.md` file. Cursor discovers skills from `~/.cursor/skills/` (personal) and `.cursor/skills/` (project).

## Documentation

- [Supported coding tools](docs/features/supported-tools.md) — all 19 tools, install paths, auto-detection, and rule formats
- [Getting started](docs/features/installer.md) — install skills on macOS, Windows, and Linux
- [USAGE.md](USAGE.md) — per-tool guide (skills vs rules, verify, update, remove)

## Adding a Skill

1. Create a directory named after the skill (lowercase, hyphens).
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.
3. Add the skill to `skill_categories.py` under the appropriate high-level category.
4. Update this README with a row in the matching category table. The skill count in the intro and `## Skills (N)` heading is synced automatically on merge to `main`; run `python scripts/sync_readme_skill_count.py` locally if you want to update it in your branch.

See [Cursor's skill documentation](https://cursor.com/docs/context/skills) for authoring guidelines.

## License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE).
