---
name: web-performance
description: >-
  Analyze web application performance thoroughly across Core Web Vitals,
  network, rendering, bundles, backend latency, and delivery. Produce
  prioritized optimization recommendations with measured baselines and
  optionally implement fixes. Use when the user asks to analyze, audit,
  improve, or optimize web app performance, page speed, Lighthouse scores,
  load time, bundle size, TTFB, LCP, INP, CLS, or render performance.
---

# Web Performance

Conduct a **thorough, measured performance audit** of a web application. Baseline real metrics first, trace bottlenecks to root causes, rank fixes by impact × effort, and optionally implement them.

This skill audits the **full delivery path** — build output, network, browser runtime, and backend/API latency for SSR apps. It is not limited to recent diffs unless the user narrows scope.

For CI pipeline speed (not page load), use [ci-optimize](../ci-optimize/SKILL.md). For UI correctness after changes, use [browser-test](../browser-test/SKILL.md).

## Implement Mode (decide first)

| User intent | Behavior after audit |
|-------------|----------------------|
| Default — "analyze performance", "audit page speed", "Lighthouse review", etc. | Deliver findings and recommendations, then **ask** whether to implement optimizations |
| Explicit implement — "analyze and fix", "optimize and implement", "apply optimizations", "make it faster" (with implementation implied) | **Skip the prompt** — implement highest-impact fixes immediately after the report |

When implementing:

1. Fix in priority order: Critical → High → Medium → Low
2. Re-measure after each batch; keep before/after numbers
3. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) after code changes
4. Prefer minimal, targeted diffs — see [simple-code](../simple-code/SKILL.md)
5. Follow [github-publish](../github-publish/SKILL.md) when publishing fixes via PR

When prompting (default), use AskQuestion when available:

- **Prompt**: "Implement the recommended performance optimizations?"
- **Options**: "Yes — implement all" (recommended when Critical/High exist), "Yes — Critical and High only", "No — report only"

If AskQuestion is unavailable, ask conversationally with the same options.

## Audit Workflow

Copy and track progress:

```
Web performance audit:
- [ ] Phase 0: Recon — stack, routes, build tooling, deployment model
- [ ] Phase 1: Baseline — Core Web Vitals, Lighthouse, load metrics
- [ ] Phase 2: Network and assets — bundles, images, fonts, caching
- [ ] Phase 3: Rendering — blocking resources, hydration, layout stability
- [ ] Phase 4: Backend and API — TTFB, SSR, database/query latency
- [ ] Phase 5: Build and delivery — splitting, compression, headers, CDN
- [ ] Phase 6: Runtime — long tasks, memory, interaction delays
- [ ] Phase 7: Report — prioritized findings with evidence
- [ ] Phase 8: Implement — prompt or auto-fix
```

Run phases **in order**. Do not recommend fixes without baseline measurements for the affected area.

### Phase 0 — Recon

Before measuring, map the performance surface:

- Framework and rendering model (SPA, SSR, SSG, hybrid — React, Vue, Next, Nuxt, SvelteKit, etc.)
- Build tool (Vite, Webpack, Turbopack, esbuild, Rollup)
- How to run locally (`package.json` scripts, `Makefile`, `docker compose`, README)
- Key user-facing routes to test (home, auth, heaviest page, checkout/dashboard if applicable)
- Backend/API dependencies for SSR or client data fetching
- Existing perf tooling in repo (Lighthouse CI, bundle analyzer, `web-vitals`, Playwright perf tests)

Start the dev server (or use staging URL the user provides). Note the URL and port. When [docker](../docker/SKILL.md) applies, run the app in a container with ports mapped to the host.

### Phase 1 — Baseline

Measure **before** proposing fixes. Record numbers in the report's baseline table.

**Primary metrics (Core Web Vitals + load):**

