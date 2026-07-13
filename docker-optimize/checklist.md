# Docker Optimize — Checklist

Use during the audit phase. Check items that apply; note wasted bytes or missing config.

## Build Context

- [ ] `.dockerignore` exists and excludes `.git`, local deps (`node_modules`, `.venv`), build output, tests, docs
- [ ] Build context size reasonable (`docker build` does not upload GB of junk)
- [ ] No secrets or `.env` files in context or image layers
- [ ] Only required paths passed to `COPY`

## Dockerfile Structure

- [ ] Multi-stage build separates build tools from runtime
- [ ] Final stage `FROM` is minimal (`-slim`, `-alpine`, `distroless`, or `scratch` where appropriate)
- [ ] Final stage does not include compiler, git, curl, or package manager unless required at runtime
- [ ] `COPY --from=build` used for artifacts only (binaries, `dist/`, wheels)
- [ ] Dependency manifests copied before source for layer caching
- [ ] `WORKDIR` set; no redundant `RUN cd`

## Dependencies

- [ ] Production image installs runtime deps only (no devDependencies, test extras, debug symbols)
- [ ] `pip install --no-cache-dir` or equivalent
- [ ] `npm ci --omit=dev` / `yarn install --production` / `pnpm --prod`
- [ ] `apt-get` uses `--no-install-recommends` and cleans `/var/lib/apt/lists/*`
- [ ] No duplicate install of same packages across stages

## Runtime Image

- [ ] Non-root `USER` when the app supports it
- [ ] `CMD`/`ENTRYPOINT` targets production process, not dev server (unless dev image)
- [ ] Health check still works after base image change
- [ ] Native extensions verified if switching Debian ↔ Alpine (musl vs glibc)
- [ ] CA certificates present for HTTPS outbound calls
- [ ] Required locale/timezone data retained if app needs them

## Measurement

- [ ] Baseline `docker images` size recorded
- [ ] `docker history` reviewed for largest layers
- [ ] After changes: image rebuilt, size compared, app smoke-tested
- [ ] Registry compressed size checked if image is pushed to GHCR/Docker Hub

## CI / Registry (optional)

- [ ] CI builds the same Dockerfile target as production
- [ ] Build cache (`cache-from`/`cache-to`) used for speed without bloating final layers
- [ ] Tags distinguish prod vs dev images when sizes differ greatly
