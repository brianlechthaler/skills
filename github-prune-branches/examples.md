# GitHub Prune Branches Examples

## Full safe prune (merged / closed-PR only)

```bash
gh auth status
git fetch origin --prune

DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
CURRENT=$(git branch --show-current)

# Local branches fully merged into default
git branch --merged "origin/$DEFAULT" --format='%(refname:short)' \
  | grep -v -E "^($DEFAULT|$CURRENT|develop|staging|production)$"

# For each safe local branch:
# git branch -d <branch>

# Remote branches: check PR state, then:
# git push origin --delete <branch>

git fetch origin --prune
```

## List remote branches with last commit age

```bash
git for-each-ref --sort=-committerdate refs/remotes/origin \
  --format='%(committerdate:short) %(refname:short)' \
  | grep -v 'origin/HEAD'
```

## Find squash-merged locals that `-d` will refuse

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

for b in $(git branch --format='%(refname:short)'); do
  [ "$b" = "$DEFAULT" ] && continue
  if ! git merge-base --is-ancestor "$b" "origin/$DEFAULT" 2>/dev/null; then
    state=$(gh pr list --head "$b" --state merged --json number,state -q '.[0].state' 2>/dev/null)
    if [ "$state" = "MERGED" ]; then
      echo "squash-merged candidate: $b"
    fi
  fi
done
```

Then, only for listed candidates the user approved:

```bash
git branch -D <branch>
```

## Delete a remote branch and its local twin

```bash
BRANCH=feat/old-thing
git push origin --delete "$BRANCH" 2>/dev/null || true
git branch -d "$BRANCH" 2>/dev/null || git branch -D "$BRANCH"  # -D only if PR MERGED
git fetch origin --prune
```

## Bulk map branches → latest PR state

```bash
gh pr list --state all --limit 200 \
  --json number,state,headRefName,url \
  -q '.[] | "\(.headRefName)\t\(.state)\t#\(.number)\t\(.url)"'
```

## Protect extra patterns while pruning

Keep anything matching `release/*` or a user keep-list:

```bash
is_protected() {
  case "$1" in
    main|master|develop|staging|production|release|releases) return 0 ;;
    release/*|releases/*|hotfix/*) return 0 ;;
    cursor/keep-*) return 0 ;;  # example user keep-list
    *) return 1 ;;
  esac
}
```

## After github-merge-all

Merge-all often passes `--delete-branch` on merge. Prune afterward to clear **local** leftovers:

```bash
# ... github-merge-all workflow ...
git fetch origin --prune
git branch --merged "origin/$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)" \
  --format='%(refname:short)'
# delete locals with git branch -d
```
