---
name: bdc-audit-ecosystem
description: Audit all impact-engine packages against canonical patterns and report deviations.
allowed-tools: Read, Grep, Glob, Bash(ls*), Bash(git*)
---

# Audit Ecosystem

Audit all impact-engine packages against the canonical patterns defined in the workspace `CLAUDE.md` and the strategy document (Section 3: Symmetric Repository Structure). Produce a markdown report of deviations — do NOT fix anything.

## Step 0: Locate packages

Find all impact-engine package directories. Look for sibling repos relative to the current working directory:

- If running from the workspace root (`workbench-impact-engine`), packages are under `components/`:
  - `components/tools-impact-engine-orchestrator`
  - `components/tools-impact-engine-measure`
  - `components/tools-impact-engine-evaluate`
  - `components/tools-impact-engine-allocate`

- If running from within a package, walk up to the workspace and find siblings.

Confirm which packages exist. Report any that are missing.

## Step 1: Audit each package

For each package found, check the following aspects against canonical values. Record every deviation.

### 1.1 `pyproject.toml`

| Check | Canonical Value |
|-------|----------------|
| Build backend | `hatchling` |
| Python requires | `>=3.10` |
| `[tool.ruff]` line-length | `120` |
| `[tool.ruff.lint]` select | `["D", "E", "F", "I"]` |
| `[tool.ruff.lint.pydocstyle]` convention | `"numpy"` |
| Hatch default env has `test` script | `pytest -v --nbmake {args}` or similar |
| Hatch default env has `lint` script | `ruff check . && ruff format --check .` or similar |

### 1.2 `.pre-commit-config.yaml`

Check for presence of these hooks:
- `nbstripout`
- `check-added-large-files` (500kb max)
- `check-merge-conflict`
- `check-yaml`
- `end-of-file-fixer`
- `trailing-whitespace`
- `ruff` (both lint and format)

### 1.3 `.github/workflows/`

| Check | Canonical Value |
|-------|----------------|
| CI file name | `ci.yaml` |
| Python matrix | `["3.10", "3.11", "3.12"]` |
| Uses `hatch run` for test/lint | Yes |
| Trigger includes push + PR to main | Yes |

### 1.4 `CLAUDE.md`

| Check | Canonical Value |
|-------|----------------|
| File exists | Yes |
| Contains "Environment" section | Yes |
| Contains "Architecture" section | Yes |
| Contains "Key Conventions" section | Yes |

### 1.5 `.claude/` directory

| Check | Canonical Value |
|-------|----------------|
| `skills/` directory exists | Yes |
| `subagents/` directory exists | Yes |
| `settings.local.json` exists | Yes |

### 1.6 Documentation

| Check | Canonical Value |
|-------|----------------|
| `docs/source/conf.py` exists | Yes |
| Sphinx theme | `sphinx-rtd-theme` |
| Extensions include `myst-parser` | Yes |
| Extensions include `nbsphinx` | Yes |

### 1.7 Package structure

| Check | Canonical Value |
|-------|----------------|
| `adapter.py` exists in package dir | Yes (except orchestrator) |
| `tests/` directory at root | Yes |
| `tests/integration/` subdirectory | Yes |
| `__init__.py` exports main class | Yes |

### 1.8 `README.md`

| Check | Canonical Value |
|-------|----------------|
| Title format | `# Impact Engine — {Stage}` (em dash) |
| Badge count | 5 (CI, Docs, License, Ruff, Slack) |
| Has italic tagline | Yes |
| Has problem paragraph | Yes |
| Has solution paragraph | Yes |
| Ends with documentation link | `Visit our [documentation](...) for details.` |
| No Quick Start section | Correct — instructional content lives in Sphinx docs |
| No Development section | Correct — instructional content lives in Sphinx docs |

Note: The orchestrator uses a design-document format and is excluded from this check.

## Step 2: Generate report

Produce a markdown report in this format:

```markdown
# Ecosystem Audit Report

*Generated: {date}*

## Summary

| Package | Deviations | Critical |
|---------|-----------|----------|
| orchestrator | X | Y |
| measure | X | Y |
| evaluate | X | Y |
| allocate | X | Y |

## orchestrator

### pyproject.toml
- {deviation description}

### .pre-commit-config.yaml
- {deviation description}

{... repeat for each aspect ...}

## measure

{... same structure ...}

## evaluate

{... same structure ...}

## allocate

{... same structure ...}
```

Mark deviations as **Critical** if they would cause CI failure or break ecosystem conventions. Mark as **Minor** if they are cosmetic or aspirational.

## Usage

- `/bdc-audit-ecosystem` — audit all packages, output to conversation
