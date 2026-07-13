---
name: docker-optimize
description: >-
  Reduce Docker image size for the current project. Baseline image layers and
  bytes, audit Dockerfiles and build context, apply multi-stage builds, smaller
  bases, .dockerignore, and dependency pruning, then re-measure until gains
  plateau. Use when the user asks to shrink containers, slim images, optimize
  Dockerfiles, reduce image size, or make Docker builds smaller.
---

# Docker Image Size Optimize

Reduce **final runtime image size** for the project you are in. Baseline bytes and layer count first, apply the highest-impact change, rebuild, and re-measure until further edits no longer yield meaningful savings.

Pair with [docker](../docker/SKILL.md) to build and test inside containers. For initial stack setup, see [compose-deploy](../compose-deploy/SKILL.md). For CI build speed (not image bytes), see [ci-optimize](../ci-optimize/SKILL.md).

## Core Rule

**Optimize for smallest production-ready runtime image.** Preserve correctness — the app must still build, start, and pass tests after every change. One focused optimization per commit when practical.

## Prerequisites

```bash
docker version
docker buildx version
```

Locate container config:

```bash
ls -la Dockerfile Dockerfile.* docker-compose*.yml compose*.yaml .dockerignore 2>/dev/null
```

Identify the **production image** — the tag pushed to a registry or run in production, not a dev-only `docker compose` service with bind mounts.

## Optimization Loop

Copy and track until done:

```
Docker optimize progress:
- [ ] Baseline measured (image tag, compressed size, layer count, largest layers)
- [ ] Build context audited (.dockerignore, COPY scope)
- [ ] Bottleneck ranked (top 3 by wasted bytes)
- [ ] Change applied (one focused optimization)
- [ ] Image rebuilt and app smoke-tested
- [ ] New size recorded and compared to baseline
- [ ] Next bottleneck identified or stop criteria met
```

### 1. Measure baseline

Build the production target:

```bash
docker build -t app:baseline .
# Multi-stage: build only the final stage
docker build --target production -t app:baseline .
```

Record size:

```bash
docker images app:baseline --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
docker history app:baseline --human --no-trunc=false
```

Prefer **compressed pull size** when comparing registry images:

```bash
docker pull ghcr.io/org/app:latest
docker images ghcr.io/org/app:latest --format '{{.Size}}'
```

Optional deep dive (when available):

```bash
# dive app:baseline   # layer efficiency; install separately if missing
```

Record:

| Field | Value |
|-------|-------|
| Image tag | |
| Uncompressed size (`docker images`) | |
| Layer count (`docker history`) | |
| Largest layers (from `docker history`) | |
| Build context size | `du -sh .` vs `docker build` context |

### 2. Rank bottlenecks

Order candidates by **bytes saved × feasibility**. Typical wins (apply what fits the repo):

| Technique | Typical savings | When to use |
|-----------|-----------------|-------------|
| `.dockerignore` | Large (context + accidental COPY) | Missing or incomplete |
| Multi-stage build | Very large | Build tools in final image |
| Smaller base (`-slim`, `-alpine`, `distroless`, `scratch`) | Large | Full OS images for simple apps |
| Production-only deps | Large | Dev/test packages in runtime image |
| Remove package manager caches | Medium | `apt`, `pip`, `npm` caches left behind |
| Fewer layers / merged RUN for package installs | Small–medium | Many separate `RUN apt-get` lines |
| Static binary (Go/Rust) → `scratch`/`distroless` | Very large | Compiled single-binary services |
| Strip symbols / UPX (careful) | Medium | Native binaries only |
| Don't COPY source when only artifact needed | Large | Frontend builds, compiled output |

Use [checklist.md](checklist.md) during the audit.

### 3. Apply one change

Edit Dockerfile, `.dockerignore`, or build args. Rebuild the **same target** as baseline.

After each change:

```bash
docker build -t app:optimized .
docker images app:baseline app:optimized --format 'table {{.Tag}}\t{{.Size}}'
```

Smoke-test the new image — do not trade size for a broken container:

```bash
docker run --rm app:optimized <health-check-or-smoke-command>
```

Use `docker compose run` when the project defines health checks or test services.

### 4. Stop criteria

Stop iterating when:

