# Usage

The orchestrator runs the full MEASURE → EVALUATE → ALLOCATE → SCALE pipeline
from a single config file.

## Quickstart

**Step 1 — Write a pipeline config:**

```yaml
# pipeline.yaml
budget: 100000
storage_url: ./data/measure

allocate:
  rule: minimax_regret

initiatives:
  - initiative_id: initiative-a
    cost_to_scale: 15000
    measure_config: configs/initiative-a.yaml

  - initiative_id: initiative-b
    cost_to_scale: 40000
    measure_config: configs/initiative-b.yaml
```

**Step 2 — Run the pipeline:**

```python
from impact_engine_orchestrator import load_config, Orchestrator

config = load_config("pipeline.yaml")
orchestrator = Orchestrator.from_config(config)
results = orchestrator.run()
```

**Step 3 — Read the results:**

```python
# Per-initiative pilot measurements
for report in results["initiative_reports"]:
    print(report["initiative_id"], report["effect_estimate"], report["confidence"])

# Portfolio allocation decision
allocation = results["allocation"]
print(allocation["selected_initiatives"])
print(allocation["budget_allocated"])
```

## Output Structure

`run()` returns a dict with two keys:

| Key | Type | Description |
|-----|------|-------------|
| `initiative_reports` | list[dict] | One entry per initiative with MEASURE + EVALUATE results |
| `allocation` | dict | ALLOCATE result: selected initiatives, budget used, objective value |

Each initiative report contains the fields from `MeasureResult` and `EvaluateResult`
merged into a single dict — see the [API Reference](../api/index) for the full field list.

## Evaluate Strategy

Each initiative can use a different confidence strategy:

```yaml
initiatives:
  - initiative_id: initiative-a
    evaluate_strategy: score    # fast deterministic scoring (default)
    measure_config: configs/initiative-a.yaml

  - initiative_id: initiative-b
    evaluate_strategy: review   # LLM-powered review via evaluate backend
    measure_config: configs/initiative-b.yaml
```

See [Configuration](../configuration/index) for the full parameter reference.
