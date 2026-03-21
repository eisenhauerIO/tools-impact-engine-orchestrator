# Usage

The orchestrator runs the full MEASURE → EVALUATE → ALLOCATE → SCALE pipeline
from a single config file.

```{image} ../_static/pipeline.svg
:alt: Pipeline Execution Pattern
:align: center
```

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
from impact_engine_orchestrator import run_pipeline

results = run_pipeline("pipeline.yaml")
```

**Step 3 — Read the results:**

```python
# Per-initiative pilot measurements
for pilot in results["pilot_results"]:
    print(pilot["initiative_id"], pilot["effect_estimate"], pilot["p_value"])

# Portfolio allocation decision
allocation = results["allocate_result"]
print(allocation["selected_initiatives"])
print(allocation["budget_allocated"])

# Outcome reports (predicted vs. actual at scale)
for report in results["outcome_reports"]:
    print(report["initiative_id"], report["predicted_return"], report["actual_return"])
```

## Output Structure

`run_pipeline()` returns a dict with five keys:

| Key | Type | Description |
|-----|------|-------------|
| `pilot_results` | list[dict] | MEASURE results for all initiatives (pilot phase) |
| `evaluate_results` | list[dict] | EVALUATE confidence scores for all initiatives |
| `allocate_result` | dict | ALLOCATE decision: selected initiatives, budget, predicted returns |
| `scale_results` | list[dict] | MEASURE results for selected initiatives (scale phase) |
| `outcome_reports` | list[dict] | Predicted vs. actual returns for selected initiatives |

See the [API Reference](../api/index) for the full field list per stage.

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
