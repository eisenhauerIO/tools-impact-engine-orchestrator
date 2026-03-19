# EVALUATE — Confidence Scoring

**Package**: [tools-impact-engine-evaluate](https://github.com/eisenhauerIO/tools-impact-engine-evaluate)

## Purpose

Assign a confidence score based on methodology reliability.

## Inputs (from MEASURE)

- Effect estimate + CI bounds
- Model type
- Diagnostics

## Produces

- Confidence score (0-1)
- Scenario returns (R_best, R_med, R_worst from CI bounds)

## Confidence by Methodology

Confidence ranges are defined per method reviewer. Two reviewers are currently registered:

| Model Type | Confidence Range | Rationale |
|------------|------------------|-----------|
| `experiment` | 0.85 - 1.0 | Gold standard: randomised assignment eliminates confounding |
| `quasi_experimental` | 0.60 - 0.85 | Strong but relies on identifying assumptions (parallel trends, instrument validity) |

## Config Key

Each initiative specifies its evaluation path via `evaluate_strategy` in the orchestrator config:

| Value | Behaviour |
|-------|-----------|
| `"score"` | Deterministic draw from the method's confidence range (default, no LLM dependency) |
| `"review"` | LLM-powered artifact review; requires evaluate backend config |
