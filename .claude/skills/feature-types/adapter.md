# Feature Type: Adapter

Instructions for scaffolding a new orchestrator integration point (adapter) in any impact-engine package.

## Git

- branch_prefix: add
- verb: Add

## Naming

Derive these values from `FEATURE_NAME`:

- `ADAPTER_NAME`: The snake_case name (e.g., `review_scoring`, `batch_measure`)
- `MODULE_NAME`: Same as `ADAPTER_NAME`
- `CLASS_NAME`: PascalCase version (e.g., `ReviewScoring`, `BatchMeasure`) + `Adapter` suffix
- `BRANCH_NAME`: `add-adapter-{ADAPTER_NAME}`

## Requirements

Ask the user these questions:

1. **Package**: Which impact-engine package does this adapter belong to? (measure, evaluate, allocate)
2. **Purpose**: What does this adapter do? (one sentence)
3. **Input contract**: What dict keys does `execute()` expect?
4. **Output contract**: What dict keys does `execute()` produce?
5. **Pure logic**: Is there existing pure logic to wrap, or does it need to be written?

## References

Ask the user which files to read for context. At minimum, read:

- The existing `adapter.py` in the target package (pattern reference)
- The package's `__init__.py` (to understand current exports)
- The orchestrator's registry (`impact_engine_orchestrator/registry.py`) if adding a registry entry
- Any existing pure logic module that the adapter will wrap

## Plan

The implementation plan should include:

1. **Pure logic module** — `{package_dir}/{MODULE_NAME}.py` with the core logic
2. **Adapter** — `{package_dir}/{MODULE_NAME}_adapter.py` wrapping pure logic for the pipeline
3. **Output dataclass** — with `__post_init__` validation, owned by this package
4. **Tests** — unit tests for pure logic + adapter
5. **Registry entry** — if the orchestrator needs to discover this adapter

## Implementation

Create these files:

### Pure logic module: `{package_dir}/{MODULE_NAME}.py`

- Contains the core algorithm/logic with no knowledge of the pipeline
- Takes typed arguments, returns typed results
- Full docstrings (numpy convention)

### Adapter: `{package_dir}/{MODULE_NAME}_adapter.py`

```python
"""Adapter for {ADAPTER_NAME}."""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class PipelineComponent(Protocol):
    """Pipeline component interface."""

    def execute(self, event: dict) -> dict:
        """Process event and return result."""
        ...


class {CLASS_NAME}Adapter:
    """Adapter for {ADAPTER_NAME}."""

    def execute(self, event: dict) -> dict:
        """Process event and return result."""
        # Extract from input dict
        # Call pure logic
        # Build output dict
        return {...}
```

### Output dataclass: `{package_dir}/contracts/{MODULE_NAME}.py`

- Dataclass with all output fields
- `__post_init__` validation
- Owned by this package (never imported by other packages)

### Tests: `tests/test_{MODULE_NAME}.py`

- Unit tests for the pure logic module
- Unit tests for the adapter (dict in -> dict out)
- Determinism test (run twice, assert identical results)

### Tests: `tests/integration/test_{MODULE_NAME}_pipeline.py`

- Integration test exercising the adapter through the pipeline interface

## Verification

Before declaring done, verify:

- [ ] Work is on a feature branch (not `main`)
- [ ] Pure logic is separated from adapter (no dict handling in pure logic)
- [ ] Adapter satisfies `PipelineComponent` Protocol (has `execute(dict) -> dict`)
- [ ] Output dataclass has `__post_init__` validation
- [ ] All tests pass (`hatch run test`)
- [ ] Lint passes (`hatch run lint`)
- [ ] No imports from sibling packages (measure/evaluate/allocate don't import each other)
- [ ] `__init__.py` updated to export the new adapter class
- [ ] PR created targeting `main`
- [ ] CI is green
