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

Minimax regret optimization (linear programming).

```python
from support import solve_minimax_regret_optimization

result = solve_minimax_regret_optimization(
    initiatives=initiatives,
    budget=budget,
    scenarios=["best", "med", "worst"]
)
```

## Fan-In Exception

ALLOCATE is the only fan-in stage. It receives **all** evaluated initiatives as a batch and returns a single portfolio selection. This is inherent to the allocation problem: you cannot select a portfolio by looking at initiatives one at a time.
