# GitHub Merge All Examples

## List every open PR

```bash
gh pr list --state open \
  --json number,title,headRefName,isDraft,mergeable,mergeStateStatus,createdAt,url \
  --limit 100
```

## Process one PR end-to-end

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
PR=43

gh pr checkout "$PR"
git fetch origin
git merge "origin/$DEFAULT"

# If conflicts: edit files, then:
git add skill_categories.py README.md
git commit -m "merge: resolve conflicts with origin/$DEFAULT"
git push origin HEAD

python3 scripts/sync_readme_skill_count.py
python3 -m pytest tests/ -q

gh pr checks "$PR" --watch
gh pr ready "$PR"
gh pr merge "$PR" --merge --delete-branch

git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

## Resolve skill_categories.py conflicts (skills repo)

When two branches each add one skill to the same category tuple, keep **both** entries:

```python
# Before (conflict markers removed):
(
    "DevOps & CI",
    (
        "docker",
        "ci-debug",      # from PR A
        "hardware-metrics",  # from PR B
        "dependabot-merge",
    ),
),
```

Then verify:

```bash
python3 -m pytest tests/test_skill_categories.py -q
```

## Re-list after each merge

```bash
gh pr list --state open --json number,title,createdAt -q 'sort_by(.createdAt) | .[] | "#\(.number) \(.title)"'
```

## Skip with comment (optional)

```bash
gh pr comment 125 --body "$(cat <<'EOF'
Skipping auto-merge: required check "deploy" failed with infrastructure error outside this PR's scope.

EOF
)"
```

## Detect merge strategy

```bash
gh pr list --state merged --limit 5 --json number,mergeCommit
# Prefer --squash when squash merges dominate; else --merge
```
