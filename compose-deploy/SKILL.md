---
name: compose-deploy
description: >-
  Generate a Docker Compose deployment for the current project by detecting its
  language stack, runtime, and backing services (Postgres, Redis, etc.). Creates
  or extends compose.yaml, Dockerfiles, and .env.example. Use when the user asks
  for docker compose, containerized deployment, local stack setup, or running the
  app with its dependencies in containers.
---

# Docker Compose Deployment

Generate a **stack-aware** Docker Compose deployment for the project you are in. Infer the app runtime from repo files, add only the backing services the project actually uses, and produce files a developer can run with `docker compose up`.

Pair with the [docker](../docker/SKILL.md) skill to validate and run the stack. Extend existing `compose.yaml` / `docker-compose.yml` and `Dockerfile` when present — do not replace working config without reason.

## Workflow

Copy and track:

```
Compose deploy progress:
- [ ] Stack and services detected
- [ ] Existing Docker/compose config reviewed
- [ ] Dockerfile created or updated (if missing)
- [ ] compose.yaml created or extended
- [ ] .env.example added (no secrets committed)
- [ ] .dockerignore added or updated
- [ ] docker compose config validates
- [ ] Stack starts and app reaches healthy/running state
- [ ] README or docs updated with run commands
```

## Step 1 — Detect stack and services

Scan the repo root and common config paths. Record findings before writing files.

### Application runtime

| Signal | Runtime | Base image hint |
|--------|---------|-----------------|
| `package.json` | Node.js | `node:<LTS>-alpine` |
| `pnpm-lock.yaml` / `yarn.lock` | Node (pnpm/yarn) | same; use matching install in Dockerfile |
| `pyproject.toml` / `requirements*.txt` / `Pipfile` | Python | `python:<version>-slim` |
| `go.mod` | Go | multi-stage: `golang` → `distroless` or `alpine` |
| `Cargo.toml` | Rust | multi-stage: `rust` → `debian:bookworm-slim` |
| `Gemfile` | Ruby | `ruby:<version>-slim` |
| `composer.json` | PHP | `php:<version>-fpm-alpine` or `apache` variant |
| `pom.xml` / `build.gradle*` | Java | multi-stage: `eclipse-temurin` |
| `mix.exs` | Elixir | multi-stage: `elixir` → `debian-slim` |
| Existing `Dockerfile` | Follow it | Reuse base image, stages, and entrypoint |

Read version pins from lockfiles, `.nvmrc`, `.python-version`, `go` directive, or `rust-toolchain.toml` when present.

### Backing services

Infer from dependencies, env vars, and config — add a service only when evidence exists:

| Evidence | Compose service | Default image |
|----------|-----------------|---------------|
| `pg`, `postgres`, `psycopg`, `asyncpg`, `sqlalchemy` + postgres URL, Prisma `postgresql`, `DATABASE_URL` with `postgres` | `db` | `postgres:16-alpine` |
| `mysql`, `mysql2`, `pymysql`, `mariadb` | `db` | `mysql:8` or `mariadb:11` |
| `redis`, `ioredis`, `bull`, `celery` + redis broker, `REDIS_URL` | `redis` | `redis:7-alpine` |
| `mongoose`, `pymongo`, `motor`, `MONGODB_URI` | `mongo` | `mongo:7` |
| `amqp`, `pika`, RabbitMQ in celery config | `rabbitmq` | `rabbitmq:3-management-alpine` |
| `elasticsearch` client, `ELASTICSEARCH_URL` | `elasticsearch` | `elasticsearch:8` (single-node dev) |
| `minio`, S3-compatible local dev | `minio` | `minio/minio` |
| `mailhog`, `smtp` dev, `MAIL_*` local | `mailpit` | `axllent/mailpit` |

Also check: `docker-compose*.yml`, `compose*.yaml`, `.env.example`, `README`, framework configs (`next.config.*`, `django` settings, `config/database.yml`, `application.properties`).

### Deployment shape

| Pattern | Compose approach |
|---------|------------------|
| Single web app | One `app` service |
| API + separate frontend | `api` + `web` services |
| Worker + API | `app` + `worker` (same image, different `command`) |
| Static site (Vite/React build) | Multi-stage Dockerfile; `nginx:alpine` or serve from app |
| Monorepo | Service per deployable package; shared `build.context` with `dockerfile` path |

## Step 2 — Prefer existing config

Before generating new files:

1. **Read** `compose.yaml`, `docker-compose.yml`, `Dockerfile`, `.devcontainer/`, `Makefile` docker targets.
2. **Extend** missing services (e.g. add `db` if app exists but database does not).
3. **Align** env var names and ports with what the app already expects.
4. **Skip** duplicate services or conflicting port mappings.

