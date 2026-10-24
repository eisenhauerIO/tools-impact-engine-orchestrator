---
name: bdc-audit-ecosystem
description: Audit all impact-engine packages against canonical patterns and report deviations.
allowed-tools: Read, Grep, Glob, Bash(ls*), Bash(git*)
---

# Audit Ecosystem

Audit all impact-engine packages against the canonical patterns below. Produce a markdown report of deviations — do NOT fix anything.

## Step 0: Locate packages

The packages are sibling repos, relative to the orchestrator repo root:

- `../impact-engine-orchestrator`
- `../impact-engine-measure`
- `../impact-engine-evaluate`
- `../impact-engine-allocate`

Confirm which packages exist. Report any that are missing.

## Step 1: Audit each package

For each package found, check the following aspects against canonical values. Record every deviation.

### 1.1 `pyproject.toml`

| Check | Canonical Value |
|-------|----------------|
| Build backend | `hatchling` |
| Python requires | `>=3.10` (orchestrator: `>=3.11`) |
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
- `pytest` (local hook, `hatch run test`)

### 1.3 `.github/workflows/`

| Check | Canonical Value |
|-------|----------------|
| CI file name | `ci.yaml` |
| Python matrix | `["3.10", "3.11", "3.12"]` (orchestrator: `["3.11", "3.12"]`, 3.10 dropped 2026-09) |
| Uses `hatch run` for test/lint | Yes |
| Trigger includes push + PR to main | Yes |

### 1.4 `CLAUDE.md`

| Check | Canonical Value |
|-------|----------------|
| File exists | Yes |
| Conforms to bdc-engagement CLAUDE schema | Yes |

### 1.5 Documentation

| Check | Canonical Value |
|-------|----------------|
| `docs/source/conf.py` exists | Yes |
| Sphinx theme | `sphinx-rtd-theme` |
| Extensions include `myst-parser` | Yes |
| Extensions include `nbsphinx` | Yes |

### 1.6 Package structure

| Check | Canonical Value |
|-------|----------------|
| Public facade exported from `__init__.py` | `measure_impact`, `evaluate_confidence`, `allocate_portfolio` (not orchestrator) |
| `tests/` directory at root | Yes |
| `tests/integration/` subdirectory | Yes |
| `__init__.py` exports main class | Yes |

### 1.7 `README.md`

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
