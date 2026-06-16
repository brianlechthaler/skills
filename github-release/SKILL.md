---
name: github-release
description: >-
  Create GitHub releases from the default branch with SemVer tags, Keep a
  Changelog-style release notes, and project-specific deploy instructions.
  Use when the user asks to release, tag, ship, cut a version, publish a
  release, or create a GitHub release with changelog and deployment steps.
---

# GitHub Release

## Core Rules

1. **Release from the default branch only** — tag the tip of `origin/$DEFAULT` after it is up to date with the remote. Never cut a release from a feature branch unless the user explicitly overrides.
2. **Use SemVer** — tags are `vMAJOR.MINOR.PATCH` (e.g. `v1.4.2`). Pre-releases use `-alpha.N`, `-beta.N`, or `-rc.N` suffixes.
3. **Ship a real changelog** — group changes by impact (Added, Changed, Fixed, Breaking, Security). Do not paste raw `git log --oneline` as the release body.
4. **Include deploy instructions** — every release notes body ends with a **Deploy** section tailored to how this project is actually run (Docker, package manager, installer script, static assets, etc.).
5. **Use `gh`** for releases, tags, and repo metadata. Verify auth before starting.

These rules apply unless the user opts out (e.g. "draft only", "don't push tag", specific version override).

## Prerequisites

```bash
gh auth status
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

Fall back to `main` when `defaultBranchRef` is null.

Confirm the release target commit:

```bash
git rev-parse "origin/$DEFAULT"
git log -1 --oneline "origin/$DEFAULT"
```

**Pre-flight checks** (fix or ask before releasing):

| Check | Command / action |
|-------|------------------|
| Default branch exists on remote | `git rev-parse --verify "origin/$DEFAULT"` |
| Working tree clean on default | `git status` on `$DEFAULT` after checkout or compare to `origin/$DEFAULT` |
| CI green (when CI exists) | `gh run list --branch "$DEFAULT" --limit 1` or wait on latest workflow |
| No duplicate tag | `git tag -l "v*"` and `gh release list` |
| Tests pass locally | Run project test/lint commands when available |

Do not release with failing CI or known regressions unless the user explicitly accepts the risk.

## SemVer Policy

Follow [Semantic Versioning 2.0.0](https://semver.org/):

| Bump | When |
|------|------|
| **MAJOR** | Breaking API/behavior changes (`BREAKING CHANGE:` footer, `type!:` or `type(scope)!:` in Conventional Commits) |
| **MINOR** | Backward-compatible features (`feat:`) |
| **PATCH** | Backward-compatible fixes and perf (`fix:`, `perf:`) |

**No user-facing release bump** for `docs:`, `chore:`, `test:`, `ci:`, `build:` unless the user wants a patch release for housekeeping — default is to skip or roll into the next feature/fix release.

### Determine the next version

```bash
LATEST=$(git tag -l 'v*' --sort=-v:refname | head -1)
BASE="${LATEST:-v0.0.0}"
RANGE="${LATEST:+$LATEST..}origin/$DEFAULT"

git log $RANGE --pretty=format:'%s%n%b---'
```

Apply bump rules to commits in `$RANGE`. Parse `vMAJOR.MINOR.PATCH` from `$LATEST` (strip leading `v`).

| Situation | Starting version |
|-----------|------------------|
| No tags yet, production-ready | `v1.0.0` |
| No tags yet, early / unstable | `v0.1.0` |
| Pre-release | `v1.0.0-rc.1`, `v1.0.0-beta.2` |

When ambiguous, propose the computed version and ask the user to confirm before creating the tag.

## Changelog Workflow

Generate release notes in [Keep a Changelog](https://keepachangelog.com/) style. Map Conventional Commits to sections:

| Commit prefix | Section |
|---------------|---------|
| `feat` | ### Added |
| `fix`, `perf` | ### Fixed |
| `refactor`, `chore`, `build`, `ci` (user-visible) | ### Changed |
| `docs` | ### Documentation (omit if trivial) |
| `BREAKING CHANGE` / `!` | ### Breaking Changes |
| Security advisories | ### Security |

### Release notes template

Write to a temp file (e.g. `/tmp/release-notes.md`) and pass to `gh release create`:

```markdown
## What's Changed