| Metric | Target (good) | Tool |
|--------|---------------|------|
| LCP | ≤ 2.5 s | Lighthouse, DevTools Performance |
| INP | ≤ 200 ms | Lighthouse, DevTools Performance |
| CLS | ≤ 0.1 | Lighthouse, DevTools |
| TTFB | ≤ 800 ms | Lighthouse, Network panel, `curl -w` |
| FCP | ≤ 1.8 s | Lighthouse |
| Total page weight | context-dependent | Network panel, Lighthouse |
| JS transferred (gzip/brotli) | context-dependent | Network panel, bundle analyzer |
| Request count | context-dependent | Network panel |

**Run Lighthouse** (preferred when Node is available):

```bash
# Install once if needed: npm install -g lighthouse
lighthouse <url> --output=json --output-path=./lighthouse-report.json --chrome-flags="--headless"
lighthouse <url> --only-categories=performance --preset=desktop
lighthouse <url> --only-categories=performance --form-factor=mobile --throttling-method=simulate
```

Also run **mobile and desktop** when the app serves both. Test the slowest meaningful route, not only `/`.

**Browser DevTools** (via browser MCP when available — read tool schemas first):

```
browser_navigate → target URL
browser_snapshot   → page loaded
# Use Performance/Network recording via MCP or instruct user if MCP lacks perf APIs
```

Capture: waterfall, largest resources, main-thread long tasks, render-blocking requests.

**Repeatable timing** (supplement Lighthouse):

```bash
curl -o /dev/null -s -w 'TTFB: %{time_starttransfer}s  Total: %{time_total}s\n' <url>
```

Run 3–5 times; report median. Prefer median over a single run.

### Phase 2 — Network and Assets

Investigate transfer size and caching:

- **JS/CSS bundles** — total size, duplicate dependencies, unused code
- **Images** — format (WebP/AVIF vs PNG/JPEG), dimensions vs display size, lazy loading, `srcset`/`sizes`
- **Fonts** — count, weight, `font-display`, subsetting, preload vs blocking
- **Third parties** — analytics, ads, widgets; async/defer loading
- **Caching** — `Cache-Control`, ETag, immutable assets, service worker (if any)
- **Compression** — gzip/brotli enabled on HTML/JS/CSS/API

**Bundle analysis** (when applicable):

```bash
# Vite — add rollup-plugin-visualizer or use built-in --mode analyze if configured
npx vite-bundle-visualizer

# Webpack
npx webpack-bundle-analyzer stats.json

# Next.js
ANALYZE=true npm run build
```

Read build config (`vite.config.*`, `webpack.config.*`, `next.config.*`) for splitChunks, manualChunks, dynamic imports.

Grep for heavy imports: moment, lodash full import, icon packs, unused CSS frameworks.

### Phase 3 — Rendering

Focus on what blocks first paint and what causes layout shift:

- Render-blocking CSS/JS in `<head>` without `defer`/`async`/`module`
- Critical CSS inlined vs full stylesheet blocking
- Client-side hydration cost (large JS before interactivity)
- Layout shift sources: images without dimensions, dynamic ad slots, late web fonts
- Excessive DOM size, deep nesting, expensive selectors
- Animations triggering layout/paint on hot paths

For SPAs: time-to-interactive vs first paint. For SSR/SSG: server render time vs client hydration waterfall.

### Phase 4 — Backend and API

When the app has a server or data layer:

- **TTFB** breakdown — DNS, TLS, server processing
- SSR route handlers — uncached heavy work on every request
- API endpoints called on initial load — count, latency, serialization size
- N+1 queries, missing indexes, unbounded list fetches
- Absence of HTTP caching or CDN for API/static responses
- Cold starts (serverless) if deployed that way

Trace the critical path for the slowest page: document → API calls → DB → response.

### Phase 5 — Build and Delivery

Review how assets reach the browser:

- Code splitting and route-based lazy loading
- Tree shaking and side-effect-free packages (`sideEffects: false`)
- Minification and modern output targets (`esbuild.target`, browserslist)
- Image pipeline in build (next/image, vite-imagetools, sharp)
- CDN usage, HTTP/2 or HTTP/3, preconnect/dns-prefetch for third-party origins
- Security headers that affect perf (CSP is fine; avoid unnecessary blocking)
- `preload`/`prefetch`/`modulepreload` for critical vs speculative resources

