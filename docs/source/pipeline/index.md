# Pipeline

The orchestrator executes a fan-out/fan-in pipeline across multiple initiatives.

## Execution Model

MEASURE and EVALUATE process multiple initiatives in parallel. ALLOCATE receives all results and runs once. SCALE fans out again over the selected subset.

```{image} ../_static/pipeline.svg
:alt: Pipeline Execution Pattern
:align: center
```

## Synchronization Points

| Point | Trigger | Action |
|-------|---------|--------|
| After MEASURE | All initiatives measured | Collect results → EVALUATE |
| After EVALUATE | All initiatives evaluated | Collect results → ALLOCATE |
| After ALLOCATE | Portfolio selected | Fan-out to SCALE |
| After SCALE | All scaled initiatives complete | Generate Outcome Report |

## Handler Interface

Each component processes a **single initiative** and returns a single result. Parallelism is handled by the orchestrator, not the handlers.

> **Exception**: ALLOCATE is a fan-in component — it receives all evaluated initiatives as a batch (`{"initiatives": [...], "budget": ...}`) and returns a single portfolio selection. This is inherent to the allocation problem: you can't select a portfolio by looking at initiatives one at a time.

```python
def handler(event: dict, context=None) -> dict:
    """Lambda-compatible interface for a single initiative."""
    # Process one initiative
    return result
```

## Deployment Strategy

| Environment | Orchestration | Parallelism |
|-------------|---------------|-------------|
| Local Dev | Python script | `concurrent.futures.ThreadPoolExecutor` |
| AWS Production | Step Functions | `Map` state with `MaxConcurrency` |

The handler interface is identical in both environments.

```{toctree}
:maxdepth: 1

measure
evaluate
allocate
scale-and-report
contracts
```
