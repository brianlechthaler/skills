---
name: document-project
description: >-
  Document projects with a short README linked to docs/, per-feature docs,
  diagrams, and screenshots. Use when writing or updating a README, creating
  docs/, documenting features, onboarding content, or project documentation.
---

# Document Project

## Core Requirements

When applicable to the work at hand:

- Always document every feature
- Avoid making the readme too long and instead link to docs in a docs/ folder
- Visual elements like graphs should be used when applicable
- If possible and when applicable, use screenshots
- Avoid sounding like AI e.g. purple prose, excessive use of em dashes
- Be concise while also including important information
- Be utilitiarian and don't use a bunch of marketing-speak

These are hard gates for documentation work. Do not mark documentation complete until every shipped or changed feature has a doc entry and the README points to it.

For lint and test gates on code changes, follow the [lint](../lint/SKILL.md) and [test](../test/SKILL.md) skills before commit.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New features, APIs, CLI commands, config surfaces | Internal-only refactors with no user-visible change |
| README creation or updates | One-line code comments (use normal code-comment style) |
| Onboarding or setup instructions | Generated lockfiles or vendored third-party code |
| Architecture or workflow explanations | User explicitly says "skip docs" for a change |
| User asks to document, explain, or write project docs | Typo fixes in existing docs with no scope change |

When unsure, default to **document the change**. If a feature is user-facing or affects setup/usage, it needs a doc.

## Documentation Layout

Use a two-tier structure:

```
project-root/
├── README.md              # Short entry point — links into docs/
└── docs/
    ├── index.md           # Optional map of all docs (for large projects)
    ├── getting-started.md # Setup, install, first run
    ├── architecture.md    # System overview, diagrams
    └── features/
        └── <feature>.md   # One file per feature or cohesive capability
```

**README.md** — orientation only: what the project is, how to install/run, where to find docs. Target roughly one screen on a laptop; never duplicate feature detail that belongs in `docs/`.

**docs/** — depth: setup edge cases, feature behavior, configuration, troubleshooting, architecture.

Link from README to `docs/` using relative paths (e.g. `[Features](docs/features/)`). Keep link text descriptive, not "click here".

## Workflow

For each documentation task:

```
1. Inventory features/capabilities affected by the change
2. Update or create docs/<relevant>.md for each feature
3. Add diagrams or screenshots where they clarify (see below)
4. Trim README — add links, remove duplicated detail
5. Run the completion checklist
```

### When to add diagrams

Use **Mermaid** (or ASCII for tiny flows) when text alone is harder to follow:

| Use a diagram | Skip a diagram |
|---------------|----------------|
| Multi-step workflows or request/response paths | Single-step operations |
| Architecture with 3+ components | One module, one responsibility |
| State machines or branching logic | Flat config key lists |
| Data flow between services | Naming conventions |

Place diagrams in the doc they explain, not in README. Prefer ` ```mermaid ` fenced blocks in Markdown.

Example (in a feature doc, use a `mermaid` fenced block):

    ## Request flow

    ```mermaid
    sequenceDiagram
      Client->>API: POST /items
      API->>DB: insert
      DB-->>API: id
      API-->>Client: 201 Created
    ```

### When to add screenshots

Capture screenshots when they show something text cannot replace:

- UI layout, dashboards, or CLI TUI output
- Error states or success confirmations users should recognize
- Multi-pane IDE or tool configuration steps

Store images under `docs/images/` (or `docs/assets/`). Use descriptive filenames (`login-form-validation-error.png`). Reference with relative paths and alt text that states what the image shows.

If the project has a runnable UI, use [document-screenshots](../document-screenshots/SKILL.md) to capture and embed images during documentation. If browser MCP is unavailable, leave a clear placeholder: `<!-- screenshot: settings panel with API key field -->`.

Do not screenshot generic terminal commands that copy-paste equally well as code blocks.

## Writing Style

Write like internal technical documentation, not marketing copy.

| Do | Avoid |
|----|-------|
| Short sentences, active voice | Purple prose, filler intros ("In today's world…") |
| Plain words: "use", "run", "returns" | Hype: "revolutionary", "seamless", "powerful" |
| Hyphens or commas for asides | Em dashes every other sentence |
| State facts: what it does, defaults, limits | Vague promises: "fast", "easy", "flexible" |
| Imperative steps for procedures | "You might want to consider…" |
| Link to related docs instead of repeating | Copy-pasting the same paragraph in README and docs |

**Tone check before finishing:** Read aloud mentally. If it sounds like a landing page or an LLM essay, rewrite shorter and more direct.

## README Template

Use this skeleton. Omit sections that do not apply; do not pad.

```markdown
# Project Name

One or two sentences: what it is and who it is for.

## Quick start

Minimal commands to install and run. Link to [Getting started](docs/getting-started.md) for details.

## Documentation

- [Getting started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Features](docs/features/)

## Requirements

Runtime versions, env vars, or services (brief).

## License

Link or name only if applicable.
```

## Feature Doc Template

Create one file per feature (or per cohesive capability) under `docs/features/`:

```markdown
# Feature Name

What it does in one sentence.

## Overview

Behavior, defaults, and constraints. No marketing language.

## Usage

Commands, API calls, or UI steps with copy-paste examples.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `foo`  | `bar`   | …           |

## Diagram (if applicable)

[Mermaid or link to docs/images/…]

## Troubleshooting

Common errors and fixes.

## Related

Links to other docs/features.
```

## Completion Checklist

Copy and complete before marking documentation done:

```
Documentation gates:
- [ ] Every new or changed feature has a doc in docs/ (not only README)
- [ ] README is short and links to docs/ for detail
- [ ] Diagrams added where flows/architecture need them
- [ ] Screenshots added or placeholder noted where UI/visual steps matter
- [ ] No AI-sounding or marketing copy; concise and factual
- [ ] Links work (relative paths, no broken anchors)
```

If the user asks to ship a feature and any box is unchecked, finish documentation first unless they explicitly opt out.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Long README with every feature explained | Short README + `docs/features/` |
| Undocumented "obvious" features | One doc entry per feature |
| Diagrams for trivial one-liners | Plain text or a code block |
| Stock screenshots or unrelated images | Capture the actual project UI/output |
| Em dashes, superlatives, emoji decoration | Plain punctuation and facts |
| Duplicating content across files | Single source in docs/; README links |
| "Documentation TODO" left indefinitely | Write the doc or note explicit user deferral |

## Additional Resources

- Stack-specific doc tooling (MkDocs, Docusaurus, etc.): follow existing project config if present; default to plain Markdown in `docs/` when none exists.
