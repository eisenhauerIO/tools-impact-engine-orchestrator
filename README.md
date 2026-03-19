# Impact Engine — Orchestrator

[![CI](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/actions/workflows/ci.yaml/badge.svg)](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/actions/workflows/ci.yaml)
[![Docs](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/actions/workflows/docs.yaml/badge.svg?branch=main)](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/actions/workflows/docs.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/eisenhauerIO/tools-impact-engine-orchestrator/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Slack](https://img.shields.io/badge/Slack-Join%20Us-4A154B?logo=slack)](https://join.slack.com/t/eisenhauerioworkspace/shared_invite/zt-3lxtc370j-XLdokfTkno54wfhHVxvEfA)

*Fan-out/fan-in pipeline runner for scaling pilot experiments to full deployment*

Running a single causal study is hard enough. Running a portfolio of pilots — measuring effects, scoring confidence, selecting winners, and validating at scale — means stitching together independent analysis steps, synchronizing results, and managing a fan-out/fan-in execution pattern. Most teams build this glue code from scratch for every engagement.

**Impact Engine — Orchestrator** wires the full MEASURE → EVALUATE → ALLOCATE → SCALE pipeline into one config-driven run. A YAML file defines your initiatives, budget, and component settings. The orchestrator fans out pilot measurements in parallel, collects confidence-scored results, runs portfolio selection, then scales the winners — producing an outcome report that compares predicted vs actual impact. Swap any pipeline component by changing one line in the config.

<p align="center">
  <img src="docs/source/_static/overview.svg" alt="Impact Engine Orchestrator Overview">
</p>

Visit our [documentation](https://eisenhauerio.github.io/tools-impact-engine-orchestrator/) for details.