### Added
- User-facing feature summary with PR/issue link when available ([#123](https://github.com/OWNER/REPO/pull/123))

### Changed
- Notable behavior or dependency updates

### Fixed
- Bug fix summary

### Breaking Changes
- What broke and how to migrate

### Security
- CVE or vulnerability fixes (if any)

**Full Changelog**: https://github.com/OWNER/REPO/compare/PREV_TAG...vX.Y.Z

---

## Deploy

<!-- Agent: replace this entire section with project-specific steps (see Deploy Detection below) -->

### Prerequisites
- List runtime versions, env vars, and secrets (names only — never values)

### Install / run
- Concrete commands pinned to this release tag or artifact

### Upgrade from previous release
- Migration steps, config changes, database migrations, rollback command

### Verify
- Health check URL, smoke test command, or expected output
```

**Quality bar for changelog entries:**

- One bullet per meaningful change; merge related commits into a single bullet.
- User-facing language — not commit hashes alone.
- Link PRs: `gh pr list --search "merged:>=YYYY-MM-DD"` or parse `(#NNN)` from merge commits.
- Call out migration steps for breaking changes.
- Include contributors when `gh api repos/{owner}/{repo}/contributors` or merge commits make that easy.

### Update `CHANGELOG.md` in the repo (when present)

If the project maintains `CHANGELOG.md` at the repo root:

1. Add a `## [X.Y.Z] - YYYY-MM-DD` section under `[Unreleased]` content.
2. Commit on a `release/vX.Y.Z` branch **or** include in the same release PR workflow the team uses.
3. For this skill's default path (release from default branch): append the new section, commit to `$DEFAULT` only when the user expects changelog-on-main; otherwise note in release body that changelog lives in GitHub Releases only.

Prefer opening a small PR for changelog-only updates when the team uses PR-only merges; if releasing directly from `$DEFAULT`, stage `CHANGELOG.md` before tagging when the user wants it in-tree.

## Deploy Detection

Inspect the repo and fill the **Deploy** section with real commands. Use the first matching profile; combine when the project uses multiple (e.g. Docker + Helm).

| Signal | Deploy content |
|--------|----------------|
| `Dockerfile` + GHCR workflow | `docker pull ghcr.io/OWNER/IMAGE:vX.Y.Z` and `docker run` with required `-e` / `-p` |
| `docker-compose.yml` | `git checkout vX.Y.Z && docker compose up -d` |
| `install.sh` / curl installer (e.g. skills repos) | One-liner pinned to tag: `curl -sL .../install.sh \| bash -s -- --all -y` from `raw.githubusercontent.com/OWNER/REPO/vX.Y.Z/...` |
| `package.json` + npm publish | `npm install PACKAGE@X.Y.Z` |
| `pyproject.toml` / setup.py + PyPI | `pip install PACKAGE==X.Y.Z` |
| Go module + tags | `go install github.com/OWNER/REPO/vX.Y.Z@X.Y.Z` |
| `Chart.yaml` (Helm) | `helm upgrade --install RELEASE ./chart --version X.Y.Z` |
| GitHub Actions release assets / `goreleaser` | Download URL from release assets: `gh release download vX.Y.Z` |
| Static site / no artifact | `git clone` + `git checkout vX.Y.Z` + build/run from README |
| Kubernetes manifests in repo | `kubectl apply -f deploy/` at tag with image tag substitution |

Always pin to the **release tag** (`vX.Y.Z`) or an immutable digest — never `@main` or `@latest` in production deploy steps.

Read `README.md`, `docs/`, and `.github/workflows/` for env vars, ports, and official deploy docs; mirror naming the project already uses.

## Release Workflow

Run sequentially unless noted.

### 1. Sync and verify target

```bash
git fetch origin --tags
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
TARGET_SHA=$(git rev-parse "origin/$DEFAULT")
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
```

Optional — confirm CI on `$TARGET_SHA`:

```bash
gh run list --commit "$TARGET_SHA" --limit 5
```

### 2. Compute version and draft notes

- Determine next SemVer (see above).
- Build `/tmp/release-notes.md` from the template.
- Show the user: version, commit SHA, summary bullets, and deploy section preview.
- **Ask for confirmation** before creating a non-draft release. Proceed without asking only when the user gave an explicit version (e.g. "release v2.1.0").

### 3. Create annotated tag and GitHub release

**Preferred — `gh release create`** (creates tag + release):

```bash
VERSION=vX.Y.Z
gh release create "$VERSION" \
  --target "$DEFAULT" \
  --title "Release $VERSION" \
  --notes-file /tmp/release-notes.md
```

**Draft release** (user asked to review first):

```bash
gh release create "$VERSION" \
  --target "$DEFAULT" \
  --title "Release $VERSION" \
  --notes-file /tmp/release-notes.md \
  --draft
```

**Pre-release:**

```bash
gh release create "$VERSION" ... --prerelease
```

**With binaries** (when the project builds artifacts):

```bash
gh release create "$VERSION" \
  --target "$DEFAULT" \
  --title "Release $VERSION" \
  --notes-file /tmp/release-notes.md \
  dist/myapp-linux-amd64 dist/myapp-darwin-arm64
```

Request `git_write` and network permissions when the environment requires them.

### 4. Post-release

- Return the release URL: `gh release view "$VERSION" --web` or `--json url -q .url`.
- If CI publishes containers on tag push, watch the workflow: `gh run watch`.
- Remind the user to announce breaking changes and run the **Verify** steps from the deploy section.

## Agent Checklist

```
Release workflow:
- [ ] gh authenticated; origin/default branch identified
- [ ] Release target is origin/$DEFAULT at intended SHA
- [ ] Pre-flight checks pass (CI, tests, no duplicate tag)
- [ ] Next SemVer computed from Conventional Commits (user confirmed if ambiguous)
- [ ] Release notes: Added/Changed/Fixed/Breaking/Security + Full Changelog link
- [ ] Deploy section filled from project signals (tag-pinned commands)
- [ ] CHANGELOG.md updated in repo when the project uses one
- [ ] gh release create run (draft/prerelease flags if requested)
- [ ] Release URL and verify steps shared with user
```

## Common Commands

| Goal | Command |
|------|---------|
| Default branch | `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` |
| Latest SemVer tag | `git tag -l 'v*' --sort=-v:refname \| head -1` |
| Commits since tag | `git log v1.0.0..origin/main --oneline` |
| List releases | `gh release list` |
| Create release | `gh release create vX.Y.Z --target main --notes-file notes.md` |
| Draft release | `gh release create vX.Y.Z --draft --notes-file notes.md` |
| Edit release notes | `gh release edit vX.Y.Z --notes-file notes.md` |
| Download assets | `gh release download vX.Y.Z` |
| Delete release (mistake) | `gh release delete vX.Y.Z --yes` (only when user asks) |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Tagging a feature branch | Tag `origin/$DEFAULT` via `--target` |
| `@latest` / `@main` in deploy steps | Pin `vX.Y.Z` or image digest |
| Raw commit dump as changelog | Grouped Keep a Changelog sections with links |
| Skipping deploy instructions | Always include **Deploy** with verify steps |
| Patch bump for every doc commit | Follow SemVer policy; batch docs unless user wants release |
| Duplicate tag / release | Check `git tag -l` and `gh release list` first |
| Secrets in release notes | Name env vars only; link to docs |
| Force-push or retag published releases | Create a new patch version; never rewrite public tags without explicit user approval |

## Additional Resources

- Copy-paste command sequences: [examples.md](examples.md)
