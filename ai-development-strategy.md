# AI-Driven Ecosystem Development Strategy

*Last updated: February 2026*

## Overview

This document outlines strategies for leveraging AI (Claude Code) to develop the
tools-impact-engine ecosystem in tandem — enforcing standards across projects,
maintaining design symmetry, and coordinating cross-repo changes.

## Ecosystem Inventory

| Repo | Package | Role | Status |
|------|---------|------|--------|
| `tools-impact-engine-orchestrator` | `impact-engine-orchestrator` | Pipeline wiring | Implemented (mock + real components) |
| `tools-impact-engine-measure` | `impact-engine` | Causal impact measurement | Needs integration |
| `tools-impact-engine-evaluate` | `impact-engine-evaluate` | Confidence scoring | Needs integration |
| `tools-impact-engine-allocate` | `portfolio-allocation` | Portfolio optimization | Integrated |

---

## 1. Shared `CLAUDE.md` as the Ecosystem Constitution

The single highest-leverage move. Each repo's `CLAUDE.md` becomes the enforcement
mechanism for ecosystem-wide standards. Create a canonical template that every repo
inherits from, then extends with repo-specific rules.

### Why This Works

When you open any repo in Claude Code, it reads `CLAUDE.md` first. Every change Claude
proposes will conform to these standards because they are in its instruction set. This is
more reliable than documentation humans must remember to read.

### Shared Section (identical across all 4 repos)

```markdown
# Ecosystem: tools-impact-engine

## Sibling Repositories
- orchestrator: github.com/eisenhauerIO/tools-impact-engine-orchestrator
- measure: github.com/eisenhauerIO/tools-impact-engine-measure
- evaluate: github.com/eisenhauerIO/tools-impact-engine-evaluate
- allocate: github.com/eisenhauerIO/tools-impact-engine-allocate

## Shared Conventions (MUST follow across all repos)

### Build & Execution
- Build system: Hatchling (`pyproject.toml` only, no setup.py/setup.cfg)
- Always use `hatch run` to execute commands. Never bare `python` or `pytest`.
- Python: >=3.10, test matrix: 3.10, 3.11, 3.12

### Code Quality
- Linter/formatter: Ruff (line-length=120, select=["D","E","F","I"], numpy docstring convention)
- Pre-commit: nbstripout, check-added-large-files (500kb), check-merge-conflict,
  check-yaml, end-of-file-fixer, trailing-whitespace, ruff, ruff-format

### Pipeline Component Interface
- All pipeline-facing classes MUST implement `PipelineComponent` ABC
- `execute(self, event: dict) -> dict` — single-initiative in, single-result out
- Exception: fan-in stages (ALLOCATE) receive batch input
- Dataclass contracts with `__post_init__` validation for all boundary types

### Naming Conventions
- Repo names: `tools-impact-engine-{stage}`
- Python packages: lowercase with underscores (`impact_engine_*`, `portfolio_allocation`)
- Initiative IDs: alphanumeric + hyphens/underscores
- Component registry names: PascalCase
- Contract field names: snake_case (NEVER abbreviated: `return_best` not `R_best`)

### Testing
- pytest with `-v --nbmake`
- Integration tests validate cross-boundary contract invariants
- Determinism tests (run twice, assert identical results)
- testpaths: ["tests", "docs/source/..."] (include notebook execution)

### CI/CD (GitHub Actions)
- Trigger: push/PR to main
- Matrix: Python 3.10, 3.11, 3.12 on ubuntu-latest
- Steps: install hatch -> ruff check + format --check -> pytest
```

### Repo-Specific Extensions

Each repo extends the shared section with its own rules. Example for **measure**:

