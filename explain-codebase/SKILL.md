---
name: explain-codebase
description: >-
  Produce a structured, in-depth explanation of a codebase by exploring
  architecture, entry points, data flow, dependencies, and conventions. Use when
  onboarding to a new project, reviewing unfamiliar code, preparing a handoff, or
  when the user asks for a codebase walkthrough, deep explanation, or
  architecture overview.
---

# Explain Codebase

Map a codebase from surface to depth and present a coherent explanation of how it works, why it is shaped the way it is, and where the risks and extension points live. This skill is a manual, file-by-file exploration; for very large repositories, consider using [codebase-memory](../codebase-memory/SKILL.md) to search a pre-indexed graph before reading broadly.

## When This Applies

| Use explain-codebase | Skip explain-codebase |
|----------------------|-----------------------|
| Onboarding to a new repo or returning after a long gap | Trivial one-line lookup in a known file |
| Architecture review or handoff documentation | The user only wants a specific function or error fixed |
| Understanding a feature's end-to-end flow | A codebase-memory MCP index is already available and sufficient |
| Preparing to refactor, migrate, or extend a subsystem | The repo is empty, generated, or a README-only scaffold |
| User asks for a "deep dive", "walkthrough", or "explain this codebase" | The user explicitly asked for a quick summary only |

When the goal is comprehension rather than editing, default to this skill before planning changes.

## Core Rules

1. **Read before explaining.** Never synthesize from assumptions; cite the files, symbols, or commands that support each claim.
2. **Layer the explanation.** Start with purpose and shape, then move to entry points, data flow, dependencies, and finally conventions and risks.
3. **Show, don't just tell.** Use directory trees, module names, and function signatures as evidence in the explanation.
4. **Stay proportional.** Match the depth of the explanation to the size and complexity of the codebase; do not over-analyze a single-file script.
5. **Cross-reference, don't repeat.** Link to related skills for specialized concerns (tests, performance, security) rather than duplicating their workflows.

## Workflow

Copy and track progress:

```
Explain codebase progress:
- [ ] Scope and target audience defined
- [ ] Surface inventory (README, config, top-level structure)
- [ ] Architecture map (layers, modules, boundaries)
- [ ] Entry points identified (CLI, server, API, jobs, UI)
- [ ] Data flow traced (request, job, event, or render path)
- [ ] Dependencies catalogued (internal, external, env)
- [ ] Conventions and risks surfaced (patterns, tests, docs, hotspots)
- [ ] Synthesis written and presented at chosen depth
```

### Step 1 — Scope the explanation

Before reading files, decide:

| Question | Why it matters |
|----------|----------------|
| What is the codebase's purpose? | Anchors every later observation. |
| Who is the audience? | Affects depth and terminology (new hire vs. peer reviewer). |
| What subsystem or feature matters most? | Prevents getting lost in unrelated files. |
| What is the desired depth? | Surface overview, deep architecture, or single-feature trace. |
| What is out of scope? | Avoids rabbit holes and scope creep. |

If the user only says "explain this codebase", start with a broad overview and ask where they want to go deeper.

### Step 2 — Surface inventory

Read the high-level signals first:

- `README.md` or `README` — purpose, quickstart, high-level architecture
- `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml` — language, dependencies, scripts
- `Dockerfile`, `compose.yaml`, `Makefile`, `Taskfile` — runtime and build plumbing
- Top-level directories — map the layout at a glance
- `docs/` or `wiki/` — existing design records
- `.github/workflows/` — CI/CD signals about quality gates and deploy flow

Summarize the project type, primary language, and rough size in one sentence before opening deeper files.

### Step 3 — Map architecture

Identify the major layers and how they relate:

| Layer | What to look for | Typical artifacts |
|-------|------------------|-------------------|
| Presentation / CLI | User-facing entry points | `src/main.py`, `app/cli.py`, `src/routes/`, `src/App.tsx` |
| Application / service | Business logic coordinators | `services/`, `handlers/`, `usecases/`, `controllers/` |
| Domain / core | Entities and invariants | `models/`, `domain/`, `entities/`, `core/` |
| Data / infrastructure | Persistence, I/O, external clients | `repositories/`, `db/`, `clients/`, `adapters/`, `infra/` |
| Cross-cutting | Logging, auth, config, telemetry | `middleware/`, `lib/`, `config/`, `utils/` (with caution) |

Draw a simple layer diagram or bullet list. Call out which directories are thin vs. thick, and where the boundary rules are enforced.

### Step 4 — Find entry points

List the concrete places the system starts doing work:

- **CLI** — main command, subcommands, argument parsing, exit codes
- **Server / API** — framework, route registration, middleware stack, port/host
- **Background jobs** — workers, schedulers, queue consumers, cron
- **UI / frontend** — root component, router, state initialization
- **Library** — public API surface, exported functions/classes
- **Tests** — how the system is exercised; often reveal intended behavior

