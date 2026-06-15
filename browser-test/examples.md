# Browser Test — Stack Examples

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
# wait until "ready" or port is listening, then navigate
```

## Docker (with docker skill)

```bash
docker compose up -d web
# Map e.g. 3000:3000 — test http://localhost:3000
```

## Playwright

```bash
# Install browsers once (in container or host per docker skill)
npx playwright install --with-deps

# Run all E2E
npx playwright test

# Run one spec during development
npx playwright test e2e/login.spec.ts

# Headed debug (when user wants to watch)
npx playwright test --headed --debug
```

Config tip: set `baseURL` in `playwright.config.ts` to the dev server URL.

## Cypress

```bash
npx cypress run                    # headless CI-style
npx cypress open                   # interactive runner
npm run test:e2e                   # if defined in package.json
```

## MCP flow example (login smoke)

1. `browser_navigate` → `http://localhost:3000/login`
2. `browser_lock` → `action: "lock"`
3. `browser_snapshot` → find email/password refs
4. `browser_fill` → email field
5. `browser_fill` → password field
6. `browser_click` → submit button ref
7. `browser_snapshot` → confirm redirect to dashboard
8. `browser_take_screenshot` → visual record
9. `browser_lock` → `action: "unlock"`

## Reporting template

```markdown
## Browser test results

**URL:** http://localhost:3000
**Server:** `npm run dev` (already running)

| Flow | Result | Notes |
|------|--------|-------|
| Smoke — home loads | Pass | Title and nav visible |
| Login happy path | Pass | Redirected to /dashboard |
| Empty cart state | Pass | "Your cart is empty" shown |

**Issues:** none
```
