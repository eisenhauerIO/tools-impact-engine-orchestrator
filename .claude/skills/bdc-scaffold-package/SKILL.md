---
name: bdc-scaffold-package
description: Bootstrap a new impact-engine package with canonical structure.
argument-hint: [package-name]
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Scaffold Package

Bootstrap a new impact-engine pipeline package with the canonical directory structure, config files, and CI setup.

## Step 0: Parse arguments

The user provides: `{package_name}`

- `PACKAGE_NAME`: The stage name (e.g., `transform`, `validate`). This becomes:
  - Repo name: `tools-impact-engine-{PACKAGE_NAME}`
  - Python package: `impact_engine_{PACKAGE_NAME}`
  - Directory: `components/tools-impact-engine-{PACKAGE_NAME}`

If no argument is provided, ask the user for the package name.

## Step 1: Gather requirements

Ask the user:

1. **Role**: What does this pipeline stage do? (one sentence)
2. **Input**: What dict keys does `execute()` expect?
3. **Output**: What dict keys does `execute()` produce?
4. **Dependencies**: Any Python packages beyond the standard set?

## Step 2: Create directory structure

```
components/tools-impact-engine-{PACKAGE_NAME}/
├── CLAUDE.md
├── pyproject.toml
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yaml
├── .gitignore
├── README.md
├── impact_engine_{PACKAGE_NAME}/
│   ├── __init__.py
│   └── adapter.py
├── tests/
│   ├── conftest.py
│   ├── test_adapter.py
│   └── integration/
│       └── test_{PACKAGE_NAME}_pipeline.py
└── docs/
    └── source/
        └── conf.py
```

## Step 3: Generate files

### `pyproject.toml`

Use hatchling as build backend. Include:
- `[project]` with name, version, description, Python `>=3.10`
- `[tool.ruff]` with canonical config (line-length=120, select=["D","E","F","I"], numpy convention)
- `[tool.hatch.envs.default]` with `test` and `lint` scripts
- `[tool.pytest.ini_options]` with testpaths

### `.pre-commit-config.yaml`

Include all canonical hooks: nbstripout, pre-commit-hooks (check-added-large-files, check-merge-conflict, check-yaml, end-of-file-fixer, trailing-whitespace), ruff (lint + format).

### `.github/workflows/ci.yaml`

Standard CI: push/PR to main, Python 3.10/3.11/3.12 matrix, hatch run lint + test.

### `CLAUDE.md`

Shared ecosystem section (from workspace CLAUDE.md) plus repo-specific section describing this package's role, input/output contract, and internal structure.

### `adapter.py`

Minimal `PipelineComponent` Protocol implementation:

```python
"""Adapter for {PACKAGE_NAME} pipeline stage."""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class PipelineComponent(Protocol):
    """Pipeline component interface."""

    def execute(self, event: dict) -> dict:
        """Process event and return result."""
        ...


class {PascalName}Adapter:
    """Adapter for the {PACKAGE_NAME} pipeline stage."""

    def execute(self, event: dict) -> dict:
        """Process event and return result."""
        # TODO: implement
        return {}
```

### `__init__.py`

Export the adapter class.

### `tests/test_adapter.py`

Basic test that `execute()` returns a dict.

### `tests/integration/test_{PACKAGE_NAME}_pipeline.py`

Stub integration test with a TODO comment.

### `docs/source/conf.py`

Sphinx config with sphinx-rtd-theme, myst-parser, nbsphinx.

## Step 4: Initialize git repo

```bash
cd components/tools-impact-engine-{PACKAGE_NAME}
git init
pre-commit install
```

## Step 5: Verify

Run in the new package directory:

```bash
hatch run lint
hatch run test
```

Both must pass before declaring done.

## Usage

- `/bdc-scaffold-package transform` — create a new `tools-impact-engine-transform` package
