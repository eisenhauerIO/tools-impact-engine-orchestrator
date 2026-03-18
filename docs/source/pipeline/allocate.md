# ALLOCATE — Portfolio Selection

**Package**: [tools-impact-engine-allocate](https://github.com/eisenhauerIO/tools-impact-engine-allocate)

## Purpose

Select which initiatives to scale given a limited budget.

## Inputs (from EVALUATE)

- Confidence scores
- Scenario returns (R_best, R_med, R_worst)
- Costs to scale each initiative

## Produces

- Selected initiatives for scaling
- Budget allocation per initiative
- Predicted returns

## Algorithm

Minimax regret optimization (linear programming). The decision rule minimizes the worst-case regret across return scenarios, producing a budget-feasible portfolio.

```python
from impact_engine_allocate import allocate_portfolio

result = allocate_portfolio(
    config={"budget": budget, "costs": costs, "rule": "minimax_regret"},
    data_dir="./results"
)
```

## Fan-In Exception

ALLOCATE is the only fan-in stage. It receives **all** evaluated initiatives as a batch and returns a single portfolio selection. This is inherent to the allocation problem: you cannot select a portfolio by looking at initiatives one at a time.
