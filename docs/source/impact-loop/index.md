# The Impact Loop

*Learn, Decide, Repeat: From Idea to Impact*

## The Problem

Organizations launch dozens of initiatives every quarter — product changes, marketing campaigns, operational improvements. Most are measured inconsistently, if at all. An A/B test here, a before-and-after comparison there, an analyst's best guess somewhere else. The result: budgets are allocated based on intuition, the loudest advocate, or raw metrics that ignore how trustworthy the underlying measurement is.

There is no feedback loop. Pilot results rarely inform scale decisions in a structured way. Initiatives that fail at scale are written off without understanding whether the pilot measurement was flawed or the intervention simply did not generalize. The organization learns slowly, or not at all.

## The Idea

The impact loop is a repeatable decision process that turns ad-hoc initiative evaluation into a structured learning system. It asks five questions in sequence:

```{image} ../_static/overview.svg
:alt: Impact Loop Overview
:align: center
```

1. **MEASURE** — *What is the causal effect?* Run a small-scale pilot study for every initiative using rigorous causal inference methods.
2. **EVALUATE** — *How much should we trust this estimate?* Score each measurement's confidence based on methodology quality, not just statistical significance.
3. **ALLOCATE** — *Where should we invest?* Select a portfolio of initiatives to scale under a budget constraint, weighting both expected return and measurement confidence.
4. **SCALE** — *Does the prediction hold?* Re-measure the selected initiatives at full scale to test whether pilot predictions generalize.
5. **REPORT** — *What did we learn?* Compare predicted outcomes against actuals to close the feedback loop and calibrate future decisions.

The key word is *loop*. This is not a one-shot analysis. Initiatives that are dropped in one cycle can be re-studied with better methodologies and re-enter the next cycle with higher confidence. Initiatives that are funded provide ground-truth outcomes that calibrate future predictions. Each iteration makes the system sharper.

---

## How It Works

### SIMULATE — Controlled test environments

Before running the loop on real data, the system needs calibration. The [catalog generator](https://github.com/eisenhauerIO/tools-catalog-generator) produces fully synthetic datasets with known treatment effects — ground truth that lets the measurement engine be validated before it touches production data.

The simulator is configuration-driven and supports multiple generation backends (rule-based for interpretable patterns, ML-based for realistic distributions). It produces product catalogs, transaction metrics, and controlled treatment effects that mirror real business scenarios.

### MEASURE — Causal effect estimation

The [impact engine](https://github.com/eisenhauerIO/tools-impact-engine-measure) estimates the causal effect of each initiative on business metrics. It goes beyond simple before-and-after comparisons: depending on the available data, it applies experiments (A/B tests), quasi-experimental methods, interrupted time-series analysis, or observational models.

The engine uses an adapter architecture — data sources, statistical models, and storage backends are all pluggable. A single YAML configuration file selects which adapters to use for a given run. This means proprietary data sources or specialized models can integrate without modifying the core engine.

Each measurement produces an effect estimate (how much the initiative moved the metric), a confidence interval (the range of plausible effects), and a model type identifier (which methodology was used).

### EVALUATE — Confidence scoring

Not all measurements are equally trustworthy. A randomized experiment with a wide confidence interval still produces a more reliable estimate than an observational study with a narrow one, because the methodology controls for confounding variables that observational approaches cannot.

The evaluate stage assigns a confidence score (0 to 1) based primarily on methodology rigor:

| Model Type | Confidence Range | Rationale |
|---|---|---|
| Experiment (RCT) | 0.85 -- 1.00 | Gold standard causal inference |
| Quasi-experiment | 0.60 -- 0.84 | Strong identification, some assumptions |
| Time-series | 0.40 -- 0.59 | Trend-based, confounding risk |
| Observational | 0.20 -- 0.39 | Correlation-based, high bias risk |

This is the stage where measurement rigor pays off. High-confidence estimates carry more weight in the portfolio decision that follows.

### ALLOCATE — Portfolio selection under uncertainty

Given a limited budget, which initiatives should be scaled? The [allocation engine](https://github.com/eisenhauerIO/tools-impact-engine-allocate) solves this as a portfolio optimization problem using minimax regret — selecting the set of initiatives that minimizes the worst-case regret across plausible scenarios.

The confidence interval from MEASURE maps directly to scenarios: the upper bound becomes the best case, the point estimate becomes the median case, and the lower bound becomes the worst case. Each scenario is weighted by the confidence score from EVALUATE, so low-confidence measurements are effectively discounted.

The result is a funded portfolio — the subset of initiatives worth scaling — along with predicted returns and budget allocations for each.

### SCALE and REPORT — Closing the loop

Selected initiatives are re-measured at full scale using the same measurement engine, now with larger sample sizes that produce tighter confidence intervals. The outcome report compares each initiative's pilot prediction against its scale actual: predicted return, actual return, prediction error, and the confidence score that informed the decision.

This comparison is the learning signal. It answers whether the pilot measurement was a reliable predictor of real-world outcomes. Over multiple cycles, this data calibrates the confidence scoring — the system learns which methodologies predict well in which contexts.

---

## Architecture Principles

Five design principles cut across all packages in the ecosystem:

**Configuration-driven.** All behavior is controlled through YAML files. No hardcoded parameters, no environment-dependent logic. This makes runs reproducible and auditable.

**Pluggable adapters.** Data sources, statistical models, and storage backends are all interchangeable. Proprietary implementations integrate cleanly without forking the core codebase.

**Data contracts.** Each stage defines its inputs and outputs as validated contracts with explicit invariants. Stages communicate through these contracts, not through shared state.

**Methodology-based confidence.** The system trusts rigorous methods over precise-looking numbers. This is the central insight that distinguishes the impact loop from naive metric-based decision making.

**Stateless runs.** Each pipeline execution is independent and reproducible. No hidden state accumulates between runs.

---

## The Cycle Continues

The impact loop's value compounds over time. Initiatives that were dropped — because the budget ran out or the measurement confidence was too low — can be re-studied with more rigorous methodologies and re-enter the next cycle. Initiatives that were funded provide ground-truth outcomes that sharpen future confidence scoring. New initiatives enter alongside returning ones.

Each cycle produces better measurements, better-calibrated confidence scores, and better allocation decisions. That is the point of the loop: not a one-shot analysis, but a learning system that improves with every iteration.
