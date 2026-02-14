# Architecture Review: `impact_engine_orchestrator` (Cross-Tool Boundary Mode)

**Scope**: impact-engine-orchestrator + 3 external tools (impact-engine, impact-engine-evaluate, portfolio-allocation)

## Design Summary

The orchestrator implements a fan-out/fan-in pipeline: **MEASURE (pilot) → EVALUATE → ALLOCATE → MEASURE (scale) → REPORT**. Three external tools each own one stage; the orchestrator wires them together via a single `PipelineComponent` ABC (`execute(event: dict) -> dict`). Data flows as `asdict()`-serialized dataclasses. The orchestrator enriches inter-stage data with initiative-level parameters from config (e.g. `cost_to_scale`), keeping stage contracts clean. A `ThreadPoolExecutor` parallelizes fan-out stages; ALLOCATE is the single fan-in point.

## Contract Map

### Boundary 1: Config → MEASURE (pilot)

| | Details |
|---|---|
| **Producer** | `PipelineConfig` / `InitiativeConfig` (config.py) |
| **Consumer** | `Measure.execute()` (components/measure/measure.py) |
| **Contract** | `{"initiative_id": str}` |
| **Alignment** | Matched |
| **Risk** | Low — minimal surface, orchestrator constructs the input |

### Boundary 2: impact-engine → Measure adapter

| | Details |
|---|---|
| **Producer** | `evaluate_impact()` → `impact_results.json` (impact-engine, models/base.py `ModelResult.to_dict()`) |
| **Consumer** | `Measure._extract_estimates()` + `MeasureResult` (components/measure/measure.py) |
| **Contract** | JSON envelope: `{schema_version, model_type, data: {model_params, impact_estimates, model_summary}}` |
| **Alignment** | Partial — fields extracted correctly but `schema_version` is never checked |
| **Risk** | **Medium** — if MEASURE tool bumps schema to 3.0 with structural changes, the adapter breaks silently |

### Boundary 3: MEASURE → EVALUATE

| | Details |
|---|---|
| **Producer** | `MeasureResult` (contracts/measure.py) — serialized via `asdict()` |
| **Consumer** | `score_initiative()` (impact-engine-evaluate, scorer.py) |
| **Contract** | MeasureResult dict + orchestrator-enriched `cost_to_scale` |
| **Alignment** | Matched — field names align (`initiative_id`, `model_type`, `ci_upper`, `effect_estimate`, `ci_lower`, `cost_to_scale`, `sample_size`) |
| **Risk** | Low — types are shared (`ModelType` enum re-exported through contracts/types.py) |

### Boundary 4: EVALUATE → ALLOCATE

| | Details |
|---|---|
| **Producer** | `EvaluateResult` (impact-engine-evaluate, scorer.py) — serialized via `asdict()` |
| **Consumer** | `MockAllocate.execute()` / `MinimaxRegretAllocate.execute()` |
| **Contract** | `{"initiatives": [EvaluateResult dict, ...], "budget": float}` |
| **Alignment** | Matched (code-level) / **Mismatched (docs)** — docs use `R_best`/`R_med`/`R_worst`, code uses `return_best`/`return_median`/`return_worst` |
| **Risk** | Low at runtime; medium for new contributor confusion |

### Boundary 5: ALLOCATE → MEASURE (scale)

| | Details |
|---|---|
| **Producer** | `AllocateResult` (contracts/allocate.py) |
| **Consumer** | Orchestrator constructs scale inputs from `selected_initiatives` + `config.scale_sample_size` |
| **Contract** | `{"initiative_id": str, "sample_size": int}` |
| **Alignment** | Matched |
| **Risk** | Low — orchestrator mediates |

### Boundary 6: All stages → OutcomeReport

| | Details |
|---|---|
| **Producer** | `Orchestrator._generate_reports()` combining pilot, eval, alloc, scale dicts |
| **Consumer** | End user / downstream analysis |
| **Contract** | `OutcomeReport` dataclass (contracts/report.py) |
| **Alignment** | Matched |
| **Risk** | Low — all fields sourced from validated upstream outputs |

