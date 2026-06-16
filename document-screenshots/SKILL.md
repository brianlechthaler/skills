---
name: document-screenshots
description: >-
  Capture browser screenshots of the current project and embed them in
  documentation under docs/images/. Use when documenting UI features, updating
  README or docs with visuals, refreshing stale screenshots, or when the user
  asks to screenshot the app for documentation.
---

# Document Screenshots

## Core Requirements

When documentation needs visuals of the running project:

- **Capture real screenshots** of the project being worked in — not stock images or placeholders
- **Save under `docs/images/`** (or `docs/assets/` if the project already uses it) with descriptive kebab-case filenames
- **Embed in the relevant doc** with relative paths and alt text that states what the image shows
- **Run the app locally** (or in Docker per [docker](../docker/SKILL.md)) so screenshots reflect the current codebase

This skill handles screenshot capture and placement. For overall doc structure, style, and README layout, follow [document-project](../document-project/SKILL.md). For interaction testing before capture, reuse patterns from [browser-test](../browser-test/SKILL.md).

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| UI pages, dashboards, modals, or flows being documented | Pure backend APIs with no visual surface |
| User asks for screenshots in docs or README | Terminal commands that copy-paste equally well as code blocks |
| Refreshing outdated images after UI changes | Project has no runnable UI (library, CLI-only with no TUI) |
| [document-project](../document-project/SKILL.md) checklist needs screenshots | User explicitly says "skip screenshots" |

When unsure and the project has a web UI, default to capturing at least one smoke screenshot of the primary view.

## Tool Selection

```
In Cursor with cursor-ide-browser MCP?
  → Use browser MCP (required for this skill)

No browser MCP?
  → Start the dev server, report the blocker, and leave <!-- screenshot: … --> placeholders
```

**Always read MCP tool schemas** under `cursor-ide-browser` before calling tools.

## Workflow

Copy and track:

```
Screenshot doc progress:
- [ ] Shot list defined (pages, states, filenames)
- [ ] Dev server running
- [ ] Screenshots captured to docs/images/
- [ ] Markdown updated with embeds and alt text
- [ ] Stale images removed or replaced
- [ ] browser_unlock called
```

### 1. Plan the shot list

Before opening the browser, decide what to capture from the docs being written or updated:

| Capture | Skip |
|---------|------|
| Primary landing or home view | Generic OS or IDE chrome unrelated to the app |
| Each major feature screen or route | Duplicate views that add no information |
| Important states: empty, error, success, loading | Sensitive data (real emails, tokens, PII) |
| Responsive layout only when docs discuss it | Full-page shots when a component crop is clearer |

Name files before capture — they should not change after saving:

```
docs/images/<feature>-<view>-<state>.png
```

Examples: `dashboard-overview.png`, `login-validation-error.png`, `settings-api-key-field.png`.

### 2. Prepare the app

1. Detect how to run the app (`package.json`, `Makefile`, `docker compose`, README).
2. Start the dev server in a background terminal if not already running. Note URL and port.
3. If [docker](../docker/SKILL.md) applies, run the server in a container and map the port to the host.

Common defaults: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`.

Use a clean state when possible: seed data, log in with test credentials, or reset fixtures so screenshots are reproducible.

### 3. Open and lock

```
browser_tabs (action: "list")
browser_navigate (url)              → omit position unless user asked to show browser
browser_lock (action: "lock")       → after navigate; lock existing tab first if reusing
```

### 4. Navigate to each shot

For each item in the shot list:

1. `browser_navigate` or interact (`browser_click`, `browser_fill`, etc.) to reach the target state
2. `browser_snapshot` — confirm the page is ready (no spinners, correct route, expected elements)
3. `browser_take_screenshot` with:
   - `filename`: workspace-relative path, e.g. `docs/images/dashboard-overview.png`
   - `fullPage: true` when the doc needs content below the fold; otherwise viewport only
   - `ref` / `element` when cropping to a specific component

Create `docs/images/` (or `docs/assets/`) before the first capture if it does not exist.

After each screenshot, verify the file exists in the workspace. Re-capture if the image is blank, shows a login wall unexpectedly, or includes sensitive data.

### 5. Embed in documentation

Add or update markdown in the doc that explains the feature — not only the README:

```markdown
![Dashboard overview showing the project list sidebar and main content area](images/dashboard-overview.png)
```

Rules:

- Paths are **relative to the markdown file** (from `docs/features/foo.md`, use `../images/…` or `images/…` depending on layout)
- **Alt text** describes what a reader should learn from the image, not "screenshot" or "image"
- Place the image near the prose it illustrates
- Remove or replace outdated images in the same commit — do not leave orphaned files unless other docs still reference them

### 6. Unlock and finish

```
browser_lock (action: "unlock")
```

Complete the [document-project](../document-project/SKILL.md) checklist for any docs touched.

## Blockers — Stop and Report

Stop and ask the user when you hit:

- Login, OAuth, CAPTCHA, or passkey with no test credentials
- Screenshot would expose secrets, production data, or PII
- Page state cannot be reached after two careful attempts
- No browser MCP and user has not approved placeholders only

Report what was captured, what was blocked, and which docs were updated.

## Execution Order

When shipping a documented UI feature:

```
1. Implement or fix the UI
2. Unit tests + lint          → test and lint skills
3. browser-test smoke         → confirm UI works (browser-test skill)
4. document-screenshots       → capture and embed images
5. document-project gates     → README links, style, completeness
6. Commit / PR                → github-publish skill when applicable
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Placeholder images left indefinitely | Capture real screenshots or explicit user deferral |
| `page-{timestamp}.png` filenames | Descriptive names planned before capture |
| Screenshots in repo root or `/tmp` | Always `docs/images/` or project `docs/assets/` |
| Huge full-page PNGs for a small widget | Element screenshot or viewport crop |
| Sensitive data in images | Redact, use fixtures, or mock data |
| `browser_lock` before `browser_navigate` | Navigate first, then lock |
| Embedding without alt text | Alt text that explains the UI state shown |

## Additional Resources

- Stack-specific URLs, ports, and capture examples: [examples.md](examples.md)
