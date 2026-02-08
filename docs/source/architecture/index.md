# Architecture

## Contract Evolution (Prototype Phase)

Two simple rules to prevent breakage during rapid iteration:

1. **Producers can add fields freely** — Additive changes are always OK
2. **Consumers must be tolerant** — Ignore unknown fields, handle missing optional fields with defaults

No explicit versioning during prototype phase. Coordinate breaking changes manually.

> **Note**: For production, consider adding `schema_version` field and semantic versioning.

## Stateless Runs

Each run is independent. No persistent state between runs. This simplifies the system and makes runs reproducible.

## Fully Autonomous

No human approval gates. The orchestrator runs end-to-end without intervention.

## CI Bounds → Scenarios

The confidence interval from Measure maps directly to allocation scenarios:
- `ci_upper` → `R_best`
- `effect_estimate` → `R_med`
- `ci_lower` → `R_worst`

## Methodology-Based Confidence

Confidence scoring is primarily methodology-driven, not just statistical. An experiment with wide CI still beats a time-series with narrow CI.
