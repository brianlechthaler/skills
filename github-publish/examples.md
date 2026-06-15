# GitHub Publish Examples

## Bootstrap a new public repo and first PR

```bash
cd my-project
git init
echo "node_modules/" > .gitignore
git add .
git commit -m "Initial commit"

gh repo create my-project --public --source=. --remote=origin --push

git checkout -b feat/user-auth
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
- [x] `npm test` passes locally
- [x] Manual login/logout smoke test
- [ ] Deploy to staging (needs user)

EOF
)"
```

## Connect an existing local repo to GitHub

```bash
git remote -v   # confirm no origin
gh repo create my-existing-app --public --source=. --remote=origin --push
```

## Update PR checklist after CI passes

```bash
PR_NUM=$(gh pr view --json number -q .number)
gh pr view "$PR_NUM" --json body -q .body > /tmp/pr-body.md
# Edit /tmp/pr-body.md: change `- [ ] CI green` to `- [x] CI green`
gh pr edit "$PR_NUM" --body-file /tmp/pr-body.md
gh pr checks
```

## Private repo (only when user asks)

```bash
gh repo create internal-tool --private --source=. --remote=origin --push
```

## Resume work on an existing branch

```bash
git fetch origin
git checkout feat/my-feature
# ... finish changes ...
git add -A
git commit -m "Address review feedback"
git push
gh pr view --web
```