- Remaining candidates save &lt; ~5% of current size, **or**
- Next change risks runtime breakage (glibc vs musl, missing CA certs, shell-less debug), **or**
- User scope is satisfied

Report before/after table and list changes made.

## High-Impact Patterns

### .dockerignore

Exclude anything not required at build time:

```
.git
.github
node_modules
__pycache__
*.pyc
.venv
venv
target/
dist/
build/
coverage/
*.md
docs/
tests/
.env
.env.*
```

Keep lockfiles and manifests the install step needs. Do not ignore files referenced by `COPY`.

### Multi-stage builds

Build in a fat stage; copy only artifacts to the runtime stage:

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-bookworm AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-bookworm-slim AS production
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

```dockerfile
FROM golang:1.22 AS build
WORKDIR /src
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app .

FROM gcr.io/distroless/static-debian12
COPY --from=build /app /app
ENTRYPOINT ["/app"]
```

### Smaller base images

| Stack | Prefer | Avoid in production |
|-------|--------|---------------------|
| Node.js | `node:<LTS>-bookworm-slim` or `-alpine` | `node:<LTS>` (full Debian) |
| Python | `python:<ver>-slim` | `python:<ver>` |
| Go / Rust static | `distroless/*`, `scratch` | `golang` / `rust` images |
| Java | `eclipse-temurin:*-jre-alpine` | JDK images when only JRE needed |
| Nginx static | `nginx:alpine` | `nginx` (full Debian) |

**Alpine vs slim:** Alpine is smaller but uses musl — verify native wheels/extensions (Python, Node native addons) before switching.

### Dependency hygiene

| Ecosystem | Production install |
|-----------|-------------------|
| npm/yarn/pnpm | `npm ci --omit=dev`, `yarn workspaces focus --production`, `pnpm deploy` |
| pip | `pip install --no-cache-dir .` without `[dev]` extras; use `pip wheel` + copy wheels in multi-stage |
| apt | `RUN apt-get update && apt-get install -y --no-install-recommends pkg && rm -rf /var/lib/apt/lists/*` |
| cargo | `cargo build --release`; copy only the binary |
| go | `CGO_ENABLED=0`, `-ldflags="-s -w"` |

Never install compilers, git, curl, or editors in the final stage unless the app truly needs them at runtime.

### COPY order and scope

1. Copy dependency manifests first → `RUN install` → copy source (maximizes cache, avoids stale deps).
2. `COPY` only paths the stage needs — not the entire repo into every stage.
3. For interpreted apps, omit tests, docs, and CI config from the runtime stage.

### BuildKit cache mounts (CI speed, not final size)

Cache mounts speed rebuilds but do not shrink the final image. Still use `--no-cache-dir` / clean package lists so installed artifacts stay small:

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt
```

## Agent Behavior Checklist

- [ ] Baseline image size and largest layers recorded before editing
- [ ] `.dockerignore` reviewed or added
- [ ] Production stage identified; build tools excluded from runtime
- [ ] One optimization at a time when possible; size re-measured after each
- [ ] Container smoke-tested or test suite run after changes
- [ ] Before/after sizes reported to the user
- [ ] Functional regressions fixed — do not ship a smaller broken image

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| `FROM ubuntu` / full `node` for a 10 MB static site | `nginx:alpine` or distroless |
| `COPY . .` before dependency install | Copy lockfiles first, then source |
| Dev dependencies in production stage | Multi-stage or `--omit=dev` |
| Leaving `apt`/`apk` caches and lists | Clean in the same `RUN` layer |
| Squashing layers blindly | Multi-stage + smaller base (squash hides problems) |
| Alpine without testing native deps | Verify build and runtime on target base |
| Shrinking test/CI images instead of prod | Clarify which image the user cares about |
| Removing CA certs or timezone data to save KB | Keep runtime essentials |

## Related Skills

- [docker](../docker/SKILL.md) — run builds and tests in containers
- [compose-deploy](../compose-deploy/SKILL.md) — generate stack-aware compose and Dockerfiles
- [ci-optimize](../ci-optimize/SKILL.md) — faster CI pipelines (orthogonal to image bytes)
- [github-workflows](../github-workflows/SKILL.md) — GHCR publish and build workflows

See [examples.md](examples.md) for before/after walkthroughs.