Check response headers:

```bash
curl -sI <url> | grep -iE 'cache-control|content-encoding|etag|vary'
```

### Phase 6 — Runtime

After load, check interaction and stability:

- Long tasks (> 50 ms) blocking main thread
- Memory growth during navigation (SPA route changes)
- Scroll/input jank — passive listeners, `requestAnimationFrame` misuse
- Web Workers for heavy computation (if applicable)
- Service worker caching strategy (stale-while-revalidate, etc.)

Re-run Lighthouse or DevTools Performance on interactions (click, submit, route change) when INP is poor.

### Phase 7 — Report

Present findings in a structured report. For audits with many findings, use the `canvas` skill — performance audits with metrics tables are a primary canvas use case.

Every finding MUST include:

| Field | Content |
|-------|---------|
| ID | `PERF-001`, `PERF-002`, … |
| Priority | Critical / High / Medium / Low |
| Category | e.g. LCP, Bundle, Image, Caching, TTFB, CLS, INP |
| Location | `path:line`, config key, or URL/resource |
| Evidence | Metric, Lighthouse audit, screenshot, or trace |
| Impact | Estimated effect on LCP/INP/weight/TTFB |
| Recommendation | Concrete fix — not "optimize images" alone |
| Effort | S / M / L |

Sort by priority, then by impact. Include:

**Baseline table** — metrics from Phase 1 (mobile + desktop if tested)

**Top 3 quick wins** — highest impact × lowest effort

**Optimization roadmap** — grouped by category with expected gains

End the report with:

```
Total: N findings (C critical, H high, M medium, L low)
Estimated upside: [summarize largest metric improvements if quantifiable]
```

### Phase 8 — Implementation

**If auto-implement mode** (user requested it): proceed immediately. No prompt.

**If default mode**: ask whether to implement. On "Yes", apply fixes per Implement Mode rules.

When implementing:

- One theme per commit when practical (images, then bundles, then caching)
- Re-run Lighthouse or targeted measurement after each batch
- Do not trade correctness for scores (broken lazy-load is worse than slow load)
- Update the report with before/after metrics; mark findings fixed or residual

## Priority Guide

| Priority | Criteria |
|----------|----------|
| **Critical** | LCP > 4 s or TTFB > 1.8 s on primary route; JS payload > 1 MB gzipped on mobile; render-blocking monolith blocking all content; no compression on text assets |
| **High** | LCP 2.5–4 s; INP > 500 ms; CLS > 0.25; unoptimized hero image; full lodash/moment imports; missing cache headers on static assets |
| **Medium** | Code-splitting gaps; font loading causing FOIT/FOUT; third-party scripts in `<head>` without async; API waterfall on load |
| **Low** | Preconnect hints; minor unused CSS; micro-optimizations with < 100 ms expected gain |

When uncertain, **measure first** — do not guess impact.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Recommendations without baseline metrics | Run Lighthouse and/or DevTools first |
| Optimizing `/` only when user flows fail elsewhere | Test heaviest real routes |
| Suggesting generic "use a CDN" without evidence | Cite missing cache headers or geographic latency |
| Large refactors for marginal gains | Rank by impact × effort; start with quick wins |
| Implementing without re-measurement | Show before/after numbers |
| Breaking UX for Lighthouse score | Preserve functionality; verify with browser-test |
| Auditing only frontend when TTFB dominates | Trace backend/SSR in Phase 4 |

## Cross-References

- Run and verify the app: [browser-test](../browser-test/SKILL.md)
- Containerized dev server: [docker](../docker/SKILL.md)
- Minimal implementation diffs: [simple-code](../simple-code/SKILL.md)
- Tests after fixes: [test](../test/SKILL.md)
- Lint after fixes: [lint](../lint/SKILL.md)
- Publish fixes: [github-publish](../github-publish/SKILL.md)
- Rich report UI: `canvas` skill

## Additional Resources

- Per-area checklists: [checklist.md](checklist.md)
- Command examples: [examples.md](examples.md)
