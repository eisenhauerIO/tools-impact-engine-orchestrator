# Development

## Quick Start

```bash
# Install
pip install -e .

# Run the orchestrator once
python scripts/run_once.py --config config.yaml

# Run tests
pytest tests/
```

## Key Insight: SCALE = MEASURE (again)

SCALE is not a separate component. It is the orchestrator calling MEASURE a second time on the subset of initiatives selected by ALLOCATE, with larger sample sizes. This simplifies the architecture to **3 components + orchestrator**.

## Project Structure

```
impact_engine_orchestrator/
├── __init__.py
├── orchestrator.py         # Fan-out/fan-in pipeline runner
├── config.py               # PipelineConfig, MeasureConfig
├── contracts/              # Dataclasses with validation
│   ├── __init__.py
│   ├── types.py            # ModelType enum
│   ├── measure.py          # MeasureResult
│   ├── evaluate.py         # EvaluateResult
│   ├── allocate.py         # AllocateResult
│   └── report.py           # OutcomeReport
└── components/
    ├── __init__.py
    ├── base.py             # PipelineComponent ABC
    ├── measure/
    │   └── measure.py      # Measure (wraps impact_engine)
    ├── evaluate/
    │   └── __init__.py     # Namespace (Evaluate from impact_engine_evaluate)
    └── allocate/
        └── mock.py         # MockAllocate
tests/
├── conftest.py
└── integration/
    ├── test_mock_pipeline.py
    └── test_real_allocate_pipeline.py
scripts/
└── run_once.py
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

## Runner Script

`scripts/run_once.py` runs the orchestrator end-to-end:

```{eval-rst}
.. literalinclude:: ../../../scripts/run_once.py
   :language: python
```

## Configuration

`config.yaml` at the repo root:

```{eval-rst}
.. literalinclude:: ../../../config.yaml
   :language: yaml
```

## Integration Path

| Phase | Action | Verification |
|-------|--------|--------------|
| ~~1~~ | ~~All Mocks~~ | ~~End-to-end flow works, deterministic~~ |
| ~~2~~ | ~~Real MEASURE~~ | ~~Done — `Measure` adapter wrapping `impact_engine`~~ |
| ~~3~~ | ~~Real ALLOCATE~~ | ~~Done — `MinimaxRegretAllocate` from `portfolio-allocation`~~ |
| ~~4~~ | ~~Real EVALUATE~~ | ~~Done — `Evaluate` from `impact-engine-evaluate`~~ |

Each swap is a single line change in the orchestrator constructor.
