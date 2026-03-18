"""Shared fixtures for orchestrator tests."""

import json

import pandas as pd
import pytest
import yaml

from impact_engine_orchestrator.components.measure.measure import Measure
from impact_engine_orchestrator.config import InitiativeConfig


@pytest.fixture()
def measure_env(tmp_path):
    """Provide helpers to create real Measure instances backed by measure_impact.

    Returns (make_initiative, make_measure, storage_url) where:
    - make_initiative(id, cost) creates an InitiativeConfig with a working measure config
    - make_measure() creates a Measure adapter wired to the temp storage
    - storage_url is the path to the storage directory (used as data_dir for allocate)
    """
    n = 50
    products_df = pd.DataFrame(
        {
            "product_id": [f"prod_{i:03d}" for i in range(n)],
            "name": [f"Product {i}" for i in range(n)],
            "category": ["Electronics"] * n,
            "price": [round(50 + (i * 3.5) % 200, 2) for i in range(n)],
        }
    )
    products_path = tmp_path / "products.csv"
    products_df.to_csv(products_path, index=False)

    storage_url = str(tmp_path / "storage")
    config_cache = {}

    def make_initiative(initiative_id, cost_to_scale):
        if initiative_id not in config_cache:
            config = {
                "DATA": {
                    "SOURCE": {
                        "type": "simulator",
                        "CONFIG": {
                            "path": str(products_path),
                            "mode": "rule",
                            "seed": 42,
                            "start_date": "2024-01-08",
                            "end_date": "2024-01-08",
                        },
                    },
                    "ENRICHMENT": {
                        "FUNCTION": "product_detail_boost",
                        "PARAMS": {
                            "enrichment_fraction": 0.5,
                            "enrichment_start": "2024-01-08",
                            "quality_boost": 0.15,
                            "seed": 42,
                        },
                    },
                },
                "MEASUREMENT": {
                    "MODEL": "experiment",
                    "PARAMS": {
                        "formula": "revenue ~ enriched + price",
                    },
                },
            }
            config_path = tmp_path / f"{initiative_id}.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config, f)
            config_cache[initiative_id] = str(config_path)

        return InitiativeConfig(
            initiative_id=initiative_id,
            cost_to_scale=cost_to_scale,
            measure_config=config_cache[initiative_id],
        )

    def make_measure():
        return Measure(storage_url=storage_url)

    return make_initiative, make_measure, storage_url


@pytest.fixture()
def allocate_data_dir(tmp_path):
    """Create a disk-based data_dir with initiative subdirectories for allocate adapter tests.

    Returns (data_dir, costs, initiatives_on_disk) where initiatives_on_disk is
    the list of solver-format dicts that load_initiatives would return.
    """
    initiatives = [
        {"id": "A", "cost": 4, "R_best": 15, "R_med": 10, "R_worst": 2, "confidence": 0.9},
        {"id": "B", "cost": 3, "R_best": 12, "R_med": 8, "R_worst": 1, "confidence": 0.6},
        {"id": "C", "cost": 3, "R_best": 9, "R_med": 6, "R_worst": 2, "confidence": 0.8},
        {"id": "D", "cost": 2, "R_best": 7, "R_med": 5, "R_worst": 3, "confidence": 0.4},
        {"id": "E", "cost": 5, "R_best": 18, "R_med": 9, "R_worst": 0, "confidence": 0.5},
    ]
    costs = {i["id"]: i["cost"] for i in initiatives}
    data_dir = tmp_path / "allocate_data"

    for init in initiatives:
        subdir = data_dir / init["id"]
        subdir.mkdir(parents=True)

        # impact_results.json in experiment format (what _extract_estimates expects)
        impact_results = {
            "model_type": "experiment",
            "data": {
                "model_params": {"formula": "revenue ~ treatment + price"},
                "impact_estimates": {
                    "params": {"treatment": init["R_med"], "price": 0.5},
                    "conf_int": {
                        "treatment": [init["R_worst"], init["R_best"]],
                        "price": [-0.1, 1.1],
                    },
                    "pvalues": {"treatment": 0.01, "price": 0.05},
                },
                "model_summary": {"nobs": 100},
            },
        }
        (subdir / "impact_results.json").write_text(json.dumps(impact_results, indent=2), encoding="utf-8")

        # evaluate_result.json (what load_initiatives reads for confidence)
        evaluate_result = {
            "initiative_id": init["id"],
            "confidence": init["confidence"],
            "confidence_range": [0.0, 1.0],
            "strategy": "score",
            "report": "test",
        }
        (subdir / "evaluate_result.json").write_text(json.dumps(evaluate_result, indent=2), encoding="utf-8")

    return str(data_dir), costs, initiatives
