# Documentation Guidelines — Orchestrator

Ecosystem-wide conventions: see `docs/GUIDELINES.md` at the workspace root.
This file documents conventions specific to the orchestrator component.

---

## Page map

| Page | Purpose |
|------|---------|
| `README.md` | Package positioning and quick start. Also the docs landing page. |
| `guides/usage.md` | Three-step quickstart: write config → build orchestrator → call run(). |
| `configuration/index.md` | Full parameter reference: top-level, allocate block, initiatives list. |
| `pipeline/index.md` | Execution model: fan-out/fan-in, synchronisation points, stage contracts. |
| `api/index.md` | Auto-generated from source. Do not hand-edit. |
| `impact-loop/tutorial.ipynb` | End-to-end pipeline run across multiple initiatives. |

---

## Sidebar structure

```
Guides     → usage, configuration, pipeline, api
Tutorials  → impact-loop/tutorial
```

---

## Pipeline stage naming

Refer to pipeline stages in all-caps when naming the stage itself, lowercase when describing the action:

```
Good: The MEASURE stage runs in parallel across all initiatives.
Good: Each initiative is measured independently.
Bad:  The measure stage runs... (stage name should be caps)
Bad:  Each initiative is MEASUREd... (verb form should be lowercase)
```

---

## Tutorials

The impact-loop tutorial is executable — all components run from pip-installed packages,
no external API keys required for the default `evaluate_strategy: score` path.
