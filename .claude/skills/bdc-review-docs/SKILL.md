---
name: bdc-review-docs
description: Review documentation against Impact Engine formatting conventions, structure guidelines, and infrastructure.
allowed-tools: Read, Grep, Glob, Bash(ls*), Bash(hatch run docs*)
---

# Review Documentation — Impact Engine

Audit documentation against Impact Engine ecosystem conventions. Produce a report of findings — do NOT fix anything unless explicitly asked.

This skill extends the `bdc-review-writing` skill with Impact Engine-specific conventions. Load `bdc-review-writing` at the start of the audit: its Part I covers generic formatting, and its Part II (Check Structure Compliance, Check Rendered Output, Check Infrastructure) supplies the steps referenced below.

## When to Use

- After restructuring documentation
- When adding a new documentation page or notebook
- Periodic health check on docs quality

## Workflow

### Step 1: Find Guidelines

Load guidelines in this order:

1. **Ecosystem-wide guidelines**: read `workbenches/impact-engine/docs/GUIDELINES.md`
   (repo `eisenhauerIO/workbenches-impact-engine`; `../../workbenches/impact-engine/docs/GUIDELINES.md`
   relative to a package repo). This file is the canonical source for formatting conventions, writing
   style, sidebar structure, tutorial conventions, and Sphinx infrastructure requirements.

2. **Package-specific guidelines**: read `docs/source/GUIDELINES.md` in the package repo
   (all four packages have one). It adds package-specific page maps, naming conventions,
   and tutorial execution rules.

If either file is missing, report it as the first finding.

### Step 2: Check Formatting Conventions

Audit all documentation source files (`.md`, `.rst`, and markdown cells in `.ipynb` notebooks) against `bdc-review-writing` Part I plus the Impact Engine-specific conventions below.

#### Product Name

| Rule | Example |
|------|---------|
| Title case on first mention per page | "Impact Engine measures..." |
| "the engine" as shorthand after first mention | "...the engine loads products..." |
| Never lowercase as a noun | "impact engine" on its own is wrong |

#### External Libraries

| Rule | Example |
|------|---------|
| First mention per page: linked | `[statsmodels](https://www.statsmodels.org/)` |
| Subsequent mentions: plain text, lowercase | statsmodels |
| Specific classes/functions: backticks, linked when useful | `` [`ols()`](url) `` |

Canonical library URLs:

| Library | URL |
|---------|-----|
| statsmodels | `https://www.statsmodels.org/` |
| causalml | `https://causalml.readthedocs.io/` |
| pysyncon | `https://github.com/sdfordham/pysyncon` |
| pandas | `https://pandas.pydata.org/` |
| NumPy | `https://numpy.org/` |

#### Code Elements

| Category | Format | Example |
|----------|--------|---------|
| Stage facades | backticks with parens | `` `measure_impact()` ``, `` `evaluate_confidence()` ``, `` `allocate_portfolio()` `` |
| Adapter/class names | backticks | `` `SubclassificationAdapter` `` |

#### Statistical and Methodological Terms

| Category | Format | Example |
|----------|--------|---------|
| Well-known acronyms | plain text, all caps | ATT, ATE, ATC, OLS, SARIMAX, ARIMA |

### Step 3: Check Structure Compliance

Follow **Check Structure Compliance** from `bdc-review-writing`.

### Step 4: Check Rendered Output

Follow **Check Rendered Output** from `bdc-review-writing`. Check the built HTML for broken links, anchor-only hrefs, missing formatting, and image/badge rendering.

### Step 5: Check Infrastructure

Follow **Check Infrastructure** from `bdc-review-writing`. Verify all items in its infrastructure table, including Matplotlib config and pre-commit hooks.

### Step 6: Report

Provide a structured summary:
- **Formatting**: violations of the conventions in Step 2, grouped by category
- **Structure**: missing pages, toctree gaps, naming issues
- **Rendered Output**: broken links, anchor-only hrefs, rendering problems
- **Infrastructure**: missing tooling or build problems
- **Recommendations**: prioritized actions to fix gaps

For each formatting issue, include:
1. **File**: path and line/cell reference
2. **Issue**: what's wrong
3. **Convention**: which rule it violates

## Arguments

Optionally specify a focus area.

Usage:
- `/bdc-review-docs` — Full audit (all steps)
- `/bdc-review-docs formatting` — Only check formatting conventions (Step 2)
- `/bdc-review-docs structure` — Only check structure compliance (Step 3)
- `/bdc-review-docs rendered` — Only check rendered output (Step 4)
- `/bdc-review-docs infra` — Only check infrastructure (Step 5)
