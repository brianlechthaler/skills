# Web Performance — Checklists

Use during Phases 2–6. Check items that apply; cite evidence for failures.

## Network and Assets

- [ ] HTML document size reasonable (< 100 KB uncompressed typical)
- [ ] JS total transfer (gzip/brotli) measured and documented
- [ ] CSS total transfer measured; unused CSS estimated if tooling available
- [ ] No duplicate versions of same library in bundle (check analyzer)
- [ ] Images use modern formats (WebP/AVIF) where supported
- [ ] Images sized to display dimensions (not 4000px for 400px slot)
- [ ] Below-fold images lazy-loaded (`loading="lazy"` or framework equivalent)
- [ ] Hero/LCP image preloaded or prioritized (`fetchpriority="high"`, `<link rel="preload">`)
- [ ] Fonts: ≤ 2 families, subsetted, `font-display: swap` or optional
- [ ] Third-party scripts deferred or loaded after first paint
- [ ] Static assets have long-cache headers (`max-age` + fingerprinted filenames)
- [ ] HTML/API responses use gzip or brotli
- [ ] No unnecessary redirects on critical path

## Rendering

- [ ] No render-blocking JS in `<head>` without `defer`/`type="module"`
- [ ] Critical CSS path identified; non-critical CSS deferred
- [ ] LCP element identified (usually hero image, heading, or video poster)
- [ ] CLS sources documented (images without width/height, injected banners, fonts)
- [ ] DOM node count reasonable for page type (< 1500 nodes typical content page)
- [ ] Hydration scope minimized (islands, partial hydration, or SSR static where possible)
- [ ] Expensive work not on main thread during initial load (consider worker/defer)

## Backend and API

- [ ] TTFB measured for document and slowest SSR route
- [ ] Database queries on critical path counted; N+1 identified
- [ ] API responses on initial load minimized (BFF aggregation, GraphQL batching, etc.)
- [ ] Server-side caching for semi-static SSR pages
- [ ] JSON payloads sized; over-fetching fields removed
- [ ] Connection pooling / warm instances if serverless cold starts hurt TTFB

## Build and Delivery

- [ ] Route-based or component-based code splitting in use
- [ ] Dynamic `import()` for heavy/rare routes and modals
- [ ] Tree shaking verified (ES modules, `sideEffects` in package.json)
- [ ] Production build minified; source maps not shipped to users
- [ ] `browserslist` or build target not unnecessarily legacy
- [ ] CDN or edge caching configured for static assets
- [ ] `preconnect` to critical third-party origins (fonts, API)
- [ ] HTTP/2 or HTTP/3 enabled on production host

## Runtime and Interaction

- [ ] INP measured or estimated from long tasks + event handlers
- [ ] Input handlers not doing heavy sync work
- [ ] Scroll listeners passive where not calling `preventDefault`
- [ ] List virtualization for long lists (> 100 items)
- [ ] Memory stable across SPA navigations (no obvious leaks)
- [ ] Service worker strategy documented if present

## Measurement Quality

- [ ] Tested on throttled mobile (Lighthouse simulated or DevTools)
- [ ] Tested representative authenticated route if auth changes payload
- [ ] Median of multiple runs, not single sample
- [ ] Baseline captured before any optimization changes