## Data Flow Diagram

```
Config (YAML)
  │
  ├── initiative_id ──────────────────────────────────┐
  ├── cost_to_scale ────────────────────┐              │
  ├── budget ───────────────────────────┼──┐           │
  └── scale_sample_size ────────────────┼──┼───┐       │
                                        │  │   │       │
STEP 1: MEASURE (pilot)  ──fan-out──►  [MeasureResult ×N]
  │  input: {initiative_id}                │   │       │
  │  calls: evaluate_impact() ─► JSON      │   │       │
  │  extracts: _extract_estimates()        │   │       │
  │  validates: MeasureResult.__post_init__│   │       │
  ▼                                        │   │       │
STEP 2: EVALUATE  ────────fan-out──►  [EvaluateResult ×N]
  │  input: MeasureResult + cost_to_scale ─┘   │       │
  │  produces: confidence, scenario returns    │       │
  ▼                                            │       │
STEP 3: ALLOCATE  ────────fan-in───►  AllocateResult ×1
  │  input: {initiatives: [N], budget} ────────┘       │
  │  produces: selected_initiatives (K ≤ N)            │
  ▼                                                    │
STEP 4: MEASURE (scale)  ──fan-out──►  [MeasureResult ×K]
  │  input: {initiative_id, sample_size} ──────────────┘
  │  reuses same Measure component
  ▼
STEP 5: GENERATE REPORTS  ──fan-in──►  [OutcomeReport ×K]
     compares predicted (ALLOCATE) vs actual (SCALE)
```

**Key enrichment point**: Between steps 1 and 2, the orchestrator injects `cost_to_scale` from config into each MeasureResult dict. This is the only point where the orchestrator adds data not produced by a stage.

## Principle Violations

### 1. [MODERATE] `p_value` coercion: `None → 0.0`

- **Principle**: Explicit Over Implicit
- **Location**: `components/measure/measure.py:113`
- **Issue**: For model types without p-values (synthetic_control, NNM, ITS, subclassification, metrics_approximation), `_extract_estimates` returns `p_value: None`, which is then silently coerced to `0.0`. A p-value of 0.0 means "perfectly significant" — the opposite of "not applicable".
- **Impact**: Downstream consumers or analysts inspecting `p_value` will misinterpret the statistical evidence. The test `assert 0.0 <= pilot["p_value"] <= 1.0` passes but validates the wrong semantic.
- **Suggestion**: Use `float("nan")` as a sentinel for "not applicable". Update `MeasureResult.__post_init__` to allow NaN. Alternatively, make `p_value` `Optional[float]`.

### 2. [MODERATE] Degenerate CI bounds for 3 model types

- **Principle**: Data Flow Invariants / Cross-Boundary Invariants
- **Location**: `components/measure/measure.py:52-80`
- **Issue**: For `interrupted_time_series`, `subclassification`, and `metrics_approximation`, `_extract_estimates` sets `ci_lower = ci_upper = effect_estimate`. This satisfies the MeasureResult invariant (`ci_lower <= effect_estimate <= ci_upper`) but makes EVALUATE's scenario returns collapse: `return_worst == return_median == return_best`. The risk quantification (best/worst case) that ALLOCATE relies on becomes meaningless for these model types.
- **Impact**: ALLOCATE's portfolio optimization cannot differentiate upside from downside for ~3/9 model types. Decisions become confidence-driven only, ignoring return uncertainty.
- **Suggestion**: If the upstream model truly provides no CI, document this as a known limitation and consider whether ALLOCATE should weight these initiatives differently. Long-term: extend these model types upstream to produce real CIs.

### 3. [MODERATE] `schema_version` unchecked at MEASURE boundary

