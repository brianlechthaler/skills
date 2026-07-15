---
name: cloud-init
description: >-
  Generate cloud-init user-data for server provisioning on Ubuntu, Debian,
  Rocky/Alma/RHEL, Amazon Linux, and other cloud-init-capable images. Creates
  #cloud-config for users, SSH, packages, files, services, and first-boot
  deploy steps. Use when the user asks for cloud-init, user-data, NoCloud,
  cloud-config, or first-boot server setup for VPS or cloud VMs.
---

# Cloud-Init Deployment

Generate a **valid `#cloud-config` user-data file** for deploying an app or hardening a fresh VM on cloud-init-capable server images. Prefer Ubuntu LTS defaults unless the user names another OS. Produce files ready for cloud providers, Terraform, Multipass, or NoCloud (USB/ISO).

Cloud-init runs **once at first boot** (unless modules are marked `always`). Keep secrets out of committed files — use placeholders, instance metadata, or secret mounts.

## When This Applies

| Use this skill | Skip |
|----------------|------|
| First-boot VM / VPS provisioning | Pure Docker Compose local stacks (use [compose-deploy](../compose-deploy/SKILL.md)) |
| `user-data`, `#cloud-config`, NoCloud seed | Host package installs without cloud-init |
| SSH user, packages, systemd units on a new server | Kubernetes manifests or Helm charts |
| Terraform / cloud `user_data` for Ubuntu et al. | Desktop/laptop Ansible-only plays with no cloud-init |

When the user wants containers **and** a VM bootstrap, generate cloud-init that installs Docker (or pulls compose) and pair with [compose-deploy](../compose-deploy/SKILL.md) / [docker](../docker/SKILL.md).

## Workflow

Copy and track:

```
Cloud-init progress:
- [ ] Target OS and cloud/provider confirmed
- [ ] App/runtime needs detected from project (if in a repo)
- [ ] Existing cloud-init / Terraform user_data reviewed
- [ ] user-data (#cloud-config) written
- [ ] Optional: meta-data / network-config for NoCloud
- [ ] Secrets documented as placeholders (never committed)
- [ ] YAML / cloud-init schema sanity-checked
- [ ] Deploy / attach instructions documented
```

## Step 1 — Confirm OS and delivery method

### Popular cloud-init server images

| Family | Typical images | Package tool | Notes |
|--------|----------------|--------------|-------|
| **Ubuntu** (default) | 22.04 / 24.04 LTS cloud images | `apt` | Best cloud-init coverage; prefer LTS |
| **Debian** | 12 (bookworm) cloud | `apt` | Same apt patterns as Ubuntu |
| **Rocky / Alma / RHEL** | 8 / 9 | `dnf` | Use `packages:` with dnf names; SELinux often Enforcing |
| **Amazon Linux** | AL2023 | `dnf` | AWS-tuned; prefer SSM/IMDS over baked keys when on AWS |
| **openSUSE / SLES** | Leap / SLES cloud | `zypper` | cloud-init supported on cloud images |

If the user does not specify an OS, **generate for Ubuntu 24.04 LTS** and note how to adapt package names for RHEL-family.

### Delivery methods

| Method | Files to produce |
|--------|------------------|
| Cloud provider / Terraform `user_data` | Single `#cloud-config` blob (or gzip+base64 where required) |
| Multipass / LXD | `user-data` file passed at launch |
| NoCloud (bare metal / local hypervisor) | `user-data` + `meta-data` (+ optional `network-config`) on seed ISO/CIDATA |
| cloud-init status debug | Same `user-data`; document `cloud-init status --wait` and `/var/log/cloud-init-output.log` |

## Step 2 — Detect what to install

When working inside an application repo, scan before writing config (same signals as [compose-deploy](../compose-deploy/SKILL.md)):

| Signal | cloud-init implication |
|--------|------------------------|
| `package.json` / `pyproject.toml` / `go.mod` / etc. | Install runtime packages or Docker; write app unit or compose |
| `Dockerfile` / `compose.yaml` | Prefer Docker Engine + Compose plugin on the VM |
| Existing `cloud-init*`, `user-data*`, Terraform `user_data` | Extend — do not clobber working SSH/users |
| `.env.example` | Map into `write_files` or systemd `EnvironmentFile=` with placeholders |

Ask only when OS, SSH key, or hostname cannot be inferred and defaults would lock the user out.

## Step 3 — Prefer existing config

1. **Read** `cloud-init.yaml`, `user-data`, `user-data.yml`, Terraform/Pulumi `user_data`, Packer builders.
2. **Extend** missing packages, files, and units.
3. **Preserve** existing `users:`, SSH keys, and vendor datasource settings.
4. **Never** replace a known-working `users:` / `ssh_authorized_keys` block without an equivalent access path.

## Step 4 — Write `#cloud-config`

### Required shape

Start with the magic header (required):

```yaml
#cloud-config
```

Use **YAML 1.1-compatible** types. Prefer lists of packages and explicit boolean `true`/`false`. Put long scripts in `write_files:` + `runcmd:`, not giant inline one-liners.

### File layout (project convention)

```
cloud-init/user-data          # preferred: #cloud-config
cloud-init/meta-data          # NoCloud: instance-id + local-hostname
cloud-init/network-config     # optional NoCloud v2 networking
```

Or a single root `user-data` / `cloud-init.yaml` when the project already uses that name. Document the exact path in the README.

### Core modules (use what you need)

