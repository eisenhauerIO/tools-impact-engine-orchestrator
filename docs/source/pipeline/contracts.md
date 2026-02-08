# Data Flow Contracts

## Shared Types

| Type | Definition | Constraints |
|------|------------|-------------|
| InitiativeId | string | Non-empty, alphanumeric with hyphens/underscores |
| ModelType | enum | `experiment` \| `quasi-experiment` \| `time-series` \| `observational` |
| Confidence | float | [0.0, 1.0] |
| Currency | float | >= 0.0 |

## Configuration

Parameters are separated into two levels. The orchestrator owns the config and routes the right data to each pipeline stage.

### Problem-Level Parameters

Shared across the entire run, not specific to any initiative.

| Parameter | Type | Description |
|-----------|------|-------------|
| budget | Currency | Total budget constraint for ALLOCATE |
| scale_sample_size | int | Sample size for scale-phase MEASURE runs |
| max_workers | int | Parallelism for fan-out stages |

### Initiative-Level Parameters

Specific to each initiative, known upfront (not produced by pipeline stages).

| Parameter | Type | Description |
|-----------|------|-------------|
| initiative_id | InitiativeId | Unique identifier |
| cost_to_scale | Currency | Cost to scale this initiative to production |

> **Key principle**: Initiative-level parameters (e.g. `cost_to_scale`) are **not** passed through pipeline stages. The orchestrator enriches stage inputs with the relevant initiative parameters from the config. This keeps contracts clean — each stage only produces its own outputs.

---

## Measure → Evaluate

| Field | Type | Description |
|-------|------|-------------|
| initiative_id | InitiativeId | Identifier for the initiative |
| effect_estimate | float | Estimated causal effect (point estimate) |
| ci_lower | float | Lower bound of confidence interval |
| ci_upper | float | Upper bound of confidence interval |
| p_value | float | Statistical significance |
| sample_size | int | Number of observations in pilot |
| model_type | ModelType | experiment / quasi-experiment / time-series |
| diagnostics | dict | Model fit diagnostics |

**Invariants:**
- `ci_lower <= effect_estimate <= ci_upper`
- `p_value` in [0.0, 1.0]
- `sample_size >= 30` (minimum for statistical validity)
- `diagnostics` must contain `r_squared` or `log_likelihood`

## Evaluate → Allocate

| Field | Type | Description |
|-------|------|-------------|
| initiative_id | InitiativeId | Initiative identifier |
| confidence | Confidence | Methodology-based confidence (0-1) |
| cost | Currency | Cost to scale this initiative |
| R_best | float | Upper CI bound → best-case return |
| R_med | float | Point estimate → median return |
| R_worst | float | Lower CI bound → worst-case return |
| model_type | ModelType | Source methodology (informational) |

**Invariants:**
- `R_worst <= R_med <= R_best`
- `cost > 0` (zero-cost initiatives don't need allocation decisions)

## Allocate → Scale

| Field | Type | Description |
|-------|------|-------------|
| selected_initiatives | list[InitiativeId] | Initiatives approved for scaling |
| predicted_returns | dict[InitiativeId, float] | Expected returns from pilot (per initiative) |
| budget_allocated | dict[InitiativeId, Currency] | Budget allocated per initiative |

**Invariants:**
- `selected_initiatives` may be empty (if no initiative fits the budget or all have negative expected returns, the orchestrator skips SCALE and returns an empty outcome report)
- All keys in `predicted_returns` and `budget_allocated` exist in `selected_initiatives`
- `sum(budget_allocated.values()) <= total_budget`

## Scale → Outcome Report

| Field | Type | Description |
|-------|------|-------------|
| initiative_id | InitiativeId | Initiative identifier |
| predicted_return | float | Return predicted from pilot |
| actual_return | float | Observed return at scale |
| prediction_error | float | Difference (actual - predicted) |
| sample_size_pilot | int | Original pilot sample |
| sample_size_scale | int | Scale sample size |
| budget_allocated | Currency | Budget allocated to this initiative |
| confidence_score | Confidence | Methodology-based confidence from EVALUATE |
| model_type | ModelType | Source methodology |

**Invariants:**
- `prediction_error == actual_return - predicted_return`
- `sample_size_scale >= sample_size_pilot` (scale should be larger)
- `sample_size_pilot >= 30`
