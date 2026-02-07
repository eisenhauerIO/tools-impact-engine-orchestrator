# Impact Engine Orchestrator - Mock Implementation Plan

## Goal
Build orchestration system with mocks for all components, enabling complete end-to-end flow simulation before integrating real components one-by-one.

## Key Insight: SCALE = MEASURE (again)
SCALE is not a separate component. It's the orchestrator calling MEASURE a second time on the subset of initiatives selected by ALLOCATE, with larger sample sizes. This simplifies the architecture to **3 components + orchestrator**.

---

## Quick Start (after implementation)
```bash
# Install
pip install -e .

# Run the orchestrator once
python scripts/run_once.py

# Run with config file
python scripts/run_once.py --config config.yaml

# Run tests
pytest tests/
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package config |
| `impact_engine_orchestrator/__init__.py` | Package root |
| `impact_engine_orchestrator/orchestrator.py` | Pipeline runner |
| `impact_engine_orchestrator/config.py` | PipelineConfig, InitiativeConfig |
| `impact_engine_orchestrator/contracts/__init__.py` | Contracts module |
| `impact_engine_orchestrator/contracts/types.py` | ModelType enum |
| `impact_engine_orchestrator/contracts/measure.py` | MeasureResult |
| `impact_engine_orchestrator/contracts/evaluate.py` | EvaluateResult |
| `impact_engine_orchestrator/contracts/allocate.py` | AllocateResult |
| `impact_engine_orchestrator/contracts/report.py` | OutcomeReport |
| `impact_engine_orchestrator/components/__init__.py` | Components module |
| `impact_engine_orchestrator/components/base.py` | PipelineComponent ABC |
| `impact_engine_orchestrator/components/measure/mock.py` | MockMeasure |
| `impact_engine_orchestrator/components/evaluate/mock.py` | MockEvaluate |
| `impact_engine_orchestrator/components/allocate/mock.py` | MockAllocate |
| `scripts/run_once.py` | CLI runner |
| `tests/integration/test_mock_pipeline.py` | Integration test |
| `notebooks/impact_engine_loop.ipynb` | Tutorial notebook |
| `.github/workflows/ci.yaml` | CI pipeline |
| `config.yaml` | Default config |

---

## pyproject.toml
```toml
[project]
name = "impact-engine-orchestrator"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pyyaml"]

