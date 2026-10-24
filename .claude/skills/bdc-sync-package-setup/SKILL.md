---
name: bdc-sync-package-setup
description: Synchronize a specific config aspect across all impact-engine packages.
argument-hint: [aspect] [package]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls*), Bash(git*), Bash(diff*)
---

# Sync Package Setup

Synchronize a specific configuration aspect across all (or a selected) impact-engine packages. Each aspect has a canonical template; this skill reads the canonical value, compares against the target, shows the diff, and applies changes per package.

## Step 0: Parse arguments

The user provides: `{aspect}` and optionally `{package}`

- `ASPECT`: One of the supported aspects (see table below)
- `PACKAGE`: Optional — limit to a single package (e.g., `measure`, `evaluate`). If omitted, apply to all 4 packages.

If no aspect is provided, list the available aspects and ask the user to choose.

## Supported Aspects

| Aspect | What it aligns | Canonical source |
|--------|---------------|-----------------|
| `ruff` | `[tool.ruff]` section in `pyproject.toml` | Step 2 below |
| `pre-commit` | `.pre-commit-config.yaml` | Step 2 below |
| `ci` | `.github/workflows/ci.yaml` | Step 2 below |
| `docs-ci` | `.github/workflows/docs.yaml` | Step 2 below |
| `claude-md` | `CLAUDE.md` section headings | bdc-engagement CLAUDE schema |
| `readme` | `README.md` structure and content | Canonical template in `.claude/templates/readme.md` |

## Step 1: Locate packages

The packages are sibling repos, relative to the orchestrator repo root (`git -C <repo> pull` each first):

- `../impact-engine-orchestrator`
- `../impact-engine-measure`
- `../impact-engine-evaluate`
- `../impact-engine-allocate`

If `{package}` was specified, filter to just that one.

## Step 2: Define canonical value

For each aspect, the canonical configuration is:

### `ruff`

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["D", "E", "F", "I"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"
```

### `pre-commit`

Required hooks: `nbstripout`, `check-added-large-files` (500kb), `check-merge-conflict`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `ruff` (lint + format), `pytest` (local hook, `hatch run test`).

### `ci`

- File: `.github/workflows/ci.yaml`
- Trigger: push/PR to main
- Matrix: Python 3.10, 3.11, 3.12 on ubuntu-latest (`requires-python = ">=3.10"`); orchestrator: 3.11, 3.12 (`>=3.11`, 3.10 dropped 2026-09)
- Steps: install hatch, `hatch run lint`, `hatch run test`

### `docs-ci`

- File: `.github/workflows/docs.yaml`
- Trigger: push to main
- Steps: install hatch, `hatch run docs:build`

### `claude-md`

Headings follow the bdc-engagement CLAUDE schema: Project overview, Development setup, Common commands, Architecture, Design record (optional), Verification, Key conventions. Content stays repo-specific.

### `readme`

Canonical README structure for all four packages.

Checks:
- Title format: `# Impact Engine — {Stage}` (em dash, title case stage name)
- Badge set: exactly 5 badges in order (CI, Docs, License, Ruff, Slack)
- Italic one-line tagline after badges
- Problem paragraph + solution paragraph
- Ends with the single documentation link line — no Quick Start or Development sections

See `.claude/templates/readme.md` for the full canonical template.

## Step 3: Compare and show diff

For each target package:
1. Read the current file
2. Compare against the canonical value
3. Show the differences to the user

## Step 4: Apply changes

For each package, ask the user for confirmation before applying. Apply changes one package at a time.

After applying:
1. Run `hatch run lint` in the modified package to verify no regressions
2. Report success or failure

## Usage

- `/bdc-sync-package-setup ruff` — align ruff config across all 4 packages
- `/bdc-sync-package-setup ci measure` — align CI config for measure only
- `/bdc-sync-package-setup` — list available aspects
