# Remote Rust Build Examples

## SSH config suggestions

Config (`~/.ssh/config`):

```
Host *
  User dev

Host *.internal builder-?
  User dev

Include config.d/*.conf

Host builder
  HostName build-01.example.com

Host github.com
  HostName github.com
  User git
```

`config.d/lab.conf`:

```
Host lab-box
  HostName 10.1.2.3
```

`python3 scripts/list_ssh_hosts.py` prints only:

```
lab-box hostname=10.1.2.3
builder hostname=build-01.example.com
github.com
```

Skipped: `*`, `*.internal`, `builder-?`. `github.com` is listed because it is a concrete `Host` entry; the user decides whether it is the builder. Do not drop it and do not add hosts that are not in the file.

Show that list and ask which host to use. Do not run `cargo build` until they answer.

## Missing config

If `~/.ssh/config` does not exist, the helper exits 2 and stderr says the config was not found and to ask for a builder host. Say that, and ask for a host. Do not use `localhost`.

## Specified host

User: "cargo build on host `lab-box`".

Use `lab-box` even if other hosts exist. Do not re-prompt.

```bash
SAFE=my-crate
HOST=lab-box
ssh -o BatchMode=yes -- "$HOST" "mkdir -p ~/builds/${SAFE}"
rsync -a --exclude target --exclude .git \
  -e "ssh -o BatchMode=yes" \
  ./ "${HOST}:builds/${SAFE}/"
ssh -o BatchMode=yes -- "$HOST" "cd ~/builds/${SAFE} && cargo build"
```

## Existing remote checkout

User: "on `builder`, run cargo build in `/srv/app`".

Do not rsync. Confirm the manifest, then build:

```bash
ssh -o BatchMode=yes -- builder "test -f /srv/app/Cargo.toml && cd /srv/app && cargo build"
```