```markdown
# Repo-Specific: tools-impact-engine-measure

## This Repo's Role
Runs causal impact analysis using multiple model types. Consumes experiment/observational
data, produces MeasureResult with effect estimates, confidence intervals, and diagnostics.

## Supported Model Types
experiment, synthetic_control, nearest_neighbour_matching, interrupted_time_series,
subclassification, metrics_approximation

## When adding a new model type:
1. Add enum value to ModelType in tools-impact-engine-contracts
2. Implement model in models/{model_name}.py
3. Ensure output JSON follows schema_version 2.x envelope format
4. Add extraction case in orchestrator's _extract_estimates (or use registry pattern)
5. Add confidence range to CONFIDENCE_MAP in evaluate's scorer
```

---

## 2. Shared Contracts Package

### The Problem

The `PipelineComponent` ABC is defined in the orchestrator, but the evaluate package has
a fallback copy. Contracts are scattered across repos. Field names drift between docs and
code (e.g. `R_best` vs `return_best`). There is no formal `AllocateInput` dataclass.

### The Solution: `tools-impact-engine-contracts`

Create a fifth package that owns all cross-boundary types:

```
tools-impact-engine-contracts/
├── CLAUDE.md
├── pyproject.toml
├── impact_engine_contracts/
│   ├── __init__.py
│   ├── component.py      # PipelineComponent ABC (single source of truth)
│   ├── types.py           # ModelType enum
│   ├── measure.py         # MeasureResult dataclass
│   ├── evaluate.py        # EvaluateResult dataclass
│   ├── allocate.py        # AllocateInput + AllocateResult dataclasses
│   └── report.py          # OutcomeReport dataclass
└── tests/
```

All 4 repos depend on this package. The orchestrator stops owning the contracts.

### Benefits

- Eliminates the fallback ABC problem — one import path everywhere
- Creates a formal `AllocateInput` — closes the gap in the architecture review
- Field name drift becomes impossible — one `EvaluateResult` definition, not a doc
  version and a code version
- AI agents can validate changes — when modifying any repo, Claude can check the
  contract package to verify field compatibility

### `CLAUDE.md` Instruction for All Repos

```markdown
## Contract Package
- All cross-boundary types live in `tools-impact-engine-contracts`
- NEVER define boundary dataclasses locally. Import from `impact_engine_contracts`.
- When changing a contract field: update the contracts package FIRST, then update
  all consumers.
```

---

## 3. Symmetric Repository Structure

Enforce identical directory layouts so AI can navigate any repo without learning a new
structure:

```
tools-impact-engine-{stage}/
├── CLAUDE.md                          # Ecosystem + repo-specific instructions
├── pyproject.toml                     # Hatchling, same ruff/pytest config
├── .pre-commit-config.yaml            # Identical hooks
├── .github/workflows/ci.yaml          # Identical CI matrix
├── {python_package_name}/
│   ├── __init__.py                    # Exports main class
│   ├── component.py                   # PipelineComponent implementation
│   └── {internal modules}
├── tests/
│   ├── conftest.py
│   ├── test_{unit}.py
│   └── integration/
│       └── test_{stage}_pipeline.py
└── docs/
    └── source/
```

### Why Symmetry Matters for AI

Claude Code uses file patterns to orient itself. If `component.py` is where the
`PipelineComponent` implementation lives in every repo, Claude can reliably find the
right file without exploration. It also means you can give a single instruction like
"update the component to handle the new `diagnostics_version` field" and Claude will
know exactly where to look in any repo.

### Canonical Configuration Reference

| Aspect | Canonical Value |
|--------|----------------|
| Build backend | `hatchling` |
| Python | `>=3.10` |
| Formatter | ruff format only (no black) |
| Line length | `120` |
| Ruff select | `["D", "E", "F", "I"]` |
| Docstring convention | `numpy` |
| Hatch default env | `features = ["dev"]` |
| Hatch scripts | `test`, `lint`, `format` |
| Hatch docs env | separate `docs` env |
| CI file | `.github/workflows/ci.yaml` |
| CI matrix | Python 3.10, 3.11, 3.12 |
| Docs path | `docs/source/` -> `docs/build/html` |
| Docs theme | sphinx-rtd-theme + myst-parser + nbsphinx |
| Pre-commit | nbstripout, pre-commit-hooks, ruff, local pytest |
| CLAUDE.md sections | Environment, Architecture, Key Conventions |

