# Impact Engine Loop - Design Document

## Overview

The Impact Engine Loop is an orchestration system for **scaling pilot experiments to full deployment**. It ties together four specialized packages: simulate ground-truth data, measure impact from pilots, review confidence levels with AI, and allocate limited resources to scale the most promising initiatives.

The core insight: run small pilots first, then invest in scaling only the initiatives that show both high impact and high confidence.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         IMPACT ENGINE LOOP                                   │
│                                                                              │
│  ┌────────────────┐                                                          │
│  │   SIMULATE     │  (Generates ground-truth data for validation)            │
│  │   [Optional]   │                                                          │
│  └───────┬────────┘                                                          │
│          ▼                                                                   │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐             │
│  │   MEASURE      │───▶│    REVIEW      │───▶│   ALLOCATE     │             │
│  │   (Pilot)      │    │   (Agentic)    │    │   (Minimax)    │             │
│  │                │    │                │    │                │             │
│  │ Effect Est.    │    │ Confidence     │    │ Portfolio      │             │
│  │ + CI Bounds    │    │ Scores         │    │ Selection      │             │
│  └────────────────┘    └────────────────┘    └───────┬────────┘             │
│                                                      │                       │
│          ┌───────────────────────────────────────────┘                       │
│          ▼                                                                   │
│  ┌────────────────┐    ┌────────────────────────────────────────┐           │
│  │   MEASURE      │───▶│           OUTCOME REPORT               │           │
│  │   (Scale)      │    │   Predicted (from pilot) vs Actual     │           │
│  │                │    │   benefit documentation                │           │
│  │ Larger Samples │    └────────────────────────────────────────┘           │
│  └────────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Demo Flow

For the demo, each run is independent:

```
MEASURE (Pilot) → REVIEW → ALLOCATE → MEASURE (Scale) → Outcome Report
```

No persistent state between runs. No human approval gates (fully autonomous).

---

## System Components

### 1. SIMULATE - Online Retail Simulator (Ground Truth)
**Package**: `tools-catalog-generator`

**Purpose**: Generate synthetic product data with known treatment effects for validating the measurement pipeline.

**Key Capabilities**:
- Two-phase generation: characteristics → metrics
- Enrichment system for applying treatment effects with known ground truth
- Quality score tracking (0.0-1.0)

**Loop Role**:
- Provides controlled test data for validating Measure accuracy
- Ground truth enables comparing estimated effects vs actual effects
- Used for system validation, not in production demo flow

---

### 2. MEASURE - Impact Engine
**Package**: `tools-impact-engine-measure`

**Purpose**: Evaluate the causal impact of interventions using statistical models.

**Key Capabilities**:
- Multiple model types: experiments (RCT), interrupted time series, observational
- Adapter-based architecture (metrics, models, storage)
- Configuration-driven pipeline
- Produces effect estimates with confidence intervals

**Loop Role - Pilot Phase**:
- Runs causal analysis on small-sample pilot data
- Produces effect estimates with upper/lower confidence bounds
- Model type determines baseline confidence (experiment > quasi-experiment > time-series)

**Loop Role - Scale Phase**:
- Re-runs analysis with larger samples for selected initiatives
- Documents actual outcomes for comparison with pilot predictions

**Key Entry Point**:
```python
from impact_engine import evaluate_impact

result_path = evaluate_impact(
    config_path="config.yaml",
    storage_url="./results"
)
```

---

### 3. REVIEW - Agentic Review
**Package**: `tools-impact-engine-review`

**Purpose**: AI-powered assessment of impact estimates and confidence levels.

**Key Capabilities**:
- Strands agent framework (AWS Bedrock or Ollama)
- Evaluates statistical validity
- Assesses methodology reliability

**Loop Role**:
- Consumes effect estimates + confidence intervals from Measure
- Assigns confidence score based on methodology reliability:
  - **Experiment (RCT)**: Highest confidence
  - **Quasi-experiment**: Medium confidence
  - **Time-series**: Lowest confidence
- Translates confidence intervals to scenario returns (R_best, R_med, R_worst)
- Flags concerns or data quality issues

