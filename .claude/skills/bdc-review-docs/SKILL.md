---
name: bdc-review-docs
description: Review documentation against Impact Engine formatting conventions, structure guidelines, and infrastructure.
allowed-tools: Read, Grep, Glob, Bash(ls*), Bash(hatch run docs*)
---

# Review Documentation — Impact Engine

Audit documentation against Impact Engine ecosystem conventions. Produce a report of findings — do NOT fix anything unless explicitly asked.

This skill extends the general review-docs workflow with Impact Engine-specific formatting conventions. For generic checks (structure, rendered output, infrastructure), follow the general skill at:

    .claude/.cache/utils-agentic-support/claude/skills/code/review/review-writing/SKILL.md

Read that file at the start of the audit to load the generic workflow steps referenced below.

## When to Use

- After restructuring documentation
- When adding a new documentation page or notebook
- Periodic health check on docs quality

## Workflow

### Step 1: Find Guidelines

Load guidelines in this order:

1. **Ecosystem-wide guidelines**: read `docs/GUIDELINES.md` at the workspace root
   (two levels above the component repo: `../../docs/GUIDELINES.md` relative to the component root).
   This file is the canonical source for formatting conventions, writing style, sidebar structure,
   tutorial conventions, and Sphinx infrastructure requirements.

2. **Component-specific guidelines**: read `docs/source/GUIDELINES.md` in the current component repo.
   This file references the ecosystem guidelines and adds component-specific page maps,
   naming conventions, and tutorial execution rules.

If either file is missing, report it as the first finding.

### Step 2: Check Formatting Conventions

Audit all documentation source files (`.md`, `.rst`, and markdown cells in `.ipynb` notebooks) against the conventions below. These apply across the entire Impact Engine ecosystem.

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
| Functions/methods | backticks with parens | `` `evaluate_impact()` `` |
| Column/field names | backticks | `` `revenue` ``, `` `product_id` `` |
| Config keys/values | backticks | `` `storage_url` `` |
| File names (no link) | backticks | `` `engine.py` `` |
| Adapter/class names | backticks | `` `SubclassificationAdapter` `` |
| Classes/interfaces (with source) | markdown link | `[MetricsManager](path)` |
| Files (with source) | markdown link | `[engine.py](path)` |

#### Statistical and Methodological Terms

| Category | Format | Example |
|----------|--------|---------|
| Well-known acronyms | plain text, all caps | ATT, ATE, ATC, OLS, SARIMAX, ARIMA |
| Design patterns | bold | **adapter pattern**, **data contracts** |
| Key architectural concepts | bold | **plugin architecture** |
| Tools/services | plain text | GitHub Actions, S3 |
| File formats | plain text | YAML, JSON |

### Step 3: Check Structure Compliance

Follow **Step 2 (Check Structure Compliance)** from the general skill.

### Step 4: Check Rendered Output

Follow **Step 4 (Check Rendered Output)** from the general skill. Check the built HTML for broken links, anchor-only hrefs, missing formatting, and image/badge rendering.

### Step 5: Check Infrastructure

Follow **Step 5 (Check Infrastructure)** from the general skill. Verify all items in the general skill's infrastructure table, including Matplotlib config and pre-commit hooks.

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
