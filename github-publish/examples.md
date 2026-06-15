# GitHub Publish Examples

## Bootstrap a new public repo and first PR

```bash
cd my-project
git init
echo "node_modules/" > .gitignore
git add .
git commit -m "Initial commit"

gh repo create my-project --public --source=. --remote=origin --push

DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin
git checkout -b feat/user-auth origin/$DEFAULT
# ... make changes ...
git add src/
git commit -m "Add user authentication with session cookies"
git push -u origin HEAD

gh pr create --draft \
  --title "Add user authentication" \
  --body "$(cat <<'EOF'
## Summary
- Add login/logout endpoints and session middleware

## Test plan
- [ ] `npm test` passes locally
- [ ] Manual login/logout smoke test
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
gh repo create my-existing-app --public --source=. --remote=origin --push
```

## Private repo (only when user asks)

```bash
gh repo create internal-tool --private --source=. --remote=origin --push
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
