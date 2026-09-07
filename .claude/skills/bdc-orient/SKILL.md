---
name: bdc-orient
description: Orient to the ecosystem state after returning from a break — pull all repos, show recent activity, and surface open issues and PRs.
allowed-tools: Bash(./setup.sh), Bash(git*), Bash(gh*)
---

# Orient

Get a snapshot of the ecosystem state. Run this when returning to the project after a break.

## Step 1: Pull all repos

```bash
./setup.sh
```

## Step 2: Recent activity per repo

For each component repo, show the last 5 commits and working tree status:

```bash
for repo in components/tools-impact-engine-orchestrator components/tools-impact-engine-measure components/tools-impact-engine-evaluate components/tools-impact-engine-allocate; do
    echo "=== $repo ==="
    git -C "$repo" log --oneline -5
    git -C "$repo" status --short
done
```

## Step 3: Open issues and PRs

```bash
for repo in workbench-impact-engine tools-impact-engine-orchestrator tools-impact-engine-measure tools-impact-engine-evaluate tools-impact-engine-allocate; do
    echo "=== $repo ==="
    gh issue list --repo eisenhauerIO/$repo --state open --limit 5
    gh pr list --repo eisenhauerIO/$repo --state open --limit 5
done
```

## Step 4: Report

Summarize in plain text:

- Any repos with uncommitted changes
- Most recent work per repo (from git log)
- Open issues and PRs that need attention

## Usage

- `/bdc-orient` — run from the workspace root
