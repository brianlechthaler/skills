# GitHub Login Examples

## Already logged in — check only, do not ask

```bash
gh auth status
```

Example success:

```
github.com
  ✓ Logged in to github.com account alice (keyring)
  - Active account: true
```

Continue the original task. Do not ask the user to authenticate to GitHub.

## Not logged in — check, then ask

```bash
gh auth status
```

Example failure (non-zero exit):

```
You are not logged into any GitHub hosts. To log in, run: gh auth login
```

Ask the user to authenticate to GitHub. After they agree:

```bash
gh auth login
gh auth status
```

Stop until the second status check succeeds.

## gh missing — do not ask to authenticate yet

```bash
gh --version
```

If this fails, tell the user to install GitHub CLI from https://cli.github.com/. Run `gh auth status` only after `gh` works.
