---
name: playwright-test
description: >-
  Test web apps and web applications in the browser with Playwright for real UI
  interaction and verification. Use when implementing or changing frontend/UI
  features, fixing visual or interaction bugs, verifying pages in a browser,
  doing smoke or E2E checks, or when the user asks to test a webapp, web
  application, or site with Playwright.
---

# Playwright Test

## Core Requirements

When the work involves a web app or web application:

- **Verify behavior in a real browser** before marking UI work complete, staging, or committing
- Exercise the **actual user flows** affected by the change (navigation, forms, buttons, modals, routing)
- **Confirm visually** with screenshots when layout or styling matters; persist captures into docs via [document-screenshots](../document-screenshots/SKILL.md) when documenting UI
- Report what was tested, the URL, and pass/fail per flow

Playwright testing supplements — does not replace — unit tests and coverage from the [test](../test/SKILL.md) skill. Run both when applicable.

For lint gates, follow [lint](../lint/SKILL.md). If the [docker](../docker/SKILL.md) skill applies, start the app and run Playwright against the containerized dev server.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Frontend/UI code (HTML, CSS, React, Vue, Svelte, etc.) | Pure backend APIs with no UI surface |
| SPA, SSR, or static site changes | CLI-only or library-only changes |
| User asks to "test in the browser" or verify a page with Playwright | Headless unit tests alone satisfy the request |
| Bug reports about layout, clicks, forms, routing | User only wants the browser MCP skill ([browser-test](../browser-test/SKILL.md)) |
| New pages, components, or interactive features | Documentation-only edits |

When unsure, default to **browser verification** for anything a user would see or click.

## Tool Selection

```
Project has Playwright configured (playwright.config.*)?
  → Run existing specs; add or update specs for changed flows

No Playwright yet?
  → Bootstrap @playwright/test, then write ad-hoc specs for verification

User wants interactive Cursor browser tab?
  → Use browser-test skill instead (cursor-ide-browser MCP)
```

**Default to Playwright** for scripted, repeatable browser checks. Prefer `getByRole`, `getByLabel`, and `getByText` over CSS/XPath.

## Playwright Workflow

### 1. Prepare the app

1. Detect how to run the app (`package.json` scripts, `Makefile`, `docker compose`, README).
2. Start the dev server if it is not already running (background terminal). Note the URL and port.
3. If [docker](../docker/SKILL.md) applies, run the server in a container and map the port to the host.

Common defaults: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`.

### 2. Ensure Playwright is ready

```bash
# Project already has Playwright — skip install
test -f playwright.config.ts || test -f playwright.config.js

# Bootstrap when missing (non-interactive)
npm init playwright@latest -- --yes --browser=chromium --lang=typescript

# Install browsers once (host or container per docker skill)
npx playwright install --with-deps
```

Set `baseURL` in `playwright.config.ts` to the dev server URL when bootstrapping or when the config lacks it.

### 3. Choose how to run

| Situation | Approach |
|-----------|----------|
| Repo has E2E specs | `npx playwright test` (or project script) |
| Quick verify during development | Write a temporary spec, run it, delete or promote to permanent |
| User wants to watch | `npx playwright test --headed` |
| Stuck on selectors | `npx playwright codegen <url>` to record locators |

Temporary specs: put under `e2e/` or `.playwright-scratch/`; name by flow (e.g. `login-smoke.spec.ts`).

### 4. Write and run checks

Minimal smoke spec pattern:

```typescript
import { test, expect } from '@playwright/test';

