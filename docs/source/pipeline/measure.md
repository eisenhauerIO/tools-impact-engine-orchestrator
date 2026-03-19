# MEASURE — Pilot Measurement

**Package**: [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure)

## Purpose

Run causal analysis on pilot data to estimate intervention effects.

## Produces

- Effect estimate (point estimate)
- Confidence interval bounds (`ci_lower`, `ci_upper`)
- Model type (`experiment`, `synthetic_control`, `nearest_neighbour_matching`, `interrupted_time_series`, `subclassification`, `metrics_approximation`)
- Statistical diagnostics

Results are written to `measure_result.json` and `impact_results.json` in the initiative's job directory under `storage_url`.

## Key Entry Point

```python
from impact_engine_measure import measure_impact

job_info = measure_impact(
    config_path="config.yaml",
    storage_url="./data",        # default: "./data"
    job_id="my-initiative",      # sets the job directory name
)
```

Returns a `JobInfo` handle. Pass to `load_results(job_info)` for typed results, or read `measure_result.json` directly for the normalized estimate.

## Config Key

Each initiative specifies its measure YAML via `measure_config` in the orchestrator config. The orchestrator passes this as `config_path` and the `initiative_id` as `job_id`.
