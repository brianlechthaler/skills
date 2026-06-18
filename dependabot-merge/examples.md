# Dependabot Merge Examples

## List and inspect open Dependabot PRs

```bash
gh pr list --author "app/dependabot" --state open \
  --json number,title,headRefName,labels,createdAt,url

gh pr view 42 --json title,body,mergeable,mergeStateStatus,statusCheckRollup,files
```

## Check out, test, fix, merge one PR

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
PR=42

gh pr checkout "$PR"
npm ci
npm test
npm run lint

# After fixing breakage:
git add src/api/client.ts
git commit -m "fix: adapt API client for axios 1.x interceptors"
git push origin HEAD

gh pr checks "$PR" --watch
gh pr merge "$PR" --merge --delete-branch

git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

## Rebase a stale Dependabot branch onto default

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin
git merge "origin/$DEFAULT"
# resolve conflicts, run tests
git push origin HEAD
gh pr checks --watch
```

## Process all open Dependabot PRs (shell loop — agent still validates each)

Use only as a scaffold; the agent must still assess, test, fix, and skip unsafe PRs individually.

```bash
while read -r pr; do
  echo "=== PR #$pr ==="
  gh pr view "$pr" --json title,mergeable -q '"\(.title) mergeable=\(.mergeable)"'
  # Agent: checkout → test → fix → merge or skip
done < <(gh pr list --author "app/dependabot" --state open --json number -q '.[].number')
```

## Detect merge strategy from recent PRs

```bash
gh pr list --state merged --limit 5 --json mergeCommit,title
# If merge commits are single-parent squash messages, prefer --squash
```

## Security PRs first

```bash
gh pr list --author "app/dependabot" --label security --state open \
  --json number,title,url
```

## Skip with a comment (optional)

```bash
gh pr comment 125 --body "$(cat <<'EOF'
Skipping auto-merge: webpack 4 → 5 requires a full config migration tracked separately.

EOF
)"
```