---

## 4. Dependency Graph and Change Protocols

### Dependency Direction (DO NOT violate)

```
contracts <- measure   <- orchestrator
contracts <- evaluate  <- orchestrator
contracts <- allocate  <- orchestrator
```

- The contracts package has ZERO dependencies on other ecosystem packages
- measure, evaluate, allocate depend ONLY on contracts (not on each other)
- orchestrator depends on all three + contracts

### Breaking Change Protocol

When modifying a contract that crosses tool boundaries:

1. Identify all producers and consumers of the contract
2. Update `tools-impact-engine-contracts` first
3. Update the producer repo
4. Update the consumer repo(s)
5. Run orchestrator integration tests to verify end-to-end

### Safe Changes (no cross-repo coordination needed)

- Internal refactoring that preserves `execute()` input/output shape
- Adding new optional fields to output dicts (additive-only)
- Performance improvements, logging, error messages
- Documentation and test additions

---

## 5. Schema Versioning

The architecture review flags unchecked `schema_version` as the highest-risk evolution
vector. Standardize this across the ecosystem.

### Rules for All Repos

- Every `execute()` output dict MUST include `"schema_version": "X.Y"`
- Major bump (X) = breaking field rename/removal
- Minor bump (Y) = additive field addition
- Consumers MUST check major version and raise a clear error on mismatch

### Implementation

Add to the contracts package:

```python
SUPPORTED_SCHEMA_VERSIONS = {
    "measure": "2",
    "evaluate": "1",
    "allocate": "1",
}

def check_schema_version(stage: str, version: str) -> None:
    """Raise if major version is unsupported."""
    major = version.split(".")[0]
    if major != SUPPORTED_SCHEMA_VERSIONS[stage]:
        raise ValueError(
            f"{stage} schema version {version} not supported. "
            f"Expected major version {SUPPORTED_SCHEMA_VERSIONS[stage]}."
        )
```

---

## 6. Ecosystem Integration CI

Add a weekly CI job to the orchestrator that clones all repos at HEAD and runs
integration tests:

```yaml
# .github/workflows/ecosystem-integration.yaml
name: Ecosystem Integration

on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday
  workflow_dispatch:

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install all ecosystem packages from main
        run: |
          pip install hatch
          pip install git+https://github.com/eisenhauerIO/tools-impact-engine-contracts.git
          pip install git+https://github.com/eisenhauerIO/tools-impact-engine-measure.git
          pip install git+https://github.com/eisenhauerIO/tools-impact-engine-evaluate.git
          pip install git+https://github.com/eisenhauerIO/tools-impact-engine-allocate.git
          pip install -e .
      - name: Run ecosystem integration tests
        run: hatch run pytest tests/integration/ -v
```

---

## 7. Multi-Repo AI Development Workflow

### Contract-First Changes (breaking)

1. Open `tools-impact-engine-contracts` in Claude Code — update the dataclass
2. Open the **producer** repo — update to emit the new contract
3. Open the **consumer** repo(s) — update to consume the new contract
4. Open orchestrator — run integration tests

### Isolated Changes (internal)

Changes within a single repo that don't touch the `execute()` interface or contract
shapes are safe to make independently. Claude Code will respect this boundary because
the `CLAUDE.md` encodes which changes are safe vs cross-cutting.

### Leveraging `CLAUDE.md` for AI Enforcement

`CLAUDE.md` is not just documentation — it is a runtime instruction set that shapes every
change AI makes. Investing in a well-structured `CLAUDE.md` template that encodes the
ecosystem's architecture, conventions, and dependency rules gives you automated standards
enforcement every time any developer (human or AI) touches any repo.

---

## 8. Claude Code Skills & Subagents

The standards above are enforced via shared skills and subagents in
`utils-agentic-support`, synced to each package's `.claude/` directory.

### New Skills

#### `audit-ecosystem` — `/audit-ecosystem`