[project.optional-dependencies]
dev = ["pytest", "nbconvert", "jupyter"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["impact_engine_orchestrator"]
```

---

## Current State
| Component | Status | Repository |
|-----------|--------|------------|
| MEASURE | Needs integration | [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure) |
| EVALUATE | Needs integration | [tools-impact-engine-evaluate](https://github.com/eisenhauerIO/tools-impact-engine-evaluate) |
| ALLOCATE | Needs integration | [tools-impact-engine-allocate](https://github.com/eisenhauerIO/tools-impact-engine-allocate) |
| Orchestrator | **NOT IMPLEMENTED** | This repo |

## What We're Building (P0)
| Component | Implementation |
|-----------|----------------|
| MEASURE | **MOCK** (deterministic fake results) |
| EVALUATE | **MOCK** (confidence scoring) |
| ALLOCATE | **MOCK** (simple selection) |
| Orchestrator | **REAL** (wires everything together) |

---

## Directory Structure
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
    │   ├── __init__.py
    │   └── mock.py         # MockMeasure
    ├── evaluate/
    │   ├── __init__.py
    │   └── mock.py         # MockEvaluate
    └── allocate/
        ├── __init__.py
        └── mock.py         # MockAllocate
tests/
├── conftest.py
└── integration/
    └── test_mock_pipeline.py   # All-mocks end-to-end
scripts/
└── run_once.py                 # Runner script for single orchestrator execution
```

---

## Pipeline Flow (All Mocked)

```
INITIATIVES (n)
      │
      ▼
┌─────────────┐
│ MockMeasure │  ← Fan-out: parallel for all n
│   (pilot)   │
└─────────────┘
      │
      ▼
┌──────────────┐
│ MockEvaluate │  ← Fan-out: parallel for all n
└──────────────┘
      │
      ▼
┌───────────────┐
│ MockAllocate  │  ← Fan-in: single call, selects m initiatives
└───────────────┘
      │
      ▼
SELECTED (m < n)
      │
      ▼
┌─────────────┐
│ MockMeasure │  ← Fan-out: parallel for selected m only
│   (scale)   │     (same component, larger sample_size)
└─────────────┘
      │
      ▼
┌────────────────┐
│ OutcomeReport  │  ← Compare pilot predictions vs scale actuals
└────────────────┘
```

---

## Implementation Steps

### Step 1: Project Setup
- [ ] Create `pyproject.toml` with hatchling build
- [ ] Create `impact_engine_orchestrator/__init__.py`
- [ ] Create `scripts/` directory
- [ ] Dependencies: `pytest` (dev)

### Step 2: Config (`impact_engine_orchestrator/config.py`)

Separates initiative-level parameters from problem-level parameters. The orchestrator owns this config and routes the right data to each stage.

```python
@dataclass
class InitiativeConfig:
    initiative_id: str
    cost_to_scale: float

@dataclass
class PipelineConfig:
    budget: float
    scale_sample_size: int
    max_workers: int
    initiatives: list[InitiativeConfig]
```

**Example config (`config.yaml`):**
```yaml
budget: 100000
scale_sample_size: 5000

initiatives:
  - initiative_id: product-desc-enhancement
    cost_to_scale: 15000
  - initiative_id: checkout-flow-optimization
    cost_to_scale: 25000
  - initiative_id: search-relevance-tuning
    cost_to_scale: 20000
  - initiative_id: pricing-display-test
    cost_to_scale: 10000
  - initiative_id: recommendation-engine-v2
    cost_to_scale: 30000
```

---

### Step 3: Contracts (`impact_engine_orchestrator/contracts/`)

**types.py:**
```python
from enum import Enum

class ModelType(Enum):
    EXPERIMENT = "experiment"
    QUASI_EXPERIMENT = "quasi-experiment"
    TIME_SERIES = "time-series"
    OBSERVATIONAL = "observational"
```

**measure.py** - `MeasureResult`:
```python
@dataclass
class MeasureResult:
    initiative_id: str
    effect_estimate: float
    ci_lower: float
    ci_upper: float
    p_value: float
    sample_size: int
    model_type: ModelType
    diagnostics: dict

    def __post_init__(self):
        assert self.ci_lower <= self.effect_estimate <= self.ci_upper
        assert self.sample_size >= 30
```

**evaluate.py** - `EvaluateResult`:
```python
@dataclass
class EvaluateResult:
    initiative_id: str
    confidence: float      # 0-1
    cost: float
    R_best: float          # ci_upper
    R_med: float           # effect_estimate
    R_worst: float         # ci_lower
    model_type: ModelType
    sample_size: int       # preserved for reporting
```

**allocate.py** - `AllocateResult`:
```python
@dataclass
class AllocateResult:
    selected_initiatives: list[str]
    predicted_returns: dict[str, float]
    budget_allocated: dict[str, float]
```

**report.py** - `OutcomeReport`:
```python
@dataclass
class OutcomeReport:
    initiative_id: str
    predicted_return: float    # from pilot
    actual_return: float       # from scale
    prediction_error: float    # actual - predicted
    sample_size_pilot: int
    sample_size_scale: int
    budget_allocated: float
    confidence_score: float
    model_type: ModelType
```

### Step 4: Component Base
**base.py:**
```python
from abc import ABC, abstractmethod

class PipelineComponent(ABC):
    @abstractmethod
    def execute(self, event: dict, context=None) -> dict:
        """Process single initiative, return result."""
        pass
```

### Step 5: Mock Components

**MockMeasure** (deterministic via hash seed, with noise for scale runs):
```python
class MockMeasure(PipelineComponent):
    def execute(self, event: dict, context=None) -> dict:
        initiative_id = event["initiative_id"]
        seed = hash(initiative_id) % 2**32
        rng = random.Random(seed)

        effect = rng.uniform(0.05, 0.25)
        ci_width = effect * rng.uniform(0.3, 0.6)
        sample_size = event.get("sample_size", rng.randint(50, 500))

        # Add controlled noise for scale runs so pilot vs scale
        # produce related but distinct estimates
        noise_rng = random.Random(seed + sample_size)
        noise = noise_rng.gauss(0, 0.01)
        effect += noise

        return {
            "initiative_id": initiative_id,
            "effect_estimate": effect,
            "ci_lower": effect - ci_width/2,
            "ci_upper": effect + ci_width/2,
            "p_value": rng.uniform(0.001, 0.05),
            "sample_size": sample_size,
            "model_type": rng.choice(["experiment", "quasi-experiment", "time-series", "observational"]),
            "diagnostics": {"r_squared": rng.uniform(0.6, 0.95)}
        }
```

**MockEvaluate** (confidence by model type):
```python
CONFIDENCE_MAP = {
    "experiment": (0.85, 1.0),
    "quasi-experiment": (0.60, 0.84),
    "time-series": (0.40, 0.59),
    "observational": (0.20, 0.39),
}

class MockEvaluate(PipelineComponent):
    def execute(self, event: dict, context=None) -> dict:
        model_type = event["model_type"]
        conf_range = CONFIDENCE_MAP[model_type]
        seed = hash(event["initiative_id"]) % 2**32
        rng = random.Random(seed)
        confidence = rng.uniform(conf_range[0], conf_range[1])

        return {
            "initiative_id": event["initiative_id"],
            "confidence": confidence,
            "cost": event["cost_to_scale"],
            "R_best": event["ci_upper"],
            "R_med": event["effect_estimate"],
            "R_worst": event["ci_lower"],
            "model_type": model_type,
            "sample_size": event["sample_size"],
        }
```

**MockAllocate** (select top by confidence-weighted return):
```python
class MockAllocate(PipelineComponent):
    def execute(self, event: dict, context=None) -> dict:
        initiatives = event["initiatives"]
        budget = event["budget"]

        # Score by confidence * R_med
        scored = [(i, i["confidence"] * i["R_med"]) for i in initiatives]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select until budget exhausted
        selected = []
        remaining = budget
        for init, score in scored:
            if init["cost"] <= remaining:
                selected.append(init["initiative_id"])
                remaining -= init["cost"]

        return {
            "selected_initiatives": selected,
            "predicted_returns": {i["initiative_id"]: i["R_med"] for i in initiatives if i["initiative_id"] in selected},
            "budget_allocated": {i["initiative_id"]: i["cost"] for i in initiatives if i["initiative_id"] in selected},
        }
```

### Step 6: Orchestrator (`impact_engine_orchestrator/orchestrator.py`)
```python
from concurrent.futures import ThreadPoolExecutor


class Orchestrator:
    def __init__(self, measure, evaluate, allocate, config):
        self.measure = measure
        self.evaluate = evaluate
        self.allocate = allocate
        self.config = config

    def run(self) -> dict:
        initiatives = self.config.initiatives
        cost_by_id = {i.initiative_id: i.cost_to_scale for i in initiatives}

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:
            # 1. MEASURE (pilot) - parallel
            measure_inputs = [{"initiative_id": i.initiative_id} for i in initiatives]
            pilot_results = self._fan_out(self.measure, measure_inputs, pool)

            # 2. EVALUATE - parallel (enrich with cost_to_scale from config)
            eval_inputs = [
                {**result, "cost_to_scale": cost_by_id[result["initiative_id"]]}
                for result in pilot_results
            ]
            eval_results = self._fan_out(self.evaluate, eval_inputs, pool)

            # 3. ALLOCATE - single (budget from config)
            alloc_result = self.allocate.execute({
                "initiatives": eval_results,
                "budget": self.config.budget,
            })

            # 4. MEASURE (scale) - parallel on selected only
            selected_ids = alloc_result["selected_initiatives"]
            scale_inputs = [
                {"initiative_id": iid, "sample_size": self.config.scale_sample_size}
                for iid in selected_ids
            ]
            scale_results = self._fan_out(self.measure, scale_inputs, pool)

        # 5. Generate outcome reports
        reports = self._generate_reports(
            pilot_results, eval_results, alloc_result, scale_results
        )

        return {
            "pilot_results": pilot_results,
            "evaluate_results": eval_results,
            "allocate_result": alloc_result,
            "scale_results": scale_results,
            "outcome_reports": reports,
        }

    def _fan_out(self, component, inputs, pool):
        futures = [pool.submit(component.execute, inp) for inp in inputs]
        return [f.result() for f in futures]

    def _generate_reports(self, pilot_results, eval_results, alloc_result, scale_results):
        reports = []
        pilot_by_id = {p["initiative_id"]: p for p in pilot_results}
        eval_by_id = {e["initiative_id"]: e for e in eval_results}
        scale_by_id = {s["initiative_id"]: s for s in scale_results}

        for iid in alloc_result["selected_initiatives"]:
            pilot = pilot_by_id[iid]
            evalu = eval_by_id[iid]
            scale = scale_by_id[iid]
            predicted = alloc_result["predicted_returns"][iid]
            actual = scale["effect_estimate"]

            reports.append({
                "initiative_id": iid,
                "predicted_return": predicted,
                "actual_return": actual,
                "prediction_error": actual - predicted,
                "sample_size_pilot": pilot["sample_size"],
                "sample_size_scale": scale["sample_size"],
                "budget_allocated": alloc_result["budget_allocated"][iid],
                "confidence_score": evalu["confidence"],
                "model_type": evalu["model_type"],
            })
        return reports
```

### Step 7: Integration Test
```python
def _make_orchestrator(budget=100000, initiatives=None):
    if initiatives is None:
        initiatives = [
            InitiativeConfig("init-001", cost_to_scale=10000),
            InitiativeConfig("init-002", cost_to_scale=15000),
            InitiativeConfig("init-003", cost_to_scale=8000),
        ]
    config = PipelineConfig(
        budget=budget,
        scale_sample_size=5000,
        max_workers=4,
        initiatives=initiatives,
    )
    return Orchestrator(
        measure=MockMeasure(),
        evaluate=MockEvaluate(),
        allocate=MockAllocate(),
        config=config,
    )


def test_all_mocks_pipeline():
    orchestrator = _make_orchestrator()
    result = orchestrator.run()

    assert len(result["outcome_reports"]) > 0

    # Verify determinism
    result2 = orchestrator.run()
    assert result["pilot_results"] == result2["pilot_results"]


def test_contract_invariants():
    orchestrator = _make_orchestrator()
    result = orchestrator.run()

    for pilot in result["pilot_results"]:
        assert pilot["ci_lower"] <= pilot["effect_estimate"] <= pilot["ci_upper"]
        assert 0.0 <= pilot["p_value"] <= 1.0
        assert pilot["sample_size"] >= 30

    for evalu in result["evaluate_results"]:
        assert evalu["R_worst"] <= evalu["R_med"] <= evalu["R_best"]
        assert 0.0 <= evalu["confidence"] <= 1.0
        assert evalu["cost"] > 0

    alloc = result["allocate_result"]
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]

    for report in result["outcome_reports"]:
        assert report["prediction_error"] == pytest.approx(
            report["actual_return"] - report["predicted_return"]
        )
        assert report["sample_size_scale"] >= report["sample_size_pilot"]


def test_empty_allocation():
    """Budget too small for any initiative — no initiatives selected."""
    orchestrator = _make_orchestrator(budget=1)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []


def test_single_initiative():
    orchestrator = _make_orchestrator(
        initiatives=[InitiativeConfig("only-one", cost_to_scale=5000)]
    )
    result = orchestrator.run()

    assert len(result["pilot_results"]) == 1
    assert len(result["outcome_reports"]) == 1
    assert result["outcome_reports"][0]["initiative_id"] == "only-one"
```

### Step 8: Runner Script (`scripts/run_once.py`)
```python
# scripts/run_once.py
"""
Run the Impact Engine Orchestrator once with mock components.

Usage:
    python scripts/run_once.py --config config.yaml
"""
import argparse

import yaml

from impact_engine_orchestrator.config import PipelineConfig, InitiativeConfig
from impact_engine_orchestrator.orchestrator import Orchestrator
from impact_engine_orchestrator.components.measure.mock import MockMeasure
from impact_engine_orchestrator.components.evaluate.mock import MockEvaluate
from impact_engine_orchestrator.components.allocate.mock import MockAllocate


def load_config(path: str) -> PipelineConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return PipelineConfig(
        budget=raw["budget"],
        scale_sample_size=raw.get("scale_sample_size", 5000),
        initiatives=[InitiativeConfig(**i) for i in raw["initiatives"]],
    )


def print_reports(result):
    print("\n" + "=" * 70)
    print("OUTCOME REPORTS")
    print("=" * 70)

    for report in result["outcome_reports"]:
        print(f"\n{report['initiative_id']}")
        print("-" * 40)
        print(f"  Predicted: {report['predicted_return']:.2%}")
        print(f"  Actual:    {report['actual_return']:.2%}")
        print(f"  Error:     {report['prediction_error']:+.2%}")
        print(f"  Confidence: {report['confidence_score']:.2f} ({report['model_type']})")
        print(f"  Budget:    ${report['budget_allocated']:,.0f}")
        print(f"  Samples:   {report['sample_size_pilot']} → {report['sample_size_scale']}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Initiatives evaluated: {len(result['pilot_results'])}")
    print(f"  Initiatives selected:  {len(result['outcome_reports'])}")
    if not result["outcome_reports"]:
        print("  No initiatives selected for scaling.")
        return
    total_budget = sum(r["budget_allocated"] for r in result["outcome_reports"])
    print(f"  Total budget used:     ${total_budget:,.0f}")
    avg_error = sum(abs(r["prediction_error"]) for r in result["outcome_reports"]) / len(result["outcome_reports"])
    print(f"  Avg prediction error:  {avg_error:.2%}")


def main():
    parser = argparse.ArgumentParser(description="Run Impact Engine Orchestrator once")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)

    orchestrator = Orchestrator(
        measure=MockMeasure(),
        evaluate=MockEvaluate(),
        allocate=MockAllocate(),
        config=config,
    )

    result = orchestrator.run()
    print_reports(result)


if __name__ == "__main__":
    main()
```

**Expected Output:**
```
Running pipeline with 5 initiatives...
  [1/5] MEASURE (pilot)...
  [2/5] EVALUATE...
  [3/5] ALLOCATE...
       Selected 3 initiatives
  [4/5] MEASURE (scale)...
  [5/5] Generating reports...

======================================================================
OUTCOME REPORTS
======================================================================

product-desc-enhancement
----------------------------------------
  Predicted: 15.23%
  Actual:    14.87%
  Error:     -0.36%
  Confidence: 0.72 (quasi-experiment)
  Budget:    $15,000
  Samples:   342 → 5000

checkout-flow-optimization
----------------------------------------
  Predicted: 18.45%
  Actual:    19.12%
  Error:     +0.67%
  Confidence: 0.92 (experiment)
  Budget:    $25,000
  Samples:   287 → 5000

======================================================================
SUMMARY
======================================================================
  Initiatives evaluated: 5
  Initiatives selected:  3
  Total budget used:     $70,000
  Avg prediction error:  0.52%
```

---

## Integration Path (Post-Mocks)

| Phase | Action | Verification |
|-------|--------|--------------|
| 1 | All Mocks | End-to-end flow works, deterministic |
| 2 | Real MEASURE | Swap `MockMeasure` → `RealMeasureAdapter` |
| 3 | Real ALLOCATE | Swap `MockAllocate` → `RealAllocateAdapter` |
| 4 | Real EVALUATE | Build confidence scoring (when designed) |

Each swap is a single line change in the orchestrator constructor.

---

## Tutorial Notebook

A Jupyter notebook (`notebooks/impact_engine_loop.ipynb`) will demonstrate the full impact engine loop end-to-end using the orchestrator. Works with mocks initially, improves as real components are swapped in. The orchestrator is the tool, the notebook is the tutorial/demo.

---

## Continuous Integration (`.github/workflows/ci.yaml`)

GitHub Actions pipeline that runs on every push and PR.

**Post-implementation verification**: After pushing, verify CI passes via `gh run list` and `gh run view`. All three Python versions (3.10, 3.11, 3.12) must pass before the implementation is considered complete.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install
        run: pip install -e ".[dev]"

      - name: Run integration tests
        run: pytest tests/ -v

      - name: Run notebooks
        run: |
          for nb in notebooks/*.ipynb; do
            jupyter nbconvert --to notebook --execute "$nb" --output /dev/null
          done
```

---

## Key Files to Reference

| Repository | Entry Point | Purpose |
|------------|-------------|---------|
| This repo | `README.md` | Design doc with all contracts |
| [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure) | `science/impact_engine/engine.py` | `evaluate_impact()` |
| [tools-impact-engine-evaluate](https://github.com/eisenhauerIO/tools-impact-engine-evaluate) | TBD | Confidence scoring |
| [tools-impact-engine-allocate](https://github.com/eisenhauerIO/tools-impact-engine-allocate) | `support.py` | `solve_minimax_regret_optimization()` |