For each entry point, give a one-line summary and the primary file or function name.

### Step 5 — Trace a representative data flow

Pick one path that exercises the most important layers:

1. Start at an entry point (e.g., a route or CLI command).
2. Follow the call chain through services, domain logic, and data access.
3. Note transformations, side effects, and external calls.
4. Identify return paths, error handling, and event publishing.
5. Name the files and functions involved so the reader can retrace.

Choose a happy path first; mention the most common error or retry path only if it significantly shapes the architecture.

### Step 6 — Catalogue dependencies

| Category | What to capture | Example signals |
|----------|-----------------|-----------------|
| Runtime language / framework | Version and ecosystem | `python 3.12`, `fastapi 0.110`, `react 18` |
| External services | Databases, queues, caches, APIs | Postgres, Redis, SQS, Stripe, OpenAI |
| Internal packages / modules | Shared libraries, monorepo packages | `packages/shared`, `internal/auth` |
| Build / dev tools | Lint, test, format, bundlers | ruff, pytest, jest, esbuild |
| Environment | Secrets, feature flags, infra | `.env.example`, `config.yaml`, Terraform |

Flag dependencies that are unusual, deprecated, or require special credentials.

### Step 7 — Surface conventions and risks

| Topic | What to look for | Common output |
|-------|------------------|---------------|
| Code style | Lint, format, type rules | ruff, black, mypy, eslint |
| Testing | Coverage, fixture patterns, test types | pytest, jest, integration tests in `tests/integration/` |
| Documentation | ADRs, READMEs, inline docs | `docs/adr/`, `CONTRIBUTING.md`, docstrings |
| Error handling | Exceptions, result types, logging | custom exceptions, `logger.exception`, sentry |
| Security hotspots | Auth, secrets, input validation | middleware, sanitizer, env loading |
| Complexity hotspots | Large files, deep inheritance, cyclic imports | files with >500 lines, `import` cycles |
| Tech debt | TODOs, FIXMEs, deprecated APIs | comments, deprecation warnings, pinned old versions |

Present risks as concrete observations tied to specific files or patterns, not as vague warnings.

### Step 8 — Synthesize

Choose an output shape matching the audience and scope:

**Overview (1–2 paragraphs)**
- Purpose, tech stack, primary entry point, and one-sentence architecture summary.

**Architecture summary (bullets + diagram)**
- Layers, major modules, boundaries, and key data flow.

**Deep dive (sections)**
- Each layer or feature in its own subsection with file references and code snippets.

**Handoff report (document)**
- Overview, architecture, data flow, dependencies, conventions, risks, and recommended next steps.

Always include:
- A directory tree or module list for orientation.
- The chosen data flow path with file names and function names.
- A list of the 3–5 most important files to read next.
- Any caveats about incomplete understanding or hidden configuration.

## Commands

These commands are illustrative; adapt to the project's language and tooling.

```bash
# Surface inventory
ls -la
python3 install.py --list          # if this is a skills repo
cat README.md
cat pyproject.toml || cat package.json || cat go.mod

# Architecture and entry points
find src -type d -maxdepth 2 | sort
grep -R "def main" --include="*.py" .
grep -R "@app.route\|@router" --include="*.py" .
grep -R "fastapi\|flask\|django" --include="*.py" .

# Dependency signals
pip show <package> || npm list <package> || go list -m all
cat requirements*.txt || cat package-lock.json | head -n 50

# Testing and conventions
python3 -m pytest --collect-only       # list tests
python3 -m ruff check .               # lint signals
find . -name "*.md" -not -path "./node_modules/*" | head -n 20
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Guessing what a file does without reading it | Open the file and quote the docstring or first 50 lines |
| Dumping every directory and file without structure | Group observations into layers and flows |
| Explaining only the happy path | Call out error handling, retries, and edge cases when they shape the design |
| Repeating specialized guidance from [test](../test/SKILL.md), [security-audit](../security-audit/SKILL.md), or [interpreted-performance](../interpreted-performance/SKILL.md) | Cross-reference those skills and return focus to architecture |
| Reading a huge file from top to bottom | Read the header, class signatures, and key methods; skip boilerplate |
| Producing walls of text without file references | Anchor every claim to a path, function, or command |
| Treating generated files as architecture | Skip `node_modules/`, `dist/`, lock files, and vendored code in the explanation |

## Cross-References

- Token-efficient exploration: [codebase-memory](../codebase-memory/SKILL.md)
- Security review: [security-audit](../security-audit/SKILL.md)
- Performance analysis: [interpreted-performance](../interpreted-performance/SKILL.md), [compiled-performance](../compiled-performance/SKILL.md), [web-performance](../web-performance/SKILL.md)
- Test-driven verification: [test](../test/SKILL.md)
- Orchestrating a large analysis: [orchestrate](../orchestrate/SKILL.md)
