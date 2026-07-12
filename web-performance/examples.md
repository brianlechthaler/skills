# Web Performance — Examples

Adapt URLs, ports, and commands to the project.

## Start the app

```bash
# Common patterns — read package.json first
npm run dev          # Vite/Next often :5173 or :3000
npm run start        # production preview
docker compose up -d # when compose-deploy/docker skills apply
```

Default URLs: `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`.

## Lighthouse CLI

```bash
npm install -g lighthouse   # or npx lighthouse

# Full report (JSON for parsing)
lighthouse http://localhost:3000 \
  --output=json \
  --output-path=./reports/lighthouse-mobile.json \
  --form-factor=mobile \
  --throttling-method=simulate \
  --chrome-flags="--headless"

# Desktop performance only
lighthouse http://localhost:3000 \
  --only-categories=performance \
  --preset=desktop \
  --output=html \
  --output-path=./reports/lighthouse-desktop.html

# Extract scores with jq
jq '.categories.performance.score * 100' reports/lighthouse-mobile.json
jq '.audits["largest-contentful-paint"].displayValue' reports/lighthouse-mobile.json
```

## Quick TTFB check

```bash
for i in 1 2 3 4 5; do
  curl -o /dev/null -s -w '%{time_starttransfer}\n' http://localhost:3000/
done | sort -n
```

## Response headers

```bash
curl -sI http://localhost:3000/ | grep -iE 'cache-control|content-encoding|etag|content-length'
curl -sI http://localhost:3000/assets/main.js | grep -i cache-control
```

## Bundle analysis

### Vite

```bash
npm install -D rollup-plugin-visualizer
# Add to vite.config — then:
npm run build
npx vite-bundle-visualizer
```

### Next.js

```bash
ANALYZE=true npm run build
# Requires @next/bundle-analyzer in next.config
```

### Webpack

```bash
npm run build -- --json > stats.json
npx webpack-bundle-analyzer stats.json
```

## Find heavy imports

```bash
rg "from ['\"]lodash['\"]|require\\(['\"]lodash['\"]\\)" --glob '*.{js,ts,tsx,vue}'
rg "from ['\"]moment['\"]" --glob '*.{js,ts,tsx}'
rg "import .* from ['\"].*icons" --glob '*.{js,ts,tsx}'
```

Prefer `lodash-es` + named imports or native APIs.

## Image audit (HTML/JSX)

```bash
rg '<img' --glob '*.{html,jsx,tsx,vue,svelte}' -n
rg 'loading=' --glob '*.{jsx,tsx,vue,svelte}'
```

Check for missing `width`/`height`, oversized sources, PNG for photos.

## web-vitals (in-app RUM)

When the project can add runtime measurement:

```bash
npm install web-vitals
```

```javascript
import { onLCP, onINP, onCLS } from 'web-vitals';

onLCP(console.log);
onINP(console.log);
onCLS(console.log);
```

Use for production RUM; Lighthouse remains the default for local audits.

## Before/after comparison template

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LCP (mobile) | 4.2 s | 2.1 s | −50% |
| JS transferred | 890 KB | 420 KB | −53% |
| Lighthouse perf | 62 | 89 | +27 |
| Requests | 78 | 45 | −42% |

Fill this table in the audit report after implementing fixes.

## Common fixes (reference)

| Problem | Typical fix |
|---------|-------------|
| Large LCP image | WebP/AVIF, correct dimensions, preload, `fetchpriority="high"` |
| Huge main bundle | Route-level `import()`, remove unused deps, analyze duplicates |
| Poor TTFB | SSR cache, DB indexes, reduce API round-trips on server |
| High CLS | Explicit image dimensions, reserve ad/banner space, `font-display: swap` |
| Slow INP | Debounce handlers, defer non-critical JS, virtualize lists |
| Uncached static assets | `Cache-Control: public, max-age=31536000, immutable` + hashed filenames |
