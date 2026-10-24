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
  - Directory: `../impact-engine-{PACKAGE_NAME}` (sibling of the orchestrator repo)

If no argument is provided, ask the user for the package name.

## Step 1: Gather requirements

Ask the user:

1. **Role**: What does this pipeline stage do? (one sentence)
2. **Facade**: Name and arguments of the public function (e.g., `measure_impact`, `evaluate_confidence`, `allocate_portfolio`)
3. **Output**: What fields does `{PACKAGE_NAME}_result.json` carry?
4. **Dependencies**: Any Python packages beyond the standard set?

## Step 2: Create directory structure

```
../impact-engine-{PACKAGE_NAME}/
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
│   └── api.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── integration/
│       └── test_{PACKAGE_NAME}_pipeline.py
└── docs/
    └── source/
        └── conf.py
```

## Step 3: Generate files

### `pyproject.toml`

Use hatchling as build backend. Include:
- `[project]` with name, version, description, Python `>=3.10` (orchestrator is the exception at `>=3.11`)
- `[tool.ruff]` with canonical config (line-length=120, select=["D","E","F","I"], numpy convention)
- `[tool.hatch.envs.default]` with `test` and `lint` scripts
- `[tool.pytest.ini_options]` with testpaths

### `.pre-commit-config.yaml`

Include all canonical hooks: nbstripout, pre-commit-hooks (check-added-large-files, check-merge-conflict, check-yaml, end-of-file-fixer, trailing-whitespace), ruff (lint + format), local `pytest` hook (`hatch run test`, `pass_filenames: false`, `always_run: true`).

### `.github/workflows/ci.yaml`

Standard CI: push/PR to main, Python 3.10/3.11/3.12 matrix, hatch run lint + test.

### `CLAUDE.md`

Follow the bdc-engagement CLAUDE schema (Project overview, Development setup, Common commands, Architecture, Verification, Key conventions), describing this package's role, facade, result file, and internal structure.

### `api.py`

Public facade that runs the stage and writes its result file to the job directory.
The package knows nothing about the orchestrator; the orchestrator adapter lives in
`impact_engine_orchestrator/components/{PACKAGE_NAME}/` (see the `component` feature type).

```python
"""Public API for the {PACKAGE_NAME} pipeline stage."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

RESULT_FILENAME = "{PACKAGE_NAME}_result.json"


def {facade_name}(config: str | Path | dict, job_dir: str | Path) -> dict:
    """Run the {PACKAGE_NAME} stage and write ``{PACKAGE_NAME}_result.json``."""
    job_dir = Path(job_dir)
    result: dict = {}  # TODO: implement
    (job_dir / RESULT_FILENAME).write_text(json.dumps(result, indent=2))
    return result
```

### `__init__.py`

Export the facade (`from .api import {facade_name}`) in `__all__`.

### `tests/test_api.py`

Basic test that the facade writes `{PACKAGE_NAME}_result.json` into a `tmp_path` job directory.

### `tests/integration/test_{PACKAGE_NAME}_pipeline.py`

Stub integration test with a TODO comment.

### `docs/source/conf.py`

Sphinx config with sphinx-rtd-theme, myst-parser, nbsphinx.

## Step 4: Initialize git repo

```bash
cd ../impact-engine-{PACKAGE_NAME}
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
