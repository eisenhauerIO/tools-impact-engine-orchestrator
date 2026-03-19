# Development

## Commands

```bash
pip install hatch
hatch env create

hatch run test   # run pytest suite
hatch run lint   # ruff check
```

## Key Insight: SCALE = MEASURE (again)

SCALE is not a separate component. It is the orchestrator calling MEASURE a second time on the subset of initiatives selected by ALLOCATE, with larger sample sizes. This simplifies the architecture to **3 components + orchestrator**.

## Project Structure

```
impact_engine_orchestrator/
├── __init__.py
├── orchestrator.py         # Fan-out/fan-in pipeline runner
├── config.py               # PipelineConfig, InitiativeConfig, StageConfig + load_config()
├── registry.py             # Component registry + build()
├── contracts/              # Dataclasses with validation
│   ├── __init__.py
│   ├── types.py            # ModelType enum
│   ├── measure.py          # MeasureResult
│   ├── evaluate.py         # Re-exports EvaluateResult from impact_engine_evaluate
│   ├── allocate.py         # Re-exports AllocateResult from impact_engine_allocate
│   └── report.py           # OutcomeReport
└── components/
    ├── __init__.py
    ├── base.py             # PipelineComponent ABC + PipelineComponentProtocol
    ├── measure/
    │   └── measure.py      # Measure adapter (wraps impact_engine_measure)
    ├── evaluate/
    │   └── evaluate.py     # Evaluate adapter (wraps impact_engine_evaluate)
    └── allocate/
        ├── allocate.py     # Allocate adapter (wraps impact_engine_allocate)
        └── mock.py         # MockAllocate for testing
tests/
├── conftest.py
└── integration/
    ├── test_mock_pipeline.py
    └── test_real_allocate_pipeline.py
```

## Current State

| Component | Status | Implementation |
|-----------|--------|----------------|
| MEASURE | Integrated | **REAL** (`impact-engine` via pip from GitHub) |
| EVALUATE | Integrated | **REAL** (`impact-engine-evaluate` via pip from GitHub) |
| ALLOCATE | Integrated | **REAL** (`portfolio-allocation` via pip from GitHub) |
| Orchestrator | Implemented | **REAL** (wires everything together) |

## Mock Components

### MockAllocate

Scores initiatives by `confidence * R_med`, selects greedily until budget is exhausted.