If compose already runs the full stack, only add what's missing or fix what's broken.

## Step 3 — Generate files

### File layout

```
compose.yaml          # preferred filename (Compose spec)
.env.example          # documented vars, no secrets
.dockerignore         # exclude node_modules, .git, __pycache__, target/, etc.
Dockerfile            # if missing
```

Add `compose.yaml` to `.gitignore` only when the project already gitignores env-specific overrides. **Never** commit `.env` with real secrets.

### compose.yaml conventions

- **Compose spec** — top-level `name:` from repo directory or `package.json` name; use `services:`, `volumes:`, `networks:`.
- **Service names** — short and standard: `app`, `api`, `web`, `worker`, `db`, `redis`.
- **Networking** — default bridge network; services reach each other by service name (`db:5432`, not `localhost`).
- **Persistence** — named volumes for database and object-store data (`db_data`, `redis_data`).
- **Startup order** — `depends_on` with `condition: service_healthy` when healthchecks exist.
- **Ports** — publish app port to host; keep databases internal unless the user needs host access for debugging.
- **Secrets** — `env_file: .env` on app services; document every var in `.env.example`. Use `${VAR:-default}` only for non-secret dev defaults.
- **Profiles** — use `profiles: [dev]` for hot-reload bind mounts and debug tooling; default profile runs production-like images.

### Dockerfile (when missing)

Follow stack-appropriate patterns:

1. **Dependency layer caching** — copy lockfiles/manifests first, install deps, then copy source.
2. **Non-root user** when the base image supports it.
3. **Single responsibility** — app image runs the app; databases use official images, not custom builds.
4. **Expose** the port the app listens on; set `WORKDIR` consistently (`/app` or `/workspace` — match the compose skill used elsewhere in the repo).

See [examples.md](examples.md) for stack-specific Dockerfile and compose templates.

### .env.example

List every variable referenced in compose and app config:

```bash
# Database (used by app service)
POSTGRES_USER=app
POSTGRES_PASSWORD=change-me
POSTGRES_DB=app
DATABASE_URL=postgresql://app:change-me@db:5432/app

# App
PORT=3000
NODE_ENV=development
```

Match names the application already reads. Link `DATABASE_URL` / `REDIS_URL` hostnames to compose service names.

## Step 4 — Validate

Run from the project root:

```bash
docker compose config          # syntax + interpolation
docker compose build           # images build
docker compose up -d           # stack starts
docker compose ps              # services running/healthy
docker compose logs app --tail=50
```

For a quick smoke test, curl the app health or root endpoint. If migrations are required, document or run them:

```bash
docker compose run --rm app <migrate-command>
```

Fix config errors before handing off. Use the [docker](../docker/SKILL.md) skill — do not install runtimes on the host to test.

## Step 5 — Document

Add or update a short section (README or `docs/deployment.md`):

```markdown
## Docker Compose

\`\`\`bash
cp .env.example .env   # edit values
docker compose up -d
docker compose logs -f app
\`\`\`

| Service | URL |
|---------|-----|
| App | http://localhost:3000 |
```

Include migrate/seed commands if the stack needs them.

## Agent Checklist

- [ ] Stack detected from real project files, not assumed
- [ ] Backing services match actual dependencies (no speculative Postgres/Redis)
- [ ] Existing compose/Dockerfile extended rather than clobbered
- [ ] Healthchecks on `db`, `redis`, and other infra services
- [ ] `depends_on` + healthy conditions wire app after infra
- [ ] Named volumes for stateful services
- [ ] `.env.example` documents all required variables
- [ ] No secrets, keys, or real passwords in committed files
- [ ] `.dockerignore` keeps build context small
- [ ] `docker compose config` and `docker compose up` succeed
- [ ] Run commands documented for the user

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Generic compose with every database | Add only services the project uses |
| `localhost` for inter-service URLs | Use compose service names |
| Baking `.env` into the image | `env_file` / environment at runtime |
| Replacing a working compose file | Merge and extend |
| Root + latest tags in production docs | Pin image versions (`postgres:16-alpine`) |
| Publishing DB ports by default | Internal network; expose only for debug |
| One giant Dockerfile for app + db | Official images for infra; Dockerfile for app |
| Skipping validation | Run `docker compose config` and `up` before done |

## Additional Resources

- Stack-specific templates: [examples.md](examples.md)
- Running and testing in containers: [docker](../docker/SKILL.md)
