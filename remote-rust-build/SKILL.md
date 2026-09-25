---
name: remote-rust-build
description: >-
  Run cargo build on a remote machine over SSH. If the user names a builder
  host, use that host. If they do not, read ~/.ssh/config, suggest only
  concrete Host entries (skip wildcards and patterns), and ask them to pick
  one before building. Use when the user asks for a remote Rust build, an SSH
  cargo build, or to compile a Rust project on another machine.
---

# Remote Rust Build

Run `cargo build` for the current Rust project on a remote builder over SSH. Use the user's existing SSH config and keys. Do not build until a single concrete host has been named by the user.

For local release profiling after a binary exists, use [compiled-performance](../compiled-performance/SKILL.md). For container builds, use [docker](../docker/SKILL.md).

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| User asks to compile a Rust project on another machine | Local `cargo build` on the machine the agent is already on |
| User asks for a remote builder, SSH cargo build, or remote Rust compile | Docker, CI workflow authoring, or release profiling |
| A `Cargo.toml` project should be built with `cargo build` over SSH | Non-Rust projects |

## Core Rules

1. **Named host wins.** If the user specifies a builder host, use that host. Do not replace it with a different config entry.
2. **No host, no build.** If they do not specify a host, suggest concrete hosts from their SSH config and wait for them to pick one. Never start a build against an unspecified host, and never pick one yourself — including when the config has exactly one host.
3. **Do not invent hosts.** Suggest only names printed by [list_ssh_hosts.py](scripts/list_ssh_hosts.py). Do not add hosts from memory, cloud APIs, or guesses such as `localhost` or `builder`.
4. **Leave SSH alone.** Do not edit SSH config, copy private keys, print key material, or weaken host-key checking.
5. **Build the code they mean.** Sync the local project when they want this working tree built. If they point at an existing remote checkout, build that path and do not overwrite it.

## Workflow

```
Remote Rust build:
- [ ] Host is explicit (user-named, or user picked from the SSH config list)
- [ ] Local Cargo.toml located
- [ ] SSH to that host succeeded without weakening checks
- [ ] Project is on the remote (existing path or sync)
- [ ] cargo build finished and its exit code is reported
```

### 1. Choose the host

Treat a host as specified only when the user gives one concrete host token (an alias or hostname) with no `*`, `?`, or `[`. Vague phrases ("the server", "my builder", "the usual machine") are not a specified host.

**User specified a host** — use it exactly. Do not scan SSH config to override it. If the token is a wildcard or pattern, refuse it and ask for a concrete host.

**User did not specify a host** — run the helper next to this skill (not a copy from the target repo):

```bash
python3 "<this-skill-dir>/scripts/list_ssh_hosts.py"
```

| Exit code | What to do |
|-----------|------------|
| 0 | Show every stdout line and ask the user to pick one host. Stop. Do not build yet. |
| 2 | Config is missing, not a file, or unreadable. Relay stderr. Ask for a host. Do not invent one. |
| 3 | Config has no concrete Host entries. Relay stderr. Ask for a host. Do not invent one. |

The script skips `*` , `?`, `[...]` character classes, and `!` negations. `Host` aliases such as `builder` are real entries; `Host *` and `Host *.internal` are not. `Include` files are read. `Match` blocks are not hosts. Optional `hostname=` on a line is the `HostName` from that block, shown only so the user can choose — connect with the alias, not a name you made up.

If the script cannot be run, read `~/.ssh/config` with the same rules and list only tokens that appear there. Still do not invent hosts.

### 2. Find the Rust project

Start at the working directory and walk parents for `Cargo.toml`. Use that directory as the project root. If none exists, stop and say this is not a Rust project. Do not create a crate. If the user names a manifest path, use that directory instead.

### 3. Connect

Use the user's SSH client and config. Do not pass extra identity files.

```bash
ssh -o BatchMode=yes -- "$HOST" "true"
```

`BatchMode=yes` only stops interactive password prompts so the agent does not hang. It does not disable host-key checks.

| Result | Action |
|--------|--------|
| Success | Continue |
| Permission denied / auth failure | Report it and ask the user to fix SSH access. Do not retry with weaker options. |
| Host key verification failed | Stop. Ask the user to verify the host key themselves. |
| `cargo` missing (`command -v cargo` fails) | Stop and say the remote has no Cargo. Do not install rustup unless the user asks. |

Pass `$HOST` as its own argument. The host must be a single token with no shell metacharacters. If it has spaces, quotes, or characters outside `A-Za-z0-9._:-`, stop and ask for a safer alias.

Forbidden SSH options and actions:

- `StrictHostKeyChecking=no`
- `UserKnownHostsFile=/dev/null`
- `sshpass`, copied `IdentityFile`s, or printing `~/.ssh` private keys
- Editing `~/.ssh/config` or `authorized_keys`

### 4. Put the project on the remote

**User gave a remote directory** — build that path. Quote it. Confirm `Cargo.toml` exists there. Do not rsync over it unless they explicitly ask to sync.

**No remote path** — sync this working tree, then build:

1. Sanitize the project directory basename to `[A-Za-z0-9._-]`. If nothing remains, use `rust-project`.
2. Remote directory: `~/builds/<sanitized>/`.
3. Prefer `rsync` (no `--delete`, no `-L`):

```bash
ssh -o BatchMode=yes -- "$HOST" "mkdir -p ~/builds/${SAFE}"
rsync -a --exclude target --exclude .git \
  -e "ssh -o BatchMode=yes" \
  ./ "${HOST}:builds/${SAFE}/"
```

4. If `rsync` is not installed, stream a tarball of the project root:

```bash
tar -czf - --exclude target --exclude .git . \
  | ssh -o BatchMode=yes -- "$HOST" \
    "mkdir -p ~/builds/${SAFE} && tar -xzf - -C ~/builds/${SAFE}"
```

Sync only the project root. Never sync `$HOME`, `~/.ssh`, or an identity file. Do not use `rsync --delete` unless the user asks.

### 5. Build

Default command is `cargo build` with no extra flags. Append flags the user requested (`--release`, `-p name`) and nothing else.

```bash
ssh -o BatchMode=yes -- "$HOST" "cd ~/builds/${SAFE} && cargo build"
```

For a user-supplied remote path, `cd` to the quoted path instead. Run the command from the directory that contains `Cargo.toml`.

Report the host, remote path, cargo command, and exit code. On failure, show the compiler errors. Do not claim success when cargo exits non-zero, and do not fall back to a local build.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Build as soon as SSH config has a host | Ask the user to pick a host first |
| Suggest `localhost`, a cloud name, or a remembered host | Suggest only script stdout, or ask |
| `ssh -o StrictHostKeyChecking=no` | Keep default host-key checking |
| Copy or print private keys | Use the user's existing SSH config |
| `rsync --delete` onto a path the user did not mean | Sync only `~/builds/<name>/`, or build the path they named |
| Install Rust on the remote without being asked | Report that `cargo` is missing and ask |
| Quietly build locally when SSH fails | Report the SSH or cargo error |

## Examples

Sample SSH configs, skipped patterns, and command sequences: [examples.md](examples.md).
