---
name: browser-test
description: >-
  Test web apps and web applications in the browser with real UI interaction
  and verification. Use when implementing or changing frontend/UI features, fixing
  visual or interaction bugs, verifying pages in a browser, doing smoke or E2E
  checks, or when the user asks to test a webapp, web application, or site in
  the browser.
---

# Browser Test

## Core Requirements

When the work involves a web app or web application:

- **Verify behavior in a real browser** before marking UI work complete, staging, or committing
- Exercise the **actual user flows** affected by the change (navigation, forms, buttons, modals, routing)
- **Confirm visually** with snapshots and screenshots when layout or styling matters
- Report what was tested, the URL, and pass/fail per flow

Browser testing supplements — does not replace — unit tests and coverage from the [test](../test/SKILL.md) skill. Run both when applicable.

For lint gates, follow [lint](../lint/SKILL.md). If the [docker](../docker/SKILL.md) skill applies, start the app and run browser checks against the containerized dev server.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Frontend/UI code (HTML, CSS, React, Vue, Svelte, etc.) | Pure backend APIs with no UI surface |
| SPA, SSR, or static site changes | CLI-only or library-only changes |
| User asks to "test in the browser" or verify a page | Headless unit tests alone satisfy the request |
| Bug reports about layout, clicks, forms, routing | Repo has Playwright/Cypress CI and user only wants that suite run |
| New pages, components, or interactive features | Documentation-only edits |

When unsure, default to **browser verification** for anything a user would see or click.

## Tool Selection

```
In Cursor with browser MCP available?
  → Use cursor-ide-browser MCP (preferred for interactive agent testing)

Project has Playwright or Cypress configured?
  → Also run the project's E2E suite for regression; use MCP for exploratory and fix-verify loops

Neither available?
  → Start the dev server, ask the user to confirm the URL, and use MCP when it becomes available
```

**Always read MCP tool schemas** under the `cursor-ide-browser` server before calling tools.

## Browser MCP Workflow

### 1. Prepare the app

1. Detect how to run the app (`package.json` scripts, `Makefile`, `docker compose`, README).
2. Start the dev server if it is not already running (background terminal). Note the URL and port.
3. If [docker](../docker/SKILL.md) applies, run the server in a container and map the port to the host.

Common defaults: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`.

### 2. Open and lock

```
browser_tabs (action: "list")     → see open tabs
browser_navigate (url)            → omit position unless user asked to show browser
browser_lock (action: "lock")     → required before interactions; skip if just navigating
```

If a tab already exists for the target URL, lock it first instead of opening a duplicate.

### 3. Understand the page

```
browser_snapshot                    → accessibility tree (primary source of truth)
browser_snapshot (interactive: true) → form controls and buttons only
browser_take_screenshot             → layout, color, visual regressions
```

Use `browser_snapshot` before every interaction — refs come from the latest snapshot.

### 4. Interact

| Action | Tool |
|--------|------|
| Click button/link | `browser_click` |
| Type in input | `browser_type` or `browser_fill` (clear-first) |
| Select dropdown | `browser_select_option` |
| Scroll | `browser_scroll` |
| Keyboard shortcut | `browser_press_key` |
| Drag | `browser_drag` |
| Deep inspection | `browser_cdp` (DOM, styles, network, performance) |

After each interaction, take a fresh `browser_snapshot` or screenshot to confirm the expected state.

### 5. Unlock and report

```
browser_lock (action: "unlock")   → when all browser work is done
```

## Test Planning

Derive cases from the change — do not click randomly.

1. **Smoke** — app loads, no console errors, critical shell renders
2. **Happy path** — primary flow end-to-end (e.g. sign-in → dashboard → action → success)
3. **Changed behavior** — every UI element or route touched by the diff
4. **Edge cases** — empty states, validation errors, loading states, mobile-width if relevant
5. **Regression** — adjacent flows that share components or routes

Copy and track:

```
Browser test progress:
- [ ] Dev server running at ___
- [ ] Smoke: page loads
- [ ] Happy path: ___
- [ ] Changed flows: ___
- [ ] Edge cases: ___
- [ ] No unexpected errors in UI or console
```

## Verification Standards

A flow **passes** when:

- Expected elements appear in `browser_snapshot`
- User actions produce the correct next screen, message, or data
- Visual screenshot matches intent (alignment, visibility, no obvious breakage)
- No blocker dialogs, infinite spinners, or error toasts unless expected

A flow **fails** when any of the above is wrong — fix the code and re-run the same steps.

Use `browser_cdp` with `Runtime.evaluate` or `Log.enable` when you need console errors or network failures.

## Execution Order

For UI change cycles:

```
1. Unit tests + coverage          → see test skill
2. Lint                           → see lint skill
3. Start dev server (or docker)   → see docker skill when applicable
4. Browser smoke + affected flows → this skill
5. Project E2E suite (if present) → playwright test / cypress run
6. Only then: stage / commit / PR
```

If the user asks to commit and browser verification is unchecked for UI work, run it first.

## Project E2E Suites

When the repo already has browser automation, run it after MCP verification passes:

| Signal | Command |
|--------|---------|
| `playwright.config.*` | `npx playwright test` |
| `cypress.config.*` | `npx cypress run` |
| `package.json` script | `npm run test:e2e` / `test:browser` |
| CI workflow | Mirror the CI browser test job |

Prefer adding or updating Playwright/Cypress specs for flows that must stay stable in CI. Use MCP for development-time verification and debugging.

## Blockers — Stop and Report

Do not loop on failing actions. Stop and ask the user when you hit:

- Login, OAuth, CAPTCHA, or passkey required
- Missing credentials or API keys
- Destructive confirmation (delete production data)
- Page state you cannot interpret after two careful attempts

Include what you tried, what you observed, and the URL.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Assume UI works because unit tests pass | Open the app and walk the flow |
| Repeat the same failing click | New snapshot, different selector, or CDP inspect |
| `browser_lock` before `browser_navigate` | Navigate first, then lock |
| Skip `browser_unlock` | Always unlock when finished |
| Test only the happy path | Cover validation, empty, and error states |
| Commit UI changes without browser check | Run smoke + affected flows |

## Additional Resources

- Stack-specific dev servers, ports, and E2E commands: [examples.md](examples.md)
