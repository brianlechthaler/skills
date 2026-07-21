# Skills catalog

<!-- skill-count:48 -->

All **48** portable [Agent Skills](https://agentskills.io/) in this repository, grouped by category. Each skill is a `<skill>/SKILL.md` directory. Install with [install.py](installer.md) or open any skill link below for full instructions.

Run `python3 install.py --list-by-category` for the same grouping from the CLI.

## Skills (48)

### Containers & Cloud (4)

| Skill | Description |
|-------|-------------|
| [cloud-init](../../cloud-init/SKILL.md) | Generate cloud-init `#cloud-config` user-data for Ubuntu, Debian, Rocky/Alma/RHEL, Amazon Linux, and other cloud images — users, SSH, packages, and first-boot deploy. |
| [compose-deploy](../../compose-deploy/SKILL.md) | Generate a Docker Compose deployment by detecting the project stack and backing services (Postgres, Redis, etc.). Creates compose.yaml, Dockerfiles, and .env.example. |
| [docker](../../docker/SKILL.md) | Run all builds, tests, and tooling inside Docker containers. Nothing installed on the host except Docker. Credentials and SSH keys are mounted read-only from the host. |
| [docker-optimize](../../docker-optimize/SKILL.md) | Reduce Docker image size: baseline layers and bytes, apply multi-stage builds, smaller bases, .dockerignore, and dependency pruning until gains plateau. |

### CI/CD (4)

| Skill | Description |
|-------|-------------|
| [ci-debug](../../ci-debug/SKILL.md) | Debug GitHub Actions failures — fetch logs, classify errors, reproduce locally, and optionally fix the underlying issue. |
| [ci-optimize](../../ci-optimize/SKILL.md) | Aggressively optimize CI for fastest completion: baseline, iterate on caching, parallelization, and path filters until gains plateau. |
| [dependabot-merge](../../dependabot-merge/SKILL.md) | Find open Dependabot PRs, verify updates are safe, fix code for new dependency versions, and merge when tests and CI pass. |
| [github-workflows](../../github-workflows/SKILL.md) | Create GitHub Actions workflows for unit tests, linters, and container builds with GHCR publish. |

### GitHub (5)

| Skill | Description |
|-------|-------------|
| [github-publish](../../github-publish/SKILL.md) | Track changes in git, publish to public GitHub repos with `gh`, and open draft PRs with completed checklist items when work is done. |
| [github-issues](../../github-issues/SKILL.md) | Triage open GitHub issues, implement one fix per issue with its own draft PR, comment on progress, and close issues when work is complete. |
| [github-release](../../github-release/SKILL.md) | Create GitHub releases from the default branch with SemVer tags, Keep a Changelog-style notes, and project-specific deploy instructions. |
| [github-merge-all](../../github-merge-all/SKILL.md) | Merge every open pull request: sync with the default branch, resolve conflicts, pass CI, and land PRs one at a time. |
| [github-prune-branches](../../github-prune-branches/SKILL.md) | Safely prune old local and remote branches that are fully merged or whose PRs are closed/merged, with dry-run and protected refs. |

### Documentation (4)

| Skill | Description |
|-------|-------------|
| [document-project](../../document-project/SKILL.md) | Document projects with a short README linked to `docs/`, per-feature docs, diagrams, and screenshots. |
| [document-screenshots](../../document-screenshots/SKILL.md) | Capture browser screenshots of the running project and embed them in `docs/images/` for documentation. |
| [experimental-warning](../../experimental-warning/SKILL.md) | Add experimental, alpha, beta, or preview warning banners on every user-facing surface — web UI, CLI, TUI, API docs, and more. |
| [hardware-requirements](../../hardware-requirements/SKILL.md) | Infer minimum and recommended CPU, RAM, disk, and GPU from the project stack, then ask before adding specs to docs. |

### Testing (4)

| Skill | Description |
|-------|-------------|
| [browser-test](../../browser-test/SKILL.md) | Test web apps in the browser with real UI interaction and verification before marking UI work complete. |
| [lint](../../lint/SKILL.md) | Enforce linting and formatting before commits. |
| [playwright-test](../../playwright-test/SKILL.md) | Test web apps with Playwright for scripted browser verification, smoke checks, and E2E flows. |
| [test](../../test/SKILL.md) | Enforce TDD and 100% test coverage on generated code before commits. |

### Agent Skills (3)

| Skill | Description |
|-------|-------------|
| [skill-create](../../skill-create/SKILL.md) | Create new agent skills from scratch — author SKILL.md, register in the repo, validate, and merge when CI is green. |
| [skill-quality](../../skill-quality/SKILL.md) | Analyze agent skill quality, score against a rubric, suggest prioritized improvements, and optionally implement fixes. |
| [skill-test](../../skill-test/SKILL.md) | Create and maintain automated tests for agent skills — structure, links, install, and rule conversion. |

### Performance & Observability (6)

| Skill | Description |
|-------|-------------|
| [compiled-performance](../../compiled-performance/SKILL.md) | Profile compiled/native applications, analyze CPU/memory/I/O bottlenecks, recommend optimizations, and optionally implement fixes with measured before/after gains. |
| [hardware-metrics](../../hardware-metrics/SKILL.md) | Measure CPU, RAM, GPU, disk I/O, and hardware temperatures under load; report saturation, thermal and storage headroom, and throttling with structured before/after snapshots. |
| [interpreted-performance](../../interpreted-performance/SKILL.md) | Profile Python, Node.js, Ruby, PHP, and other interpreted runtimes; analyze CPU, memory, I/O, and GC bottlenecks; recommend optimizations; optionally implement fixes with measured gains. |
| [opentelemetry](../../opentelemetry/SKILL.md) | Implement OpenTelemetry observability — traces, metrics, and logs with OTLP export, auto-instrumentation, resource attributes, and collector wiring. |
| [valgrind-memcheck](../../valgrind-memcheck/SKILL.md) | Run Valgrind Memcheck on C/C++ binaries to detect memory leaks and heap errors, report findings in detail, and offer fixes. |
| [web-performance](../../web-performance/SKILL.md) | Analyze web app performance across Core Web Vitals, bundles, network, and backend latency; recommend and optionally implement optimizations. |

### Security (3)

| Skill | Description |
|-------|-------------|
| [security-audit](../../security-audit/SKILL.md) | Perform aggressive full-surface security audits with optional auto-remediation of discovered vulnerabilities. |
| [mcp-security](../../mcp-security/SKILL.md) | Implement and harden MCP servers using NSA AISC security design considerations (CSI PP-26-1834). |
| [prompt-security](../../prompt-security/SKILL.md) | Harden system prompts against leakage, injection, and override — non-disclosure, instruction hierarchy, and red-team review. |

### MCP (3)

| Skill | Description |
|-------|-------------|
| [add-mcp-server](../../add-mcp-server/SKILL.md) | Add a project-local MCP server so agents can interact with databases, APIs, and other project resources. |
| [codebase-memory](../../codebase-memory/SKILL.md) | Explore codebases through a knowledge-graph MCP — search, trace, and fetch snippets instead of reading whole files. |
| [headroom](../../headroom/SKILL.md) | Compress large tool outputs and file contents via Headroom MCP to cut context tokens while keeping reversible retrieval. |

### Local LLM (2)

| Skill | Description |
|-------|-------------|
| [llm-backend-select](../../llm-backend-select/SKILL.md) | Benchmark Ollama, llama.cpp, and vLLM on the user's system and pick the best backend for a chosen metric — tok/s, TTFT, KV cache, memory, or concurrency. |
| [llmfit](../../llmfit/SKILL.md) | Pick the best local LLM for the user's hardware with llmfit — detect specs, score fit/speed/quality, and recommend runnable models. |

### Productivity & Planning (4)

| Skill | Description |
|-------|-------------|
| [daily-plan](../../daily-plan/SKILL.md) | Combine Slack, Gmail, and Jira signals into one ranked high-level plan for what to accomplish today. |
| [gmail-daily-plan](../../gmail-daily-plan/SKILL.md) | Scrape or read Gmail inbox, unread, and important mail, then produce a ranked high-level plan for what to accomplish today. |
| [jira-daily-plan](../../jira-daily-plan/SKILL.md) | Scrape or read Jira assigned issues, sprint boards, and blockers, then produce a ranked high-level plan for what to accomplish today. |
| [slack-daily-plan](../../slack-daily-plan/SKILL.md) | Scan Slack mentions, DMs, and priority channels, then produce a ranked high-level plan for what to accomplish today. |

### Context & Efficiency (5)

| Skill | Description |
|-------|-------------|
| [caveman](../../caveman/SKILL.md) | Cut agent output tokens ~65% with ultra-compressed caveman prose while keeping code, commands, and errors exact. |
| [terse](../../terse/SKILL.md) | Minimize tokens in user-facing prose — fewest words needed for status, results, and next steps. |
| [prompt-conciseness](../../prompt-conciseness/SKILL.md) | Shorten system prompts and agent instructions to save tokens while preserving every critical policy and capability. |
| [simple-code](../../simple-code/SKILL.md) | Write the simplest possible code with the fewest lines — no redundant logic, abstractions, or helpers. |
| [toonify](../../toonify/SKILL.md) | Serialize structured data as TOON instead of JSON to cut prompt tokens 30–60% with lossless encode/decode and schema templates. |

### Orchestration (1)

| Skill | Description |
|-------|-------------|
| [orchestrate](../../orchestrate/SKILL.md) | Plan comprehensively and run subagents in parallel by phase, respecting dependencies and avoiding race conditions. |

## Related

- [Skill authoring](skill-authoring.md) — add a new skill to this repo
- [Getting started](../getting-started.md) — install skills into your agent
- [Installer](installer.md) — `install.py` flags and flows
