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
├── config.py               # PipelineConfig
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
    │   └── mock.py         # MockMeasure
    ├── evaluate/
    │   └── mock.py         # MockEvaluate
    └── allocate/
        └── mock.py         # MockAllocate
tests/
└── integration/
    └── test_mock_pipeline.py
scripts/
└── run_once.py
```

## Current State

| Component | Status | Implementation |
|-----------|--------|----------------|
| MEASURE | Needs integration | **MOCK** (deterministic fake results) |
| EVALUATE | Needs integration | **MOCK** (confidence scoring) |
| ALLOCATE | Needs integration | **MOCK** (simple selection) |
| Orchestrator | Implemented | **REAL** (wires everything together) |

## Mock Components

### MockMeasure

Deterministic via hash seed, with a noise component keyed on `seed + sample_size` so pilot vs scale produce related but distinct estimates.

### MockEvaluate

Confidence scoring by model type:

| Model Type | Confidence Range |
|------------|------------------|
| Experiment | 0.85 -- 1.00 |
| Quasi-experiment | 0.60 -- 0.84 |
| Time-series | 0.40 -- 0.59 |
| Observational | 0.20 -- 0.39 |

### MockAllocate

Scores initiatives by `confidence * R_med`, selects greedily until budget is exhausted.

## Runner Script

`scripts/run_once.py` runs the orchestrator end-to-end with mock components:

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
| 1 | All Mocks | End-to-end flow works, deterministic |
| 2 | Real MEASURE | Swap `MockMeasure` → `RealMeasureAdapter` |
| 3 | Real ALLOCATE | Swap `MockAllocate` → `RealAllocateAdapter` |
| 4 | Real EVALUATE | Build confidence scoring (when designed) |

Each swap is a single line change in the orchestrator constructor.
