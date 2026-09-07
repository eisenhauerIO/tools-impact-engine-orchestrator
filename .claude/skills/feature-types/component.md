# Feature Type: Component

Instructions for scaffolding a new pipeline component in the impact-engine orchestrator.

## Git

- branch_prefix: add
- verb: Add

## Naming

Derive these values from `FEATURE_NAME`:

- `COMPONENT_NAME`: The snake_case name (e.g., `risk_scorer`, `data_validator`)
- `CLASS_NAME`: PascalCase version (e.g., `RiskScorer`, `DataValidator`)
- `REGISTRY_KEY`: PascalCase (same as `CLASS_NAME`)
- `BRANCH_NAME`: `add-component-{COMPONENT_NAME}`

## Requirements

Ask the user these questions:

1. **Purpose**: What does this pipeline component do? (one sentence)
2. **Position**: Where in the pipeline does it run? (before/after which stage?)
3. **Input contract**: What dict keys does `execute()` expect?
4. **Output contract**: What dict keys does `execute()` produce?
5. **Dependencies**: Does it depend on output from other stages?

## References

Ask the user which files to read for context. At minimum, read:

- An existing component for pattern reference (e.g., `components/measure/`)
- `impact_engine_orchestrator/components/base.py` (Protocol definition)
- `impact_engine_orchestrator/registry.py` (registration pattern)
- `impact_engine_orchestrator/pipeline.py` or equivalent (pipeline wiring)

## Plan

The implementation plan should include:

1. **Component directory** — `impact_engine_orchestrator/components/{COMPONENT_NAME}/`
2. **Component class** — implements `PipelineComponent` Protocol
3. **Contract dataclass** — under `impact_engine_orchestrator/contracts/{COMPONENT_NAME}.py`
4. **Registry entry** — register in `registry.py`
5. **Tests** — unit + integration

## Implementation

Create these files:

### Component: `impact_engine_orchestrator/components/{COMPONENT_NAME}/`

```
{COMPONENT_NAME}/
├── __init__.py          # Exports {CLASS_NAME}
└── {COMPONENT_NAME}.py  # Implementation
```

The component class:

```python
"""{CLASS_NAME} pipeline component."""

import logging

logger = logging.getLogger(__name__)


class {CLASS_NAME}:
    """{Purpose description}."""

    def execute(self, event: dict) -> dict:
        """Process event and return result.

        Parameters
        ----------
        event : dict
            Input event with keys: {input keys}.

        Returns
        -------
        dict
            Result with keys: {output keys}.
        """
        # Implementation
        return {...}
```

### Contract: `impact_engine_orchestrator/contracts/{COMPONENT_NAME}.py`

- Dataclass with all output fields
- `__post_init__` validation for required fields and value ranges
- Owned by the orchestrator (this component lives here)

### Registry: `impact_engine_orchestrator/registry.py`

Add the new component to the registry:

```python
"{REGISTRY_KEY}": {CLASS_NAME},
```

### Tests: `tests/test_{COMPONENT_NAME}.py`

- Unit tests for the component (dict in -> dict out)
- Edge case tests (missing keys, invalid values)
- Determinism test (run twice, assert identical results)

### Tests: `tests/integration/test_{COMPONENT_NAME}_pipeline.py`

- Integration test exercising the component through the full pipeline

## Verification

Before declaring done, verify:

- [ ] Work is on a feature branch (not `main`)
- [ ] Component satisfies `PipelineComponent` Protocol (has `execute(dict) -> dict`)
- [ ] Contract dataclass has `__post_init__` validation
- [ ] Component registered in `registry.py`
- [ ] All tests pass (`hatch run test`)
- [ ] Lint passes (`hatch run lint`)
- [ ] Integration test covers end-to-end flow
- [ ] PR created targeting `main`
- [ ] CI is green
