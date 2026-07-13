# Docker Optimize — Examples

## Example 1: Python app — single stage to multi-stage slim

**Starting point:** `python:3.12` image, `COPY . .`, `pip install -r requirements.txt` with dev deps — **~1.1 GB**.

**Baseline:**

```bash
docker build -t app:baseline .
docker images app:baseline --format '{{.Size}}'
docker history app:baseline --human | head
```

**Changes:**

1. Add `.dockerignore` excluding `.git`, `tests/`, `__pycache__`, `.venv`
2. Switch to `python:3.12-slim`
3. Split requirements: `requirements.txt` (prod) vs `requirements-dev.txt`
4. `pip install --no-cache-dir -r requirements.txt` only

**After:**

```dockerfile
FROM python:3.12-slim AS production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER nobody
CMD ["python", "-m", "src.main"]
```

| Metric | Before | After |
|--------|--------|-------|
| Image size | 1.1 GB | ~180 MB |
| Layers with build tools | yes | no |

## Example 2: Node frontend — build stage + nginx alpine

**Problem:** Final image contains full `node_modules`, source, and Vite dev tooling — **~900 MB**.

**Fix:**

```dockerfile
FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

| Metric | Before | After |
|--------|--------|-------|
| Image size | 900 MB | ~45 MB |
| Attack surface | Node + source | nginx static only |

## Example 3: Go API — distroless static

**Problem:** `FROM golang:1.22` used as runtime — **~800 MB**.

**Fix:**

```dockerfile
FROM golang:1.22 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /server ./cmd/server

FROM gcr.io/distroless/static-debian12
COPY --from=build /server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

| Metric | Before | After |
|--------|--------|-------|
| Image size | 800 MB | ~12 MB |
| Shell in container | yes | no (expected) |

## Example 4: .dockerignore-only win

**Problem:** `COPY . .` pulls 400 MB `.git` and `node_modules` into build context; accidental layer bloat.

**Fix:** Add `.dockerignore`:

```
.git
node_modules
coverage
*.log
.env
```

No Dockerfile change required if install step already runs `npm ci` cleanly.

| Metric | Before | After |
|--------|--------|-------|
| Build context | 420 MB | 8 MB |
| Final image | 650 MB | 620 MB (smaller context prevents accidental COPY bloat) |

## Example 5: Iteration report template

```markdown
## Docker size optimization — api service

| Metric | Baseline | Final | Δ |
|--------|----------|-------|---|
| `docker images` size | 892 MB | 124 MB | −86% |
| Layer count | 28 | 12 | −16 |
| Largest layer | node_modules 410 MB | slim base 45 MB | — |

### Changes applied
1. Added `.dockerignore`
2. Multi-stage: build → `node:20-bookworm-slim` production
3. `npm ci --omit=dev` in production stage

### Verification
- `docker run --rm app:optimized npm test` (via compose test service): pass
- Health endpoint `/health`: 200
```
