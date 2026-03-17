# CLAUDE.md

## Project overview

Fan-out/fan-in pipeline runner for the impact engine ecosystem. Orchestrates
MEASURE → EVALUATE → ALLOCATE → SCALE across multiple initiatives, with
parallel execution via `ThreadPoolExecutor`.

## Development setup

```bash
pip install hatch
hatch env create
```

## Common commands

- `hatch run test` — run pytest suite
- `hatch run lint` — check with ruff
- `hatch run format` — auto-format with ruff

Always use `hatch run` to execute commands. Never bare `python` or `pytest`.

## Architecture

- `impact_engine_orchestrator/orchestrator.py` — `Orchestrator` class: `run()`, `_fan_out()`, `_generate_reports()`, `_validate_stage_output()`
- `impact_engine_orchestrator/config.py` — `PipelineConfig`, `InitiativeConfig`, `StageConfig` dataclasses + `load_config()`
- `impact_engine_orchestrator/registry.py` — component registry mapping short names to classes + `build()`
- `impact_engine_orchestrator/components/base.py` — `PipelineComponent` ABC + `PipelineComponentProtocol`
- `impact_engine_orchestrator/components/measure/measure.py` — MEASURE adapter: wraps `evaluate_impact()`, normalizes model-specific output via `_extract_estimates()`
- `impact_engine_orchestrator/components/evaluate/evaluate.py` — EVALUATE adapter: wraps `evaluate_confidence()`
- `impact_engine_orchestrator/components/allocate/allocate.py` — ALLOCATE adapter: field mapping, preprocessing, solver delegation
- `impact_engine_orchestrator/components/allocate/mock.py` — `MockAllocate` for testing
- `impact_engine_orchestrator/contracts/` — output dataclasses (`MeasureResult`, `OutcomeReport`, `ModelType` enum); evaluate and allocate contracts re-exported from their packages

## Adapter-ownership principle

**The orchestrator owns all glue logic.** Field mapping, result normalization, and
contract validation live in the orchestrator so that component packages (measure,
evaluate, allocate) can evolve independently. Components expose functional APIs
and know nothing about each other or the orchestrator's naming conventions.

Concretely:
- `_extract_estimates()` normalizes 6 model-type-specific output schemas into a
  flat `MeasureResult` — this logic belongs here, not in the measure package
- `_FIELD_MAP_IN` translates orchestrator field names (`return_best`) to allocate
  internal names (`R_best`) — this logic belongs here, not in the allocate package
- `orchestrator.run()` enriches cross-stage data (e.g. merging pilot results into
  evaluate output) — this is the orchestrator's core coordination responsibility

When a component changes its output schema, the orchestrator adapter is the place
to update. Components never import from or adapt to the orchestrator.

## Verification

1. `hatch run lint` — no ruff violations
2. `hatch run test` — all tests pass
3. Push to branch and confirm GitHub Actions CI passes

## Key conventions

- NumPy-style docstrings
- Logging via `logging.getLogger(__name__)` (no print statements)
- `PipelineComponent` protocol: `execute(self, event: dict) -> dict`
- Stage output validated via `_validate_stage_output()` with required key sets
- Contract field names: `snake_case` (NEVER abbreviated: `return_best` not `R_best`)
- `_external/` contains reference submodules — do not modify
