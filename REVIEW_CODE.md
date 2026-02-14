# Design Review: `impact_engine_orchestrator` (Code Design Mode)

## Design Summary

The package implements a fan-out/fan-in pipeline with four stages (MEASURE → EVALUATE → ALLOCATE → SCALE) using a clean plugin pattern: a single `PipelineComponent` ABC, concrete implementations injected into the `Orchestrator` at construction time, YAML-only config via dataclasses, and dataclass contracts for structural validation. The dependency graph is straightforward with external packages consumed only at the leaf level.

## Principle Violations

### 1. [MODERATE] Untyped dict-based inter-stage contracts

- **Principle**: Explicit Over Implicit / Fail Fast
- **Location**: `orchestrator.py:33-53`, `components/base.py:10`
- **Issue**: `PipelineComponent.execute` has signature `(event: dict) -> dict`. All inter-stage wiring operates on raw dicts. Dataclass contracts exist but are used only *inside* components for validation, then immediately serialized via `asdict()`. The orchestrator indexes into output dicts by string keys (`result["initiative_id"]`, `alloc_result["selected_initiatives"]`).
- **Impact**: Typos in dict keys produce runtime `KeyError` rather than static/IDE-detectable errors. The contracts in `contracts/` give a false sense of type safety — they document the shape but don't enforce it at the boundary where data crosses between stages.
- **Suggestion**: If dict portability is intentional (serverless/cross-language), document that rationale. Otherwise consider `TypedDict` for signatures or a lightweight validation wrapper in `_fan_out` that checks returned dicts against the expected contract.

### 2. [MODERATE] `_extract_estimates` is a large conditional dispatcher without extensibility

- **Principle**: Open/Closed Principle (OCP)
- **Location**: `components/measure/measure.py:14-82`
- **Issue**: Six `if model_type == "..."` blocks, each with model-specific key access patterns. Adding a new model type requires modifying this function. Each block has subtly different structure (some have `p_value`, some set `ci_lower == ci_upper == effect`).
- **Impact**: Grows linearly with model types. Varied structures per model type make bugs easy to introduce.
- **Suggestion**: A registry/strategy pattern (`EXTRACTORS: dict[str, Callable]`) or pushing extraction into the `impact_engine` package so each model returns a normalized format.

### 3. [MODERATE] Test helper duplication

- **Principle**: DRY
- **Location**: `tests/integration/test_mock_pipeline.py:10-29` and `tests/integration/test_real_allocate_pipeline.py:10-29`
- **Issue**: Nearly identical `_make_orchestrator` helpers — only the allocate component differs. Default `initiative_specs`, `PipelineConfig` construction, and `Orchestrator` assembly are duplicated verbatim.
- **Impact**: Constructor signature changes require updating both in lockstep.
- **Suggestion**: Extract into `conftest.py` with allocate component as a parameter.

### 4. [MODERATE] Docstring says 4 stages but constructor takes 3 components

- **Principle**: Principle of Least Surprise
- **Location**: `orchestrator.py:12`
- **Issue**: Docstring describes "MEASURE-EVALUATE-ALLOCATE-SCALE" pipeline, but the constructor only accepts `measure`, `evaluate`, `allocate`. SCALE reuses `self.measure`. A reader will look for a `scale` parameter that doesn't exist.
- **Suggestion**: Update docstring: "MEASURE-EVALUATE-ALLOCATE pipeline with SCALE reusing the MEASURE component at higher sample size."

### 5. [MINOR] `contracts/evaluate.py` is dead code

- **Principle**: YAGNI / KISS
- **Location**: `contracts/evaluate.py`
- **Issue**: Pure re-export of `EvaluateResult` — never imported by anything in the codebase. Unlike `contracts/types.py` which is actively used.
- **Suggestion**: Remove it, or commit to the symmetry by importing from it where `EvaluateResult` is used.

### 6. [MINOR] `p_value` coercion hides missing data

- **Principle**: Explicit Over Implicit
- **Location**: `components/measure/measure.py:113`
- **Issue**: When `_extract_estimates` returns `p_value=None` (all non-experiment models), `Measure.execute` silently converts it to `0.0`. A p-value of 0.0 means "perfect significance" but here means "not applicable."
- **Impact**: Downstream consumers could incorrectly treat these as having strong statistical evidence.
- **Suggestion**: Make `p_value: float | None` in `MeasureResult`, or use `float('nan')` with documented convention.

### 7. [MINOR] Confidence interval degeneracy for several model types

- **Principle**: Fail Fast / Explicit Over Implicit
- **Location**: `components/measure/measure.py:53-80`
- **Issue**: For `interrupted_time_series`, `subclassification`, and `metrics_approximation`, extraction sets `ci_lower = ci_upper = effect_estimate`. This passes the `MeasureResult` assertion but produces a degenerate CI (width=0) that communicates false precision. Downstream evaluate uses these as `return_best`/`return_worst`, so these models always show zero uncertainty range.
- **Suggestion**: Document explicitly, or add a flag indicating "CI not available" rather than degenerate values.

### 8. [MINOR] Runner script mixes presentation with invocation

- **Principle**: Separation of Concerns
- **Location**: `scripts/run_once.py:17-43`
- **Issue**: `print_reports` contains formatting logic (dollar signs, percentages) in the runner script. Acceptable for a single entry point but becomes problematic with multiple output formats.
- **Suggestion**: Fine for now. Extract if additional entry points are added.

## Strengths

1. **Clean Dependency Inversion** — Orchestrator depends only on the `PipelineComponent` abstraction; concretes injected at construction.
2. **Pragmatic ALLOCATE fan-in** — Single ABC, ALLOCATE documented as exception rather than a separate interface (KISS).
3. **Graceful empty allocation** — Budget too small → no selections → empty reports, tested explicitly.
4. **Configuration as data** — YAML-only, no inline defaults scattered through code.
5. **Eager contract validation** — `__post_init__` assertions catch malformed data early.
6. **Deterministic test design** — Explicit determinism checks (`result1 == result2`).
7. **Simple concurrency** — `ThreadPoolExecutor` in `_fan_out` is minimal, correct, futures collected in order.

## Recommendations

| # | Recommendation | Impact | Effort |
|---|----------------|--------|--------|
| 1 | Registry pattern for `_extract_estimates` | High | Medium |
| 2 | Clarify p-value & CI degeneracy semantics | Medium | Low |
| 3 | Extract shared test helper to `conftest.py` | Low | Very low |
| 4 | Fix orchestrator docstring (3→4 stage clarity) | Low | Trivial |
| 5 | Remove or utilize `contracts/evaluate.py` | Negligible | Trivial |
| 6 | Typed inter-stage contracts (if dict portability not needed) | High | High |
