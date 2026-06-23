# GitHub Issues Examples

## List and inspect open issues

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

gh issue list --state open \
  --json number,title,labels,assignees,createdAt,url \
  --limit 100

gh issue view 42 --json title,body,labels,comments,state,url
```

## Triage: duplicate and already-fixed

```bash
# Find similar issues
gh issue list --state all --search "in:title session null" --json number,title,state,url

# Close duplicate
gh issue comment 43 --body "Duplicate of #42. Tracking fix there."
gh issue close 43

# Close already fixed
gh issue comment 10 --body "Fixed on \`main\` in abc1234 — null check added in session middleware."
gh issue close 10
```

## Full cycle for one issue

```bash
ISSUE=42
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

# 1. Announce
gh issue comment "$ISSUE" --body "Starting work — opening a draft PR shortly."

# 2. Branch from default
git fetch origin
git checkout "$DEFAULT" && git pull origin "$DEFAULT"
git checkout -b "fix/issue-${ISSUE}-null-session"

# 3. Implement, commit, push (after tests/lint)
git add src/session.ts tests/test_session.ts
git commit -m "$(cat <<'EOF'
fix: guard against null session in middleware

EOF
)"
git push -u origin HEAD

# 4. Draft PR linked to issue
gh pr create --draft \
  --title "Fix null session handling (#42)" \
  --body "$(cat <<'EOF'
## Summary
- Add null guard in session middleware before property access

Fixes #42

## Test plan
- [x] `pytest tests/test_session.py`
- [x] CI passes

EOF
)"

PR_URL=$(gh pr view --json url -q .url)
gh issue comment "$ISSUE" --body "Draft PR: $PR_URL"

# 5. Wait for CI
gh pr checks --watch

# 6. After user approves merge
gh pr ready
gh pr merge --merge --delete-branch

git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

## Comment templates

**Starting work:**

```bash
gh issue comment <n> --body "Starting work on this — branch \`fix/issue-<n>-<slug>\` and draft PR incoming."
```

**Blocked:**

```bash
gh issue comment <n> --body "Blocked: need confirmation on <specific question> before I can proceed."
```

**PR ready for review:**

```bash
gh issue comment <n> --body "Draft PR ready for review: <url>. Waiting for CI and merge approval."
```

## Process multiple issues (sequential — agent validates each)

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

while read -r issue; do
  echo "=== Issue #$issue ==="
  gh issue view "$issue" --json title,labels -q '"\(.title) labels=\([.labels[].name] | join(","))"'
  # Agent: triage → comment → branch → fix → draft PR → CI → ask merge → close
  # Return to default before next iteration
  git checkout "$DEFAULT" && git pull origin "$DEFAULT"
done < <(gh issue list --state open --json number -q '.[].number')
```

## Check for existing PRs on an issue

```bash
gh pr list --search "fixes #42" --state open --json number,title,url
gh issue view 42 --json timelineItems   # when available; otherwise search PR bodies
```

## Re-sync issue branch with default

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin
git merge "origin/$DEFAULT"
# resolve conflicts, run tests, push
git push origin HEAD
gh pr checks --watch
```
