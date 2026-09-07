# Canonical README Template — Impact Engine Components

This template defines the standard README structure for impact-engine pipeline packages
(measure, evaluate, allocate). The orchestrator is excluded — it uses a design-document format.

## Template

~~~markdown
# Impact Engine — {Stage}

[![CI](https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/ci.yaml/badge.svg)](https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/ci.yaml)
[![Docs](https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/eisenhauerIO/tools-impact-engine-{stage}/actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/eisenhauerIO/tools-impact-engine-{stage}/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Slack](https://img.shields.io/badge/Slack-Join%20Us-4A154B?logo=slack)](https://join.slack.com/t/eisenhauerioworkspace/shared_invite/zt-3lxtc370j-XLdokfTkno54wfhHVxvEfA)

*{One-line tagline — what the package does, not how}*

{Problem paragraph — 2-3 sentences explaining why this matters}

{Solution paragraph — 2-3 sentences explaining what the package does and how it fits in the pipeline}

Visit our [documentation](https://eisenhauerio.github.io/tools-impact-engine-{stage}/) for details.
~~~

## Rules

### Title
- Format: `# Impact Engine — {Stage}` (em dash, not hyphen)
- Stage name is title case: Measure, Evaluate, Allocate

### Badges
- Exactly 5 badges, in this order: CI, Docs, License, Ruff, Slack
- All on a single line, no blank lines between them

### Tagline
- Italic, single sentence
- Describes *what* the package does, not *how*
- No period at the end

### Opening Paragraphs
- First paragraph: the problem (why this matters)
- Second paragraph: the solution (what the package does)
- **README is the source of truth for component messaging.** science.html derives from it:
  - science.html science explanation ← README problem paragraph (adapted for business audience)
  - science.html software paragraph ← README solution paragraph (adapted for mixed audience)
- When you update the README paragraphs, update science.html to match

### Documentation Link
- Single line: `Visit our [documentation](https://eisenhauerio.github.io/tools-impact-engine-{stage}/) for details.`
- No Quick Start, no Development commands — all instructional content lives in the Sphinx docs

## Alignment with science.html

Each component's README tagline and solution paragraph must be consistent with the
corresponding `<h4>` software paragraph in `promotion/tools-impact-engine-website/science.html`. When updating
either, check the other.

| Stage | science.html Section | README Tagline Alignment |
|-------|---------------------|--------------------------|
| Measure | Causal Inference — What happened? | Tagline about causal impact measurement |
| Evaluate | Evidence Assessment — What did we learn? | Tagline about confidence/evidence scoring |
| Allocate | Decision Theory — What should we do? | Tagline about portfolio optimization |
