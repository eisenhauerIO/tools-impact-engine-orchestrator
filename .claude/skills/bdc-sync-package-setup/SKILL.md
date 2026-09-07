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
| `ruff` | `[tool.ruff]` section in `pyproject.toml` | See Section 3 of strategy doc |
| `pre-commit` | `.pre-commit-config.yaml` | See Section 3 of strategy doc |
| `ci` | `.github/workflows/ci.yaml` | See Section 3 of strategy doc |
| `docs-ci` | `.github/workflows/docs.yaml` | See Section 3 of strategy doc |
| `claude` | `.claude/` directory (skills symlinks + settings) | Run `/sync` in target repo |
| `claude-md` | `CLAUDE.md` standard sections | Workspace `CLAUDE.md` shared sections |
| `readme` | `README.md` structure and content | Canonical template in `templates/readme.md` |

## Step 1: Locate packages

Find packages under `components/` in the workspace root:

- `components/tools-impact-engine-orchestrator`
- `components/tools-impact-engine-measure`
- `components/tools-impact-engine-evaluate`
- `components/tools-impact-engine-allocate`

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

Required hooks: `nbstripout`, `check-added-large-files` (500kb), `check-merge-conflict`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `ruff` (lint + format).

### `ci`

- File: `.github/workflows/ci.yaml`
- Trigger: push/PR to main
- Matrix: Python 3.10, 3.11, 3.12 on ubuntu-latest
- Steps: install hatch, `hatch run lint`, `hatch run test`

### `docs-ci`

- File: `.github/workflows/docs.yaml`
- Trigger: push to main
- Steps: install hatch, `hatch run docs:build`

### `claude`

Delegates to `/sync` — run the sync-agentic-support skill in the target repo.

### `claude-md`

Standard sections from the workspace `CLAUDE.md`: Ecosystem header, Sibling Repositories, Shared Conventions. Each repo keeps its own repo-specific extensions below the shared section.

### `readme`

Canonical README structure for pipeline component packages (measure, evaluate, allocate). The orchestrator is excluded — it uses a design-document format.

Checks:
- Title format: `# Impact Engine — {Stage}` (em dash, title case stage name)
- Badge set: exactly 5 badges in order (CI, Docs, License, Ruff, Slack)
- Italic one-line tagline after badges
- Problem paragraph + solution paragraph
- Sections in order: Quick Start, Documentation, Development
- Quick Start uses `pip install git+https://github.com/...`
- Documentation table with links to hosted Sphinx docs
- Development section includes all four hatch commands (test, lint, format, docs:build)

See `templates/readme.md` for the full canonical template.

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
