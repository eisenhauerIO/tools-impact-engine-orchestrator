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

- `impact_engine_orchestrator/api.py` — `run_pipeline()`: public entry point (config path → `PipelineResult`)
- `impact_engine_orchestrator/orchestrator.py` — `Orchestrator` class: `run()`, `_fan_out()`, `_generate_reports()`; module-level `_validate_stage_output()`
- `impact_engine_orchestrator/config.py` — `PipelineConfig`, `InitiativeConfig`, `StageConfig` dataclasses + `load_config()`
- `impact_engine_orchestrator/registry.py` — component registry mapping short names to classes + `build()`
- `impact_engine_orchestrator/components/base.py` — `PipelineComponent` ABC + `PipelineComponentProtocol`
- `impact_engine_orchestrator/components/measure/measure.py` — MEASURE adapter: calls `measure_impact()`, reads `measure_result.json` for normalized estimates
- `impact_engine_orchestrator/components/evaluate/evaluate.py` — EVALUATE adapter: calls `evaluate_confidence()`
- `impact_engine_orchestrator/components/allocate/allocate.py` — ALLOCATE adapter: calls `allocate_portfolio()`, reads `allocate_result.json`
- `impact_engine_orchestrator/components/allocate/mock.py` — `MockAllocate` for testing
- `impact_engine_orchestrator/contracts/` — output dataclasses (`MeasureResult`, `OutcomeReport`, `PipelineResult` in `pipeline.py`, `ModelType` enum); evaluate and allocate contracts re-exported from their packages

Stages hand off via disk: each writes `{stage}_result.json` to the job directory
(`measure_result.json` → Orchestrator + Allocate; `evaluate_result.json` → Allocate;
`allocate_result.json` → Orchestrator). Adapters are thin readers — call the
facade, read the file; no field mapping in the orchestrator.

Registry: one entry per stage, behavior from config — `Measure` (model type via
initiative measure config), `Evaluate` (strategy via manifest: `score` / `review`),
`Allocate` (`rule`: `minimax_regret` / `bayesian`), `MockAllocate` (greedy heuristic for testing).

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
- Pipeline config YAML: `UPPER_CASE` for structural section keys (`ALLOCATE`, `INITIATIVES`), `snake_case` for leaf keys (`budget`, `rule`, `cost_to_scale`) — matches the measure config convention
