# Impact Engine Orchestrator - Design Document

## Overview

The Impact Engine Orchestrator is an orchestration system for **scaling pilot experiments to full deployment**.

**Input**: A cohort of project proposals (initiatives) to be piloted.

**Output**: A subset of initiatives scaled to production, with outcome reports comparing predicted vs actual impact.

The core insight: pilot many initiatives, then invest in scaling only those that show both high impact and high confidence.

<p align="center">
  <img src="docs/source/_static/overview.svg" alt="Impact Engine Orchestrator Overview">
</p>

---

## Component Repositories

| Component | Repository | Status |
|-----------|------------|--------|
| **MEASURE** | [eisenhauerIO/tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure) | Needs integration |
| **EVALUATE** | [eisenhauerIO/tools-impact-engine-evaluate](https://github.com/eisenhauerIO/tools-impact-engine-evaluate) | Needs integration |
| **ALLOCATE** | [eisenhauerIO/tools-impact-engine-allocate](https://github.com/eisenhauerIO/tools-impact-engine-allocate) | Needs integration |
| **SCALE** | Reuses MEASURE | — |
| **SIMULATE** | [eisenhauerIO/tools-catalog-generator](https://github.com/eisenhauerIO/tools-catalog-generator) | Implemented |

---

## Pipeline Steps

### 1. MEASURE - Pilot Measurement
**Package**: `tools-impact-engine-measure`

**Purpose**: Run causal analysis on pilot data to estimate intervention effects.

**Produces**:
- Effect estimate (point estimate)
- Confidence interval bounds (ci_lower, ci_upper)
- Model type used (experiment, quasi-experiment, time-series)
- Statistical diagnostics

**Key Entry Point**:
```python
from impact_engine import evaluate_impact

result = evaluate_impact(
    config_path="config.yaml",
    storage_url="./results"
)
```

---

### 2. EVALUATE - Confidence Scoring
**Package**: `tools-impact-engine-evaluate`

**Purpose**: Assign a confidence score based on methodology reliability.

**Inputs** (from MEASURE):
- Effect estimate + CI bounds
- Model type
- Diagnostics

**Produces**:
- Confidence score (0-1)
- Scenario returns (R_best, R_med, R_worst from CI bounds)

**Confidence by Methodology**:

| Model Type | Confidence Range | Rationale |
|------------|------------------|-----------|
| Experiment (RCT) | 0.85 - 1.0 | Gold standard causal inference |
| Quasi-experiment | 0.60 - 0.84 | Strong but with assumptions |
| Time-series | 0.40 - 0.59 | Trend-based, confounding risk |
| Observational | 0.20 - 0.39 | Correlation, high bias risk |

---

### 3. ALLOCATE - Portfolio Selection
**Package**: `tools-impact-engine-allocate`

**Purpose**: Select which initiatives to scale given a limited budget.

**Inputs** (from EVALUATE):
- Confidence scores
- Scenario returns (R_best, R_med, R_worst)
- Costs to scale each initiative

**Produces**:
- Selected initiatives for scaling
- Budget allocation per initiative
- Predicted returns

**Algorithm**: Minimax regret optimization (linear programming)

**Key Entry Point**:
```python
from support import solve_minimax_regret_optimization

result = solve_minimax_regret_optimization(
    initiatives=initiatives,
    budget=budget,
    scenarios=["best", "med", "worst"]
)
```

---

### 4. SCALE - Scale and Report
**Package**: Reuses `tools-impact-engine-measure`

**Purpose**: Run MEASURE again on selected initiatives at larger scale, then compare predicted vs actual outcomes.

**Process**:
1. Take selected initiatives from ALLOCATE
2. Run MEASURE on each (with larger sample size / longer time window)
3. Compare scaled effect_estimate to pilot predictions
4. Generate outcome report

**Inputs** (from ALLOCATE):
- Selected initiatives
- Predicted returns (from pilot MEASURE → EVALUATE)
- Budget allocated

**Produces**:
- Actual returns at scale (from scaled MEASURE)
- Prediction error (actual - predicted)
- Outcome report

> **Note**: SCALE is not a separate component—it's the orchestrator calling MEASURE a second time on the subset of initiatives that passed ALLOCATE.

---

## Shared Types

| Type | Definition | Constraints |
|------|------------|-------------|
| InitiativeId | string | Non-empty, alphanumeric with hyphens/underscores |
| ModelType | enum | `experiment` \| `quasi-experiment` \| `time-series` \| `observational` |
| Confidence | float | [0.0, 1.0] |
| Currency | float | >= 0.0 |

---

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

## Data Flow Contracts

### Measure → Evaluate

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

### Evaluate → Allocate

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

### Allocate → Scale

| Field | Type | Description |
|-------|------|-------------|
| selected_initiatives | list[InitiativeId] | Initiatives approved for scaling |
| predicted_returns | dict[InitiativeId, float] | Expected returns from pilot (per initiative) |
| budget_allocated | dict[InitiativeId, Currency] | Budget allocated per initiative |

**Invariants:**
- `selected_initiatives` may be empty (if no initiative fits the budget or all have negative expected returns, the orchestrator skips SCALE and returns an empty outcome report)
- All keys in `predicted_returns` and `budget_allocated` exist in `selected_initiatives`
- `sum(budget_allocated.values()) <= total_budget`

### Scale → Outcome Report

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

---

## Outcome Report

The final deliverable documents predicted vs actual outcomes:

```
┌──────────────────────────────────────────────────────────────────────┐
│                       OUTCOME REPORT                                  │
├──────────────────────────────────────────────────────────────────────┤
│ Initiative: Product Description Enhancement                          │
│ ─────────────────────────────────────────────────────────────────── │
│ Pilot Results:                                                       │
│   Effect Estimate: +12.5% conversion                                 │
│   95% CI: [8.2%, 16.8%]                                              │
│   Confidence Score: 0.78 (quasi-experiment)                          │
│   Sample Size: 500 products                                          │
│                                                                      │
│ Scale Results:                                                       │
│   Sample Size: 5,000 products                                        │
│   Actual Effect: +11.8% conversion                                   │
│                                                                      │
│ Comparison:                                                          │
│   Predicted (median): +12.5%                                         │
│   Actual: +11.8%                                                     │
│   Prediction Error: -0.7% (within CI)                                │
│                                                                      │
│ Budget: $50,000 allocated                                            │
│ ROI: Estimated $425,000 incremental revenue                          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Decisions

### 1. Contract Evolution (Prototype Phase)

Two simple rules to prevent breakage during rapid iteration:

1. **Producers can add fields freely** - Additive changes are always OK
2. **Consumers must be tolerant** - Ignore unknown fields, handle missing optional fields with defaults

No explicit versioning during prototype phase. Coordinate breaking changes manually.

> **Note**: For production, consider adding `schema_version` field and semantic versioning.

### 2. Stateless Runs
Each run is independent. No persistent state between runs. This simplifies the system and makes runs reproducible.

### 3. Fully Autonomous
No human approval gates. The orchestrator runs end-to-end without intervention.

### 4. CI Bounds → Scenarios
The confidence interval from Measure maps directly to allocation scenarios:
- `ci_upper` → `R_best`
- `effect_estimate` → `R_med`
- `ci_lower` → `R_worst`

### 5. Methodology-Based Confidence
Confidence scoring is primarily methodology-driven, not just statistical. An experiment with wide CI still beats a time-series with narrow CI.

---

## Execution Model

### Parallelism (Fan-Out / Fan-In)

MEASURE and EVALUATE process multiple initiatives in parallel. ALLOCATE receives all results and runs once.

<p align="center">
  <img src="docs/source/_static/pipeline.svg" alt="Pipeline Execution Pattern">
</p>

### Synchronization Points

| Point | Trigger | Action |
|-------|---------|--------|
| After MEASURE | All initiatives measured | Collect results → EVALUATE |
| After EVALUATE | All initiatives evaluated | Collect results → ALLOCATE |
| After ALLOCATE | Portfolio selected | Fan-out to SCALE |
| After SCALE | All scaled initiatives complete | Generate Outcome Report |

### Handler Interface

Each component processes a **single initiative** and returns a single result. Parallelism is handled by the orchestrator, not the handlers.

> **Exception**: ALLOCATE is a fan-in component — it receives all evaluated initiatives as a batch (`{"initiatives": [...], "budget": ...}`) and returns a single portfolio selection. This is inherent to the allocation problem: you can't select a portfolio by looking at initiatives one at a time.

```python
def handler(event: dict, context=None) -> dict:
    """Lambda-compatible interface for a single initiative."""
    # Process one initiative
    return result
```

### Deployment Strategy

| Environment | Orchestration | Parallelism |
|-------------|---------------|-------------|
| Local Dev | Python script | `concurrent.futures.ThreadPoolExecutor` |
| AWS Production | Step Functions | `Map` state with `MaxConcurrency` |

The handler interface is identical in both environments.

---

## Appendix: SIMULATE (Optional)

**Package**: `tools-catalog-generator`

**Purpose**: Generate synthetic data with known treatment effects for validating the measurement pipeline.

**Use Case**: System validation and testing, not production.

- Provides controlled test data for validating MEASURE accuracy
- Ground truth enables comparing estimated effects vs actual effects
