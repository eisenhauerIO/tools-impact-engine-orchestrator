---
name: bdc-orient
description: Orient to the ecosystem state after returning from a break — pull all repos, show recent activity, and surface open issues and PRs.
allowed-tools: Bash(git*), Bash(gh*)
---

# Orient

Get a snapshot of the ecosystem state. Run this when returning to the project after a break.

The four repos are siblings: `../impact-engine-{orchestrator,measure,evaluate,allocate}` relative to the orchestrator.

## Step 1: Pull all repos

```bash
for repo in ../impact-engine-orchestrator ../impact-engine-measure ../impact-engine-evaluate ../impact-engine-allocate; do
    git -C "$repo" pull --ff-only
done
```

## Step 2: Recent activity per repo

For each repo, show the last 5 commits and working tree status:

```bash
for repo in ../impact-engine-orchestrator ../impact-engine-measure ../impact-engine-evaluate ../impact-engine-allocate; do
    echo "=== $repo ==="
    git -C "$repo" log --oneline -5
    git -C "$repo" status --short
done
```

## Step 3: Open issues and PRs

```bash
for repo in workbenches-impact-engine tools-impact-engine-orchestrator tools-impact-engine-measure tools-impact-engine-evaluate tools-impact-engine-allocate; do
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

- `/bdc-orient` — run from the orchestrator repo root
