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
- `impact_engine_orchestrator/components/measure/measure.py` — MEASURE adapter: calls `measure_impact()`, reads `measure_result.json` for normalized estimates
- `impact_engine_orchestrator/components/evaluate/evaluate.py` — EVALUATE adapter: calls `evaluate_confidence()`
- `impact_engine_orchestrator/components/allocate/allocate.py` — ALLOCATE adapter: calls `allocate_portfolio()`, reads `allocate_result.json`
- `impact_engine_orchestrator/components/allocate/mock.py` — `MockAllocate` for testing
- `impact_engine_orchestrator/contracts/` — output dataclasses (`MeasureResult`, `OutcomeReport`, `ModelType` enum); evaluate and allocate contracts re-exported from their packages

## Disk-based stage output pattern

Each pipeline stage writes its result to the job directory as a JSON file.
Downstream stages read from disk rather than receiving in-memory data:

| Stage | Writes | Read by |
|-------|--------|---------|
| MEASURE | `measure_result.json` | Orchestrator (for `MeasureResult`), Allocate (via `load_initiatives`) |
| EVALUATE | `evaluate_result.json` | Allocate (via `load_initiatives`) |
| ALLOCATE | `allocate_result.json` | Orchestrator (reads result back) |

The orchestrator adapters are thin readers — they call the component's facade,
then read the result file. No field mapping or model-specific parsing in the
orchestrator.

## Registry

One entry per stage, behavior from config:

| Entry | Class | Config controls |
|-------|-------|----------------|
| `Measure` | `Measure` | Model type via initiative measure config |
| `Evaluate` | `Evaluate` | Strategy via manifest (`score` / `review`) |
| `Allocate` | `Allocate` | Decision rule via `rule` field (`minimax_regret` / `bayesian`) |
| `MockAllocate` | `MockAllocate` | Greedy heuristic for testing |

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