- **Principle**: Breaking Change Detection / Fail at the Boundary
- **Location**: `components/measure/measure.py:103-106`
- **Issue**: The `impact_results.json` envelope contains `schema_version: "2.0"` (from `SCHEMA_VERSION` in models/base.py). The Measure adapter reads this JSON but never checks the version. If the MEASURE tool releases a schema 3.0 with renamed or restructured fields, the adapter will fail with a `KeyError` deep inside `_extract_estimates`, with no helpful error message.
- **Impact**: Silent or confusing breakage after MEASURE tool upgrades.
- **Suggestion**: Add a version check at the top of `Measure.execute()`: read `schema_version` from the JSON, assert it starts with `"2."`, and raise a clear error otherwise. This costs 2 lines and catches the most dangerous breaking change vector in the system.

### 4. [MODERATE] Documentation-code drift on field names

- **Principle**: Explicit Over Implicit
- **Location**: `docs/source/pipeline/contracts.md` vs `impact_engine_evaluate/scorer.py`
- **Issue**: Three misalignments between documented contracts and code:
  - **Evaluate → Allocate fields**: Docs say `R_best`, `R_med`, `R_worst`; code uses `return_best`, `return_median`, `return_worst`
  - **ModelType enum**: Docs list 4 values; code has 9
  - **diagnostics invariant**: Docs say "must contain `r_squared` or `log_likelihood`"; code doesn't validate diagnostics content
- **Impact**: New contributors implementing against the docs will hit field name mismatches. The docs become unreliable as a contract reference.
- **Suggestion**: Update contracts.md to reflect actual field names. Consider generating contract docs from the dataclass definitions to prevent future drift.

### 5. [MODERATE] No formal contract for ALLOCATE input

- **Principle**: Explicit Over Convention
- **Location**: `orchestrator.py:41-46`
- **Issue**: The ALLOCATE input `{"initiatives": [EvaluateResult dict, ...], "budget": float}` has no dataclass or schema definition. It's an implicit dict contract constructed inline by the orchestrator. Every other boundary has a named dataclass.
- **Impact**: The fan-in interface is the most complex in the pipeline (aggregates N results + config param), yet it's the only one without a formal definition. New ALLOCATE implementations must reverse-engineer the expected input from MockAllocate's code.
- **Suggestion**: Create an `AllocateInput` dataclass in `contracts/allocate.py` for symmetry and discoverability.

### 6. [MINOR] Pilot/scale artifact overwrite

- **Principle**: Principle of Least Surprise
- **Location**: `components/measure/measure.py:97-101` — `job_id=initiative_id` for both pilot and scale
- **Issue**: Both pilot and scale MEASURE runs use the same `job_id` (the `initiative_id`). The scale run overwrites the pilot's `impact_results.json` and artifacts on disk. Pipeline results in memory are unaffected, but on-disk observability shows only the scale run.
- **Impact**: Debugging pilot vs scale discrepancies requires re-running with custom job_ids. Low severity since in-memory results are correct.
- **Suggestion**: Prefix job_id with phase: `f"pilot-{initiative_id}"` / `f"scale-{initiative_id}"`.

### 7. [MINOR] `cost_to_scale` → `cost` rename across boundary

- **Principle**: Principle of Least Surprise
- **Location**: Config uses `cost_to_scale`; orchestrator enriches with `cost_to_scale`; `score_initiative()` maps it to `EvaluateResult.cost`; ALLOCATE reads `.cost`
- **Issue**: The same concept has two names depending on pipeline position. Not a bug (the rename is explicit in `score_initiative`), but adds cognitive load when tracing data flow.
- **Impact**: Minor — anyone debugging "where does cost come from?" must trace through the scorer to find the rename.
- **Suggestion**: Document the rename in the Evaluate → Allocate contract section.

### 8. [MINOR] Evaluate adapter's fallback PipelineComponent

