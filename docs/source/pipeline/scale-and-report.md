# SCALE and REPORT

## SCALE

**Package**: Reuses [tools-impact-engine-measure](https://github.com/eisenhauerIO/tools-impact-engine-measure)

SCALE is not a separate component — it is the orchestrator calling MEASURE a second time on the subset of initiatives that passed ALLOCATE, with larger sample sizes.

### Process

1. Take selected initiatives from ALLOCATE
2. Run MEASURE on each (with larger sample size / longer time window)
3. Compare scaled effect_estimate to pilot predictions
4. Generate outcome report

### Inputs (from ALLOCATE)

- Selected initiatives
- Predicted returns (from pilot MEASURE → EVALUATE)
- Budget allocated

### Produces

- Actual returns at scale (from scaled MEASURE)
- Prediction error (actual - predicted)
- Outcome report

## Outcome Report

The final deliverable documents predicted vs actual outcomes:

```
┌──────────────────────────────────────────────────────────────────────┐
│                       OUTCOME REPORT                                │
├──────────────────────────────────────────────────────────────────────┤
│ Initiative: Product Description Enhancement                         │
│ ──────────────────────────────────────────────────────────────────── │
│ Pilot Results:                                                      │
│   Effect Estimate: +12.5% conversion                                │
│   95% CI: [8.2%, 16.8%]                                             │
│   Confidence Score: 0.78 (quasi-experiment)                         │
│   Sample Size: 500 products                                         │
│                                                                     │
│ Scale Results:                                                      │
│   Sample Size: 5,000 products                                       │
│   Actual Effect: +11.8% conversion                                  │
│                                                                     │
│ Comparison:                                                         │
│   Predicted (median): +12.5%                                        │
│   Actual: +11.8%                                                    │
│   Prediction Error: -0.7% (within CI)                               │
│                                                                     │
│ Budget: $50,000 allocated                                           │
│ ROI: Estimated $425,000 incremental revenue                         │
└──────────────────────────────────────────────────────────────────────┘
```
