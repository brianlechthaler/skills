# GitHub Publish Examples

## Bootstrap a new public repo and first PR

```bash
cd my-project
git init
echo "node_modules/" > .gitignore

# Create GitHub repo and remote — do not push project commits to main yet
gh repo create my-project --public --source=. --remote=origin

DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
if [ "$DEFAULT" = "null" ] || [ -z "$DEFAULT" ]; then DEFAULT=main; fi

git fetch origin
if ! git rev-parse --verify "origin/$DEFAULT" >/dev/null 2>&1; then
  git checkout --orphan "$DEFAULT"
  git reset --hard
  git commit --allow-empty -m "Initial commit"
  git push -u origin "$DEFAULT"
fi

# All deliverables go on a feature branch and merge via PR
git checkout -b feat/initial-project origin/$DEFAULT
git add .
git commit -m "Add initial project scaffold"
git push -u origin HEAD

gh pr create --draft \
  --title "Add initial project scaffold" \
  --body "$(cat <<'EOF'
## Summary
- Add project scaffold and configuration

## Test plan
- [ ] `npm test` passes locally
- [ ] CI passes

EOF
)"
```

## Move work off the default branch

You made changes while on `main`:

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

git stash push -u -m "user-auth"
git checkout -b feat/user-auth origin/$DEFAULT
git stash pop
git add -A
git commit -m "Add user authentication with session cookies"
git push -u origin HEAD
```

## Rename or rebase a misaligned feature branch

Work is on `cursor/wip` but should be `fix/session-expiry` based on current main:

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

git stash push -u -m "session-fix"
git checkout -b fix/session-expiry origin/$DEFAULT
git stash pop
git add -A
git commit -m "Fix session expiry handling"
git push -u origin HEAD
```

## Complete all PR todos, run tests, wait for CI, ask to merge

```bash
PR_NUM=$(gh pr view --json number -q .number)

# Run local tests first
npm test
npm run lint

# Update every checklist item in the PR body
gh pr view "$PR_NUM" --json body -q .body > /tmp/pr-body.md
# Edit /tmp/pr-body.md: change all applicable `- [ ]` to `- [x]`
gh pr edit "$PR_NUM" --body-file /tmp/pr-body.md

# Wait for CI
gh pr checks --watch

# Confirm no open checkboxes remain, then ask the user:
# "All local tests and CI checks passed. Approve merge into main?"

# After explicit approval:
gh pr ready
gh pr merge --merge --delete-branch
```

## Connect an existing local repo to GitHub

```bash
git remote -v   # confirm no origin
gh repo create my-existing-app --public --source=. --remote=origin

DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
if [ "$DEFAULT" = "null" ] || [ -z "$DEFAULT" ]; then DEFAULT=main; fi

git fetch origin
if ! git rev-parse --verify "origin/$DEFAULT" >/dev/null 2>&1; then
  git stash push -u -m "publish-work"
  git checkout --orphan "$DEFAULT"
  git reset --hard
  git commit --allow-empty -m "Initial commit"
  git push -u origin "$DEFAULT"
  git checkout -b feat/publish-existing-work origin/$DEFAULT
  git stash pop
else
  git checkout -b feat/publish-existing-work origin/$DEFAULT
fi

git add -A
git commit -m "Add existing application code"
git push -u origin HEAD
gh pr create --draft --title "Add existing application code" --body "..."
```

## Private repo (only when user asks)

```bash
gh repo create internal-tool --private --source=. --remote=origin
# Bootstrap empty default branch if needed, then feature branch + PR (same as public)
```

## Resume work on an existing branch

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git checkout feat/my-feature
git rebase origin/$DEFAULT
# ... finish changes ...
git add -A
git commit -m "Address review feedback"
git push
gh pr view --web
```
