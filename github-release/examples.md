# GitHub Release Examples

## Standard release from default branch

```bash
git fetch origin --tags
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
TARGET=$(git rev-parse "origin/$DEFAULT")

LATEST=$(git tag -l 'v*' --sort=-v:refname | head -1)
echo "Latest tag: ${LATEST:-none}"
echo "Target: $TARGET on $DEFAULT"

# Review commits since last tag, compute next SemVer, draft /tmp/release-notes.md
git log ${LATEST:+$LATEST..}origin/$DEFAULT --oneline

VERSION=v1.2.0   # after SemVer analysis + user confirmation

cat > /tmp/release-notes.md <<EOF
## What's Changed

### Added
- Add GitHub release skill with SemVer and deploy instructions ([#42](https://github.com/$REPO/pull/42))

### Fixed
- Correct install path on Windows PowerShell

**Full Changelog**: https://github.com/$REPO/compare/${LATEST:-v0.0.0}...$VERSION

---

## Deploy

### Prerequisites
- Cursor, Claude Code, or another supported agent tool

### Install from this release
\`\`\`bash
curl -sL https://raw.githubusercontent.com/$REPO/$VERSION/install.sh | bash -s -- --all -y
\`\`\`

### Upgrade
Re-run the installer; symlinks update when installing from a local clone at \`$VERSION\`.

### Verify
\`\`\`bash
./install.sh --list
ls ~/.cursor/skills/github-release/SKILL.md
\`\`\`
EOF

gh release create "$VERSION" \
  --target "$DEFAULT" \
  --title "Release $VERSION" \
  --notes-file /tmp/release-notes.md

gh release view "$VERSION" --json url -q .url
```

## First release (no existing tags)

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
VERSION=v1.0.0   # or v0.1.0 for early/unstable projects

# Commits for entire default branch history
git log origin/$DEFAULT --oneline

# Full Changelog link uses only the new tag (no compare base)
# https://github.com/OWNER/REPO/releases/tag/v1.0.0

gh release create "$VERSION" \
  --target "$DEFAULT" \
  --title "Release $VERSION" \
  --notes-file /tmp/release-notes.md
```

## Docker / GHCR project

Release notes deploy section example:

```markdown
## Deploy

### Prerequisites
- Docker 24+
- `DATABASE_URL` and `REDIS_URL` environment variables

### Pull and run
```bash
docker pull ghcr.io/myorg/myapp:v2.3.1
docker run -d --name myapp \
  -p 8080:8080 \
  -e DATABASE_URL \
  -e REDIS_URL \
  ghcr.io/myorg/myapp:v2.3.1
```

### Upgrade from v2.3.0
```bash
docker pull ghcr.io/myorg/myapp:v2.3.1
docker stop myapp && docker rm myapp
# re-run docker run with same env vars
```

### Verify
```bash
curl -sf http://localhost:8080/health
```
```

After tag push, watch the container publish workflow:

```bash
gh run list --workflow=container.yml --limit 1
gh run watch
```

## Draft release for review

```bash
gh release create v3.0.0-rc.1 \
  --target main \
  --title "Release v3.0.0-rc.1" \
  --notes-file /tmp/release-notes.md \
  --draft \
  --prerelease

# User approves → publish
gh release edit v3.0.0-rc.1 --draft=false
```

## Release with binary assets

```bash
make build-all   # produces dist/myapp-linux-amd64, etc.

gh release create v1.0.0 \
  --target main \
  --title "Release v1.0.0" \
  --notes-file /tmp/release-notes.md \
  dist/myapp-linux-amd64 \
  dist/myapp-darwin-arm64 \
  dist/myapp-windows-amd64.exe
```

Deploy section for asset-based releases:

```markdown
## Deploy

### Download
```bash
gh release download v1.0.0 --pattern 'myapp-linux-amd64' --clobber
chmod +x myapp-linux-amd64
./myapp-linux-amd64 --version
```
```

## SemVer bump from commits

Commits since `v1.4.2`:

```
feat(api): add pagination to list endpoint
fix(auth): expire sessions after idle timeout
feat!: remove legacy /v1 routes
docs: update README install section
```

Result: **v2.0.0** (breaking `feat!` overrides minor bump from other `feat`).

Only fixes since `v2.0.0`:

```
fix(ui): button alignment on mobile
chore: bump dev dependency
```

Result: **v2.0.1** (`chore` alone would not trigger a release unless user requests).

## Update CHANGELOG.md before release

```bash
# Append to CHANGELOG.md (Keep a Changelog format)
cat >> CHANGELOG.md <<'EOF'

## [1.2.0] - 2025-06-15

### Added
- GitHub release skill

### Fixed
- Windows install path
EOF

git add CHANGELOG.md
git commit -m "docs: add changelog for v1.2.0"
git push origin main

# Then create the release (notes can mirror CHANGELOG section)
gh release create v1.2.0 --target main --notes-file /tmp/release-notes.md
```
