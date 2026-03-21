# Configuration

The pipeline is driven by a single YAML file passed to `load_config()`.

## Minimal Example

```yaml
budget: 100000
storage_url: ./data/measure

allocate:
  rule: minimax_regret

initiatives:
  - initiative_id: my-initiative
    cost_to_scale: 15000
    measure_config: configs/my-initiative.yaml
```

## Top-Level Parameters

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `budget` | float | required | Total budget constraint for ALLOCATE |
| `max_workers` | int | 4 | Thread pool size for parallel fan-out stages |
| `storage_url` | str | required | Directory where MEASURE writes job results |

## `allocate` Block

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `rule` | str | required | Decision rule: `minimax_regret` or `bayesian` |

## `initiatives` List

Each entry configures one initiative:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `initiative_id` | str | required | Unique identifier (alphanumeric, hyphens, underscores) |
| `cost_to_scale` | float | required | Budget required to deploy this initiative to production |
| `measure_config` | str | `""` | Path to the initiative's measure YAML (resolved relative to this file) |
| `evaluate_strategy` | str | `"score"` | Confidence strategy: `"score"` (deterministic) or `"review"` (LLM-powered) |

## Path Resolution

`measure_config` paths are resolved relative to the orchestrator config file, so a layout like this works without absolute paths:

```
config.yaml
configs/
  my-initiative.yaml
  another-initiative.yaml
```
