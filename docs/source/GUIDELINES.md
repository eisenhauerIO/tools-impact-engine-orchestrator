# Documentation Guidelines — Orchestrator

Ecosystem-wide conventions: see `docs/GUIDELINES.md` at the workspace root.
This file documents conventions specific to the orchestrator component.

---

## Page map

| Page | Purpose |
|------|---------|
| `README.md` | Package positioning and quick start. Also the docs landing page. |
| `guides/usage.md` | Quickstart: write config → call `run_pipeline()` → read results. |
| `configuration/index.md` | Full parameter reference: top-level keys, **ALLOCATE** block, **INITIATIVES** list. |
| `api/index.md` | Auto-generated from source. Do not hand-edit. |
| `impact-loop/impact-loop.ipynb` | End-to-end pipeline run across multiple initiatives. |

---

## Sidebar structure

```
Guides     → usage, configuration, api
Tutorials  → impact-loop/impact-loop
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

The impact-loop tutorial is marked non-executable (`nbsphinx execute: never`) because it
requires `setup_data.py` to be run first to generate simulated product catalogs. Notebooks
are tested separately via `pytest --nbmake`.