| Module | Purpose |
|--------|---------|
| `hostname` / `fqdn` | Identity |
| `users` + `ssh_authorized_keys` | Non-root login; lock password auth when keys exist |
| `package_update` / `package_upgrade` / `packages` | OS packages |
| `write_files` | Configs, systemd units, app env files (mode/owner) |
| `bootcmd` | Very early commands (rare; prefer `runcmd`) |
| `runcmd` | First-boot shell commands after packages |
| `timezone` / `locale` | Regional defaults |
| `growpart` / `resize_rootfs` | Expand root disk on cloud volumes |
| `runcmd` + systemd | Enable lingering services / timers |

### Ubuntu / Debian packages (defaults)

Common baseline:

```yaml
package_update: true
package_upgrade: true
packages:
  - ca-certificates
  - curl
  - gnupg
  - unattended-upgrades
```

Add stack packages only with evidence (`nginx`, `python3`, `nodejs` from NodeSource/snap only when justified). Prefer **Docker** for app runtimes when the repo already containerizes.

### RHEL-family / Amazon Linux package notes

- Use `dnf` package names (`python3`, `nginx`, not Debian-only names).
- Firewall: `firewalld` instead of `ufw`.
- SELinux: keep Enforcing; use proper contexts or document `semanage` when writing nonstandard ports/paths.
- EPEL only when required packages need it.

### Safe SSH user pattern

```yaml
users:
  - default
  - name: deploy
    groups: [sudo]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_WITH_YOUR_KEY
```

- Keep `default` on Ubuntu cloud images unless the user wants a single custom user.
- **Never** commit real private keys. Public keys only; placeholder comments if unknown.
- Prefer `ssh_pwauth: false` when keys are provided.

### App deploy patterns

| Goal | Approach |
|------|----------|
| Run containerized app | Install Docker + Compose; `write_files` compose + env; `runcmd` `docker compose up -d` |
| Bare systemd service | Install runtime packages; `write_files` unit under `/etc/systemd/system/`; `systemctl enable --now` via `runcmd` |
| Static / reverse proxy | `nginx` or Caddy package + `write_files` site config |
| One-shot bootstrap script | `write_files` to `/usr/local/bin/bootstrap.sh` + `runcmd` |

See [examples.md](examples.md) for full Ubuntu, Debian, Rocky, and Amazon Linux templates.

## Step 5 — Validate

When `cloud-init` CLI is available (Ubuntu container or host):

```bash
# Schema / configure dry concepts (version-dependent)
cloud-init schema --config-file cloud-init/user-data
```

Always verify YAML parses (strip the non-YAML magic header first):

```bash
python3 - <<'PY'
from pathlib import Path
path = Path("cloud-init/user-data")
text = path.read_text()
assert text.startswith("#cloud-config"), "missing #cloud-config header"
body = text.split("\n", 1)[1]
try:
    import yaml
    yaml.safe_load(body)
except ImportError:
    # Fallback: structural checks only
    assert ":" in body
print("ok")
PY
```

Prefer a small Ubuntu container for schema checks when Docker is available ([docker](../docker/SKILL.md)):

```bash
docker run --rm -v "$PWD/cloud-init:/data:ro" ubuntu:24.04 \
  bash -lc 'apt-get update -qq && apt-get install -y -qq cloud-init >/dev/null && cloud-init schema --config-file /data/user-data'
```

If schema tool is unavailable, still verify:

1. File starts with `#cloud-config`
2. YAML parses
3. No real secrets committed
4. At least one SSH access path exists for the intended admin user

On a live instance after launch:

```bash
cloud-init status --wait
sudo tail -n 100 /var/log/cloud-init-output.log
```

## Step 6 — Document attach / launch

Add a short README section, e.g.:

```markdown
## Cloud-init

\`\`\`bash
# Multipass
multipass launch 24.04 --name app --cloud-init cloud-init/user-data

# cloud-localds (NoCloud seed)
cloud-localds seed.img cloud-init/user-data cloud-init/meta-data
\`\`\`

Replace `ssh_authorized_keys` before launch. On AWS/GCP/Azure, paste `user-data` into the instance metadata / Terraform `user_data` field.
```

## Agent Checklist

- [ ] `#cloud-config` header present
- [ ] Target OS explicit (default Ubuntu LTS) with package-manager-correct packages
- [ ] SSH key placeholders or user-supplied public keys — no private keys
- [ ] Existing user-data extended when present
- [ ] App install path matches repo (Docker vs packages vs systemd)
- [ ] `write_files` use correct `permissions` / `owner`
- [ ] No secrets in git; `.env` values are placeholders
- [ ] Validation attempted (schema or YAML parse)
- [ ] Launch / attach commands documented

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Missing `#cloud-config` header | First line must be `#cloud-config` |
| Baking passwords or API tokens into user-data in git | Placeholders + secret manager / metadata / `smcli` |
| Only password auth with no key | `ssh_authorized_keys` + `ssh_pwauth: false` |
| Debian package names on Rocky/AL2023 | Map to `dnf` packages per OS table |
| Huge unreproducible `runcmd` scripts | `write_files` + small `runcmd` |
| Assuming cloud-init re-runs every boot | Document first-boot; use `cloud_final_modules` / frequency only when required |
| Disabling SELinux to "make it work" | Fix contexts/ports or stay on Ubuntu if SELinux is out of scope |
| Replacing vendor `users: [default]` blindly | Keep `default` or ensure equivalent console/SSH access |

## Additional Resources

- OS templates: [examples.md](examples.md)
- Containerized app on the VM: [compose-deploy](../compose-deploy/SKILL.md), [docker](../docker/SKILL.md)