test('smoke — home loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/.+/);
  await expect(page.getByRole('navigation')).toBeVisible();
  await page.screenshot({ path: 'test-results/smoke-home.png', fullPage: true });
});
```

Interaction reference:

| Action | Playwright |
|--------|------------|
| Click button/link | `page.getByRole('button', { name: 'Submit' }).click()` |
| Type in input | `page.getByLabel('Email').fill('user@example.com')` |
| Clear and fill | `page.getByLabel('Email').clear(); await ...fill(...)` |
| Select dropdown | `page.getByLabel('Country').selectOption('US')` |
| Checkbox | `page.getByRole('checkbox', { name: 'Remember me' }).check()` |
| Scroll | `page.locator('#section').scrollIntoViewIfNeeded()` |
| Keyboard | `page.keyboard.press('Enter')` |
| Wait for navigation | `await page.waitForURL('**/dashboard')` |
| Screenshot | `page.screenshot({ path: '...', fullPage: true })` |
| Console errors | Collect via `page.on('console', ...)` or `page.on('pageerror', ...)` |

After each interaction, assert the expected next state — do not assume success from a click alone.

Run:

```bash
npx playwright test                          # all specs
npx playwright test e2e/login-smoke.spec.ts  # one file
npx playwright test --headed --debug         # debug single test
npx playwright show-report                   # HTML report after run
```

Use `--trace on` when diagnosing flaky or failed flows.

### 5. Report results

Summarize pass/fail per flow, the base URL, commands run, and screenshot paths. On failure, read Playwright's error output and trace before changing selectors blindly.

## Test Planning

Derive cases from the change — do not click randomly.

1. **Smoke** — app loads, no console errors, critical shell renders
2. **Happy path** — primary flow end-to-end (e.g. sign-in → dashboard → action → success)
3. **Changed behavior** — every UI element or route touched by the diff
4. **Edge cases** — empty states, validation errors, loading states, mobile-width if relevant
5. **Regression** — adjacent flows that share components or routes

Copy and track:

```
Playwright test progress:
- [ ] Dev server running at ___
- [ ] Playwright installed / browsers ready
- [ ] Smoke: page loads
- [ ] Happy path: ___
- [ ] Changed flows: ___
- [ ] Edge cases: ___
- [ ] No unexpected errors in UI or console
```

## Verification Standards

A flow **passes** when:

- Expected elements are visible (`toBeVisible`, `toHaveText`, `toHaveURL`)
- User actions produce the correct next screen, message, or data
- Screenshot matches intent (alignment, visibility, no obvious breakage)
- No unexpected console errors or failed network requests (unless expected)

A flow **fails** when any of the above is wrong — fix the code and re-run the same spec.

Capture console and page errors in specs when debugging:

```typescript
test.beforeEach(async ({ page }) => {
  page.on('console', (msg) => {
    if (msg.type() === 'error') console.log('console error:', msg.text());
  });
  page.on('pageerror', (err) => console.log('page error:', err.message));
});
```

## Execution Order

For UI change cycles:

```
1. Unit tests + coverage          → see test skill
2. Lint                           → see lint skill
3. Start dev server (or docker)   → see docker skill when applicable
4. Playwright smoke + flows       → this skill
5. Only then: stage / commit / PR
```

If the user asks to commit and browser verification is unchecked for UI work, run it first.

## Promoting Temporary Specs

When a flow must stay stable in CI:

1. Move scratch specs into the project's permanent `e2e/` (or configured test dir)
2. Use stable locators (`getByRole` > `getByTestId` > CSS)
3. Wire into CI via [github-workflows](../github-workflows/SKILL.md) if not already present
4. Run the full suite: `npx playwright test`

## Blockers — Stop and Report

Do not loop on failing actions. Stop and ask the user when you hit:

- Login, OAuth, CAPTCHA, or passkey required
- Missing credentials or API keys
- Destructive confirmation (delete production data)
- Page state you cannot interpret after two careful attempts

Include what you tried, Playwright error output, and the URL.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Assume UI works because unit tests pass | Run Playwright against the live dev server |
| Repeat the same failing locator | Use `codegen`, trace, or a different role/label selector |
| Fragile CSS/XPath selectors | Prefer `getByRole`, `getByLabel`, `getByText` |
| Hard-coded absolute URLs in every spec | Set `baseURL` in config; use relative `page.goto('/')` |
| Test only the happy path | Cover validation, empty, and error states |
| Commit UI changes without browser check | Run smoke + affected flows |
| Leave `.playwright-scratch/` clutter | Delete temp specs or promote them to `e2e/` |

## Additional Resources

- Stack-specific dev servers, ports, and Playwright commands: [examples.md](examples.md)
