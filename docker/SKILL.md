---
name: docker
description: >-
  Run all builds, tests, and tooling inside Docker containers with nothing
  installed on the host except Docker. Mount host credentials and SSH keys
  read-only when needed. Clean up ephemeral test containers when finished.
  Use when building, testing, installing dependencies, running linters, CI
  locally, or when the user mentions Docker, containers, or containerized
  workflows.
---

# Containerized Docker Workflow

## Core Rules

1. **Containers for everything** — build, test, lint, format, and run all project tooling inside containers.
2. **Nothing on the host** — do not install languages, package managers, or project dependencies on the host. The only assumed host tools are `docker` and `docker compose`.
3. **Mount secrets, don't copy** — bind-mount credentials and SSH keys from the host read-only; never bake them into images.

When the user asks to run a command that normally requires a local toolchain, translate it to a container equivalent first.

## Decision Flow

```
Need to build / test / install / lint / run?
  → Use existing Dockerfile or compose service if present
  → Else create a minimal Dockerfile or compose service, then run in container
  → Never fall back to host install (npm install, pip install, apt, brew, etc.)
```

## Prefer Existing Project Setup

Before creating new container config, check for:

| File | Use for |
|------|---------|
| `docker-compose.yml` / `compose.yaml` | Dev, test, and CI services |
| `Dockerfile` / `Dockerfile.*` | Build and one-off runs |
| `.devcontainer/` | VS Code / Cursor dev container config |
| `Makefile` with `docker-*` targets | Project-specific container commands |

Reuse and extend existing services rather than inventing parallel workflows.

## Standard Patterns

### One-off command (no compose yet)

```bash
docker run --rm -it \
  -v "$(pwd):/workspace" \
  -w /workspace \
  image:tag \
  command args
```

### Compose service (preferred for recurring work)

```bash
docker compose run --rm service-name command args
docker compose up --build service-name
```

### Interactive dev shell

```bash
docker compose run --rm service-name bash
# or
docker run --rm -it -v "$(pwd):/workspace" -w /workspace image:tag bash
```

Always use `--rm` for ephemeral tasks. Mount the project at a fixed path (`/workspace` is the default convention).

## Cleanup Ephemeral Containers

When you finish testing or one-off container work, remove any temporary containers you created. Do not leave stopped or idle test containers behind.

**Prevention (preferred):**
- Use `--rm` on `docker run` and `docker compose run` so containers auto-remove on exit.
- Avoid `-d` / detached mode for short test runs unless you will explicitly clean up afterward.

**After testing, clean up anything still running or stopped:**

```bash
# List containers from this session (note names/IDs before removing)
docker ps -a

# Stop and remove specific containers you started
docker stop <container-id-or-name>
docker rm <container-id-or-name>

# Remove one-off compose containers (service name from your compose file)
docker compose rm -f -s -v service-name

# If you started detached containers and lost track of IDs, remove exited containers
docker container prune -f
```

Only prune or bulk-remove containers you created for the current task. Do not remove unrelated long-lived dev containers, databases, or services the user is actively using unless they ask.

If a test fails mid-run and leaves a container behind, clean it up before moving on or ending the session.

## Credential and SSH Mounts

Mount host paths **read-only** (`:ro`). Only mount what the task requires.

| Need | Typical mount |
|------|---------------|
| Git over SSH | `-v "$HOME/.ssh:/root/.ssh:ro"` or map to container user home |
| AWS | `-v "$HOME/.aws:/root/.aws:ro"` |
| GCP | `-v "$HOME/.config/gcloud:/root/.config/gcloud:ro"` |
| Azure | `-v "$HOME/.azure:/root/.azure:ro"` |
| npm/yarn/pip tokens | `-v "$HOME/.npm:/root/.npm:ro"` or env file mount |
| Generic env secrets | `--env-file .env` (file stays on host, not in image) |
| Docker socket (build images in CI container) | `-v /var/run/docker.sock:/var/run/docker.sock` |

Example with credentials:

```bash
docker run --rm -it \
  -v "$(pwd):/workspace" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$HOME/.aws:/root/.aws:ro" \
  -w /workspace \
  image:tag \
  command args
```

In compose, use bind mounts under `volumes:` — same `:ro` rule applies.

**Never:**
- `COPY` or `ADD` private keys, tokens, or `.env` into a Dockerfile
- Commit credentials to the image or repo
- Run containers as root with writable secret mounts unless required

## Common Task Translations

| Host habit (don't do) | Container approach |
|-----------------------|-------------------|
| `npm install && npm test` | `docker compose run --rm node npm test` (install in image or entrypoint) |
| `pip install -r requirements.txt && pytest` | `docker compose run --rm python pytest` |
| `cargo build && cargo test` | `docker compose run --rm rust cargo test` |
| `go test ./...` | `docker compose run --rm go go test ./...` |
| `make test` (needs local tools) | Add `make docker-test` or document compose equivalent |

Dependencies belong in the **image** (Dockerfile `RUN install...`) or a **dedicated install step inside the container**, not on the host.

## Adding Container Support to a Project

When no container setup exists:

1. **Dockerfile** — base image matching the project's language/runtime; copy dependency manifests first for layer caching; install deps with `RUN`; set `WORKDIR /workspace`.
2. **compose.yaml** — define `build`, `test`, and `dev` services; mount source read-write for dev; use read-only secret mounts.
3. **Document** — add a short "Development" section showing the 2–3 commands developers need.

Minimal compose example:

```yaml
services:
  dev:
    build: .
    volumes:
      - .:/workspace
      - ${HOME}/.ssh:/root/.ssh:ro
    working_dir: /workspace

  test:
    build: .
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: make test
```

## Agent Behavior Checklist

When working in a containerized project:

- [ ] Run installs, builds, and tests via `docker` / `docker compose`, not host commands
- [ ] Check for existing Dockerfile or compose before proposing new ones
- [ ] Mount credentials read-only; use `--env-file` for secrets
- [ ] Use `--rm` for one-off containers
- [ ] Clean up ephemeral test containers when finished (stop/rm, or `docker compose rm`, or `docker container prune -f` for exited leftovers)
- [ ] Fix failing container commands (Dockerfile, compose, mounts) — do not bypass with host installs
- [ ] If Docker is unavailable on the host, say so; do not silently install tools locally

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| `curl \| bash` on host for runtimes | Use an official base image |
| `brew install`, `apt install` on host for project deps | Add to Dockerfile |
| Copying `.ssh/id_rsa` into repo or image | Bind-mount `:ro` at runtime |
| "Just run it locally this once" | One-off `docker run` with same mounts |
| Leaving stopped test containers around | Use `--rm`; run cleanup before ending the task |
| Polling host `node -v` / `python --version` | Check versions inside the container |
