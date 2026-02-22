# Design

*Last updated: February 2026*

## Overview

The Impact Engine Orchestrator runs a portfolio-selection pipeline across multiple initiatives. Given a set of candidate initiatives, it measures their causal impact at pilot scale, scores confidence, allocates budget to the most promising ones, then measures again at full scale to verify predictions.

The architecture is **fan-out/fan-in**. Three external tools — [MEASURE](https://github.com/eisenhauerIO/tools-impact-engine-measure), [EVALUATE](https://github.com/eisenhauerIO/tools-impact-engine-evaluate), and [ALLOCATE](https://github.com/eisenhauerIO/tools-impact-engine-allocate) — each own one pipeline stage. The orchestrator wires them together, parallelizes independent work, and enriches data between stages.

```
MEASURE (pilot)  ──fan-out──►  [N initiatives in parallel]
       │
EVALUATE         ──fan-out──►  [N initiatives in parallel]
       │
ALLOCATE         ──fan-in───►  [select K ≤ N for scaling]
       │
MEASURE (scale)  ──fan-out──►  [K initiatives in parallel]
       │
REPORT           ──fan-in───►  [predicted vs actual for K]
```

---

## Plugin Architecture

All pipeline components implement a single abstract interface: [`PipelineComponent`](../../impact_engine_orchestrator/components/base.py).

```python
class PipelineComponent(ABC):
    @abstractmethod
    def execute(self, event: dict) -> dict:
        """Process single initiative, return result."""
```

The [`Orchestrator`](../../impact_engine_orchestrator/orchestrator.py) receives three components via constructor injection and knows nothing about their internals. Components are selected via YAML configuration — swapping `MockAllocate` for `MinimaxRegretAllocate` is a config change, not a code change:

```yaml
# configs/allocate.yaml
component: MinimaxRegretAllocate  # or MockAllocate
```

The [`Orchestrator.from_config()`](../../impact_engine_orchestrator/orchestrator.py) class method uses a [component registry](../../impact_engine_orchestrator/registry.py) to resolve YAML component names to classes and construct them with stage-level kwargs:

```python
config = load_config("config.yaml")
orchestrator = Orchestrator.from_config(config)
```

Direct Python construction still works for tests and advanced usage:

```python
orchestrator = Orchestrator(
    measure=Measure(storage_url="./data"),
    evaluate=Evaluate(),
    allocate=MinimaxRegretAllocate(),
    config=config,
)
```

SCALE is not a fourth component — it reuses the same `Measure` instance at a higher sample size. This keeps the system at **3 components + orchestrator**.

> **ALLOCATE exception**: The ABC describes a single-initiative handler, but ALLOCATE is inherently a fan-in stage — it receives all evaluated initiatives as a batch (`{"initiatives": [...], "budget": ...}`) and returns a single portfolio selection. You can't select a portfolio by looking at initiatives one at a time.

---

## Data Flow and Contracts

Data flows between stages as `dict`s (serialized via `asdict()` from dataclass contracts). Each contract is a dataclass with `__post_init__` validation that catches malformed data at construction time.

| Boundary | Contract | Key Invariants |
|----------|----------|----------------|
| MEASURE output | [`MeasureResult`](../../impact_engine_orchestrator/contracts/measure.py) | `ci_lower <= effect_estimate <= ci_upper`, `sample_size >= 30` |
| EVALUATE output | [`EvaluateResult`](../../_external/tools-impact-engine-evaluate/impact_engine_evaluate/scorer.py) | `return_worst <= return_median <= return_best`, `0 <= confidence <= 1` |
| ALLOCATE output | [`AllocateResult`](../../impact_engine_orchestrator/contracts/allocate.py) | `sum(budget_allocated) <= budget`, selected IDs consistent across dicts |
| Final output | [`OutcomeReport`](../../impact_engine_orchestrator/contracts/report.py) | `prediction_error == actual_return - predicted_return` |

### Enrichment

The orchestrator enriches stage inputs with cross-cutting data from the pipeline config, keeping each stage's contract free of passthrough fields:

- **MEASURE** receives `measure_config` — the per-initiative config path, resolved from the orchestrator YAML
- **EVALUATE** receives `cost_to_scale` — injected into each MeasureResult dict before passing to EVALUATE

```python
# MEASURE enrichment (pilot and scale)
measure_inputs = [
    {"initiative_id": i.initiative_id, "measure_config": i.measure_config}
    for i in initiatives
]

# EVALUATE enrichment
eval_inputs = [{**result, "cost_to_scale": cost_by_id[result["initiative_id"]]}
               for result in pilot_results]
```

### Three-Level Configuration

Parameters are organized into three levels:

- **Orchestrator manifest** ([YAML config](../../docs/source/impact-loop/config.yaml)): `budget`, `scale_sample_size`, `max_workers`, and references to stage config files
- **Stage configs** (e.g., `configs/measure.yaml`): component selection and stage-level constructor kwargs
- **Initiative-level** (per initiative, in the manifest): `initiative_id`, `cost_to_scale`, `measure_config`

All paths in the orchestrator YAML are resolved relative to the YAML file's directory. Initiative-level parameters are *not* passed through pipeline stages — the orchestrator enriches stage inputs with the relevant parameters from config.

---

## Cross-Tool Boundaries

The orchestrator integrates with three external tools, each consumed as a pip dependency from GitHub:

| Tool | Package | Interface |
|------|---------|-----------|
| MEASURE | `impact-engine` | `evaluate_impact(config_path, storage_url, job_id) -> str` (returns path to JSON) |
| EVALUATE | `impact-engine-evaluate` | `Evaluate` class implementing `PipelineComponent` |
| ALLOCATE | `portfolio-allocation` | `MinimaxRegretAllocate` class implementing `PipelineComponent` |

The MEASURE boundary is the most complex: the [`Measure` adapter](../../impact_engine_orchestrator/components/measure/measure.py) calls `evaluate_impact`, reads the resulting JSON envelope (`{schema_version, model_type, data: {impact_estimates, model_summary, ...}}`), and normalizes the model-specific output into a `MeasureResult`. This extraction handles six model types, each with different key structures.

EVALUATE and ALLOCATE are cleaner boundaries — both tools export classes that already implement `PipelineComponent`, so the orchestrator passes dicts directly without parsing.

### Contract Evolution

During prototype phase, two rules prevent breakage:

1. **Producers can add fields freely** — additive changes are always safe
2. **Consumers must be tolerant** — ignore unknown fields, handle missing optional fields with defaults

No explicit schema versioning yet. Breaking changes are coordinated manually across tools.

---

## Concurrency

Fan-out stages (MEASURE and EVALUATE) run initiatives in parallel using `ThreadPoolExecutor`. The orchestrator's [`_fan_out`](../../impact_engine_orchestrator/orchestrator.py) method submits all inputs, then collects results in submission order. If any component raises, the exception propagates immediately.

```python
def _fan_out(self, component, inputs, pool):
    futures = [pool.submit(component.execute, inp) for inp in inputs]
    return [f.result() for f in futures]
```

ALLOCATE runs once (sequential). SCALE fans out again over only the selected subset.

---

## Engineering Practices

The codebase enforces quality through [pre-commit hooks](../../.pre-commit-config.yaml) and [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Tests use [pytest](../../tests/) with real components backed by simulated data — the [`measure_env`](../../tests/conftest.py) fixture generates synthetic product data and working MEASURE configs in a temp directory, enabling end-to-end integration tests without external services.

Dependency injection makes testing straightforward: swap any component at construction time. Dedicated tests verify [contract invariants](../../tests/integration/test_mock_pipeline.py) across all stage boundaries, [determinism](../../tests/integration/test_real_allocate_pipeline.py) across repeated runs, and [edge cases](../../tests/integration/test_mock_pipeline.py) like empty allocations (budget too small for any initiative).