Audits all packages against canonical patterns (Section 3) and reports deviations.

Checks:
- `pyproject.toml`: build-backend, ruff config, hatch env names/scripts, Python version
- `.pre-commit-config.yaml`: required hooks (nbstripout, pre-commit-hooks, ruff, local pytest)
- `.github/workflows/`: ci.yaml + docs.yaml presence, Python matrix, hatch usage
- `CLAUDE.md`: existence, required sections (Environment, Architecture, Key Conventions)
- `.claude/`: skills/ symlinks, settings.local.json
- Docs: `docs/source/conf.py` existence, theme, extensions
- Package structure: adapter.py presence, tests/ directory, `__init__.py` exports

Output: markdown report grouped by package, listing deviations from canonical.

#### `sync-package-setup` — `/sync-package-setup [aspect]`

Synchronizes a specific config aspect across all (or selected) packages.

| Aspect | What it aligns |
|--------|---------------|
| `ruff` | `[tool.ruff]` section in pyproject.toml |
| `pre-commit` | `.pre-commit-config.yaml` |
| `ci` | `.github/workflows/ci.yaml` |
| `docs-ci` | `.github/workflows/docs.yaml` |
| `claude` | `.claude/` directory with skills symlinks + settings |
| `claude-md` | CLAUDE.md standard sections |

Workflow: Read canonical template -> read target file -> show diff -> apply per package.

#### `scaffold-package` — `/scaffold-package [package-name]`

Bootstraps a new impact-engine package with canonical structure:
pyproject.toml, package dir, adapter.py, tests/, .pre-commit-config.yaml,
CI workflows, CLAUDE.md, .claude/, docs/source/, .gitignore, README.md.

### New Subagent

#### `ecosystem-reviewer`

**Model:** opus | Reviews a change for cross-ecosystem consistency.

Checks:
- Contract compatibility: does a dataclass/adapter change break consumers?
- Adapter pattern conformance: pure logic separated from orchestrator integration?
- Naming conventions: consistent field names across boundaries (`initiative_id` not `id`)
- Public API surface: clean `__init__.py` exports?
- Config handling: YAML-only, no inline defaults?

### New Feature-Types (for `/add-feature`)

#### `adapter`

Scaffolds a new orchestrator integration point in any package:
pure logic module + adapter.py + contract dataclass + tests + registry entry.

#### `component`

Scaffolds a new pipeline component in the orchestrator:
component dir under `components/`, PipelineComponent subclass, contract under `contracts/`,
registry entry, integration test.

### Files to Create in `utils-agentic-support`

- `claude/skills/audit-ecosystem/SKILL.md`
- `claude/skills/sync-package-setup/SKILL.md`
- `claude/skills/scaffold-package/SKILL.md`
- `claude/subagents/ecosystem-reviewer.md`
- `claude/skills/add-feature/feature-types/adapter.md`
- `claude/skills/add-feature/feature-types/component.md`

---

## Priority Order

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Standardize `CLAUDE.md` across all repos | Immediate enforcement for every AI-assisted change | Low |
| 2 | Extract `tools-impact-engine-contracts` | Eliminates root cause of cross-repo issues | Medium |
| 3 | Enforce symmetric directory layout | Reliable AI navigation; lower onboarding cost | Low |
| 4 | Add schema version checking | Closes the highest-risk evolution vector | Low |
| 5 | Add ecosystem integration CI | Catches cross-repo breakage before users | Low |
| 6 | Document dependency graph and change protocols in `CLAUDE.md` | Prevents AI from violating dependency direction | Low |
| 7 | Create `audit-ecosystem` skill | Baseline assessment of all deviations | Low |
| 8 | Create `sync-package-setup` skill | Fix deviations aspect-by-aspect | Medium |
| 9 | Create `ecosystem-reviewer` subagent | Prevent future drift during development | Medium |
| 10 | Create `adapter` + `component` feature-types | Standardize new code scaffolding | Low |
| 11 | Create `scaffold-package` skill | Enable future package creation | Low |
