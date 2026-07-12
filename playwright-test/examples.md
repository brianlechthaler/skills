# Playwright Test — Stack Examples

Adapt URLs and commands to the project. Prefer Makefile/CI scripts when present.

## Dev server URLs

| Stack | Start | Default URL |
|-------|-------|-------------|
| Vite (React, Vue, Svelte) | `npm run dev` | `http://localhost:5173` |
| Next.js | `npm run dev` | `http://localhost:3000` |
| Create React App | `npm start` | `http://localhost:3000` |
| Nuxt | `npm run dev` | `http://localhost:3000` |
| Angular | `ng serve` | `http://localhost:4200` |
| Rails | `bin/rails server` | `http://localhost:3000` |
| Django | `python manage.py runserver` | `http://localhost:8000` |
| Flask | `flask run` | `http://localhost:5000` |
| Docker Compose | `docker compose up web` | check `ports:` in compose file |

Background start example:

```bash
npm run dev
# wait until "ready" or port is listening, then run playwright
```

## Docker (with docker skill)

```bash
docker compose up -d web
# Map e.g. 3000:3000 — set baseURL to http://localhost:3000
npx playwright test
```

## Bootstrap Playwright

```bash
# New project — non-interactive TypeScript + Chromium
npm init playwright@latest -- --yes --browser=chromium --lang=typescript

# Add to existing project
npm i -D @playwright/test
npx playwright install --with-deps
```

`playwright.config.ts` baseURL example:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Common commands

```bash
npx playwright test                              # all E2E
npx playwright test e2e/login.spec.ts          # one spec
npx playwright test -g "smoke"                   # by title
npx playwright test --headed                     # visible browser
npx playwright test --headed --debug           # inspector
npx playwright test --trace on                 # trace every test
npx playwright show-report                     # open HTML report
npx playwright codegen http://localhost:3000   # record locators
```

## Playwright flow example (login smoke)

`e2e/login-smoke.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test('login happy path', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('secret');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.screenshot({ path: 'test-results/login-dashboard.png' });
});
```

Run:

```bash
npx playwright test e2e/login-smoke.spec.ts
```

## Console error check

```typescript
test('no console errors on home', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  await page.goto('/');
  expect(errors).toEqual([]);
});
```

## Reporting template

```markdown
## Playwright test results

**URL:** http://localhost:3000
**Server:** `npm run dev` (already running)
**Command:** `npx playwright test e2e/`

| Flow | Result | Notes |
|------|--------|-------|
| Smoke — home loads | Pass | Title and nav visible |
| Login happy path | Pass | Redirected to /dashboard |
| Empty cart state | Pass | "Your cart is empty" shown |

**Issues:** none
```