- **Principle**: Dependency Inversion / Explicit Over Implicit
- **Location**: `_external/tools-impact-engine-evaluate/impact_engine_evaluate/adapter.py:10-18`
- **Issue**: The Evaluate adapter tries to import `PipelineComponent` from the orchestrator; on failure, it defines its own identical ABC. This means `isinstance(Evaluate(), PipelineComponent)` is `True` only when the orchestrator is installed.
- **Impact**: Low — Python duck typing makes this work. But it reveals a dependency direction question: should the ABC live in a shared package rather than the orchestrator?
- **Suggestion**: Acceptable for now (prototype phase). For production, consider extracting `PipelineComponent` into a shared `impact-engine-contracts` package.

## Strengths

1. **Clean enrichment pattern**: The orchestrator's explicit injection of `cost_to_scale` between MEASURE and EVALUATE keeps stage contracts free of passthrough parameters. Each stage only produces its own outputs.

2. **Dataclass contracts with runtime invariants**: `MeasureResult.__post_init__` validates CI bounds and sample size at construction time, catching upstream errors immediately rather than letting them propagate.

3. **Dependency injection**: The Orchestrator accepts `PipelineComponent` instances, making it trivial to swap MockAllocate for MinimaxRegretAllocate or any future implementation.

4. **Deterministic reproducibility**: Seeded confidence scoring (`_stable_seed` on initiative_id) ensures identical results across runs, which is validated by dedicated determinism tests.

5. **Empty allocation handling**: The system gracefully handles budgets too small for any initiative — SCALE is skipped, outcome reports are empty, no errors. This is explicitly tested.

6. **Two-level parameter design**: Separating problem-level (budget, scale_sample_size) from initiative-level (initiative_id, cost_to_scale) parameters prevents config sprawl and makes the orchestrator's role as enricher clear.

7. **Integration tests validate full contracts**: `test_contract_invariants` checks cross-boundary invariants end-to-end (CI bounds, confidence range, budget allocation consistency, prediction error math), not just unit-level correctness.

8. **Stateless runs**: No persistent state between runs. Each `orchestrator.run()` is independent, making the system easy to reason about and test.

## Evolution Risks

| Change | Blast radius | Detection |
|--------|-------------|-----------|
| MEASURE tool renames `impact_estimates` key | Orchestrator `_extract_estimates` crashes with KeyError | **Undetected** until runtime — no schema_version check |
| MEASURE adds new model_type (e.g. `difference_in_differences`) | `_extract_estimates` raises `ValueError("Unknown model_type")` | Detected at runtime, but requires Measure adapter update |
| EVALUATE adds new field to EvaluateResult | Additive, safe — ALLOCATE ignores unknown fields | N/A |
| EVALUATE removes `confidence` field | ALLOCATE scores crash (MockAllocate reads `i["confidence"]`) | **Undetected** until runtime |
| ALLOCATE changes output schema (e.g. renames `selected_initiatives`) | Orchestrator `_generate_reports` crashes | **Undetected** until runtime |
| ModelType enum adds new value | Safe — CONFIDENCE_MAP lookup would fail with KeyError in scorer | Detected at EVALUATE stage |
| Config adds new initiative-level param | Safe — Orchestrator only reads known fields | N/A |

**Highest-risk evolution vector**: MEASURE tool schema changes. It's the only external tool where the orchestrator parses raw output (JSON) rather than receiving structured data through a typed interface.

## Recommendations

| # | Recommendation | Impact | Effort |
|---|----------------|--------|--------|
| 1 | Check `schema_version` at MEASURE boundary | High | Low |
| 2 | Fix `p_value` coercion (`None → 0.0` → `nan` or `Optional`) | Medium | Low |
| 3 | Update contracts.md to match code field names | Medium | Low |
| 4 | Create `AllocateInput` dataclass | Medium | Low |
| 5 | Document degenerate CI bounds for ITS/subclassification/metrics_approximation | Informational | Low |
| 6 | Disambiguate pilot/scale job_ids | Nice-to-have | Low |