**Key Entry Point**:
```python
from framework.strands_agent import create_strands_agent

review_agent = create_strands_agent(
    system_prompt=review_prompt,
    tools=[impact_tools],
    model=model
)
```

---

### 4. ALLOCATE - Portfolio Optimization
**Package**: `tools-impact-engine-allocate`

**Purpose**: Determine which initiatives to scale given a limited budget.

**Key Capabilities**:
- Minimax regret optimization (linear programming)
- Multi-scenario analysis (best/medium/worst case from confidence bounds)
- Confidence-penalized decision making

**Loop Role**:
- Receives from Review:
  - Impact estimates
  - Scenarios (R_best, R_med, R_worst from confidence bounds)
  - Confidence scores (methodology-based reliability)
  - Costs (to scale each initiative)
- Given budget constraint, selects optimal portfolio to scale
- Selected initiatives proceed to Scale phase

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

## Data Flow Contracts

### Measure (Pilot) → Review

| Field | Type | Description |
|-------|------|-------------|
| initiative_id | string | Identifier for the initiative |
| effect_estimate | float | Estimated causal effect (point estimate) |
| ci_lower | float | Lower bound of confidence interval |
| ci_upper | float | Upper bound of confidence interval |
| p_value | float | Statistical significance |
| sample_size | int | Number of observations in pilot |
| model_type | string | experiment / quasi-experiment / time-series |
| diagnostics | dict | Model fit diagnostics |

### Review → Allocate

| Field | Type | Description |
|-------|------|-------------|
| id | string | Initiative identifier |
| confidence | float | Methodology-based confidence (0-1) |
| cost | float | Cost to scale this initiative |
| R_best | float | Upper CI bound → best-case return |
| R_med | float | Point estimate → median return |
| R_worst | float | Lower CI bound → worst-case return |
| model_type | string | Source methodology |
| flags | list | Concerns or data quality issues |

### Allocate → Measure (Scale)

| Field | Type | Description |
|-------|------|-------------|
| selected_initiatives | list | Initiatives approved for scaling |
| predicted_returns | dict | Expected returns from pilot (per initiative) |
| budget_allocated | dict | Budget allocated per initiative |

### Measure (Scale) → Outcome Report

| Field | Type | Description |
|-------|------|-------------|
| initiative_id | string | Initiative identifier |
| predicted_return | float | Return predicted from pilot |
| actual_return | float | Observed return at scale |
| prediction_error | float | Difference (actual - predicted) |
| sample_size_pilot | int | Original pilot sample |
| sample_size_scale | int | Scale sample size |

---

## Confidence Scoring

The Review agent assigns confidence based on methodology reliability:

| Model Type | Confidence Range | Rationale |
|------------|------------------|-----------|
| Experiment (RCT) | 0.85 - 1.0 | Gold standard causal inference |
| Quasi-experiment | 0.60 - 0.84 | Strong but with assumptions |
| Interrupted Time Series | 0.40 - 0.59 | Trend-based, confounding risk |
| Observational | 0.20 - 0.39 | Correlation, high bias risk |

Confidence is further adjusted by:
- Sample size adequacy
- Statistical significance
- Data quality indicators
- Pre-trend checks (for time series)

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
│   Prediction Error: -0.7% (within CI ✓)                              │
│                                                                      │
│ Budget: $50,000 allocated                                            │
│ ROI: Estimated $425,000 incremental revenue                          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Decisions

### 1. Stateless Runs
Each demo run is independent. No persistent state between runs. This simplifies the system and makes runs reproducible.

### 2. Fully Autonomous
No human approval gates. The loop runs end-to-end without intervention.

### 3. Confidence Bounds → Scenarios
The confidence interval from Measure maps directly to allocation scenarios:
- `ci_upper` → `R_best`
- `effect_estimate` → `R_med`
- `ci_lower` → `R_worst`

### 4. Methodology-Based Confidence
Confidence scoring is primarily methodology-driven, not just statistical. An experiment with wide CI still beats a time-series with narrow CI.
