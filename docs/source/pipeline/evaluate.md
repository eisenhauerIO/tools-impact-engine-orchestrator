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

| Model Type | Confidence Range | Rationale |
|------------|------------------|-----------|
| Experiment (RCT) | 0.85 - 1.0 | Gold standard causal inference |
| Quasi-experiment | 0.60 - 0.84 | Strong but with assumptions |
| Time-series | 0.40 - 0.59 | Trend-based, confounding risk |
| Observational | 0.20 - 0.39 | Correlation, high bias risk |
