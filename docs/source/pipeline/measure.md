# MEASURE — Pilot Measurement

**Package**: [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure)

## Purpose

Run causal analysis on pilot data to estimate intervention effects.

## Produces

- Effect estimate (point estimate)
- Confidence interval bounds (ci_lower, ci_upper)
- Model type used (experiment, quasi-experiment, time-series)
- Statistical diagnostics

## Key Entry Point

```python
from impact_engine import evaluate_impact

result = evaluate_impact(
    config_path="config.yaml",
    storage_url="./results"
)
```
