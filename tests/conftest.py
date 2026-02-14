"""Shared fixtures for integration tests with real Measure."""

import pandas as pd
import pytest
import yaml

from impact_engine_orchestrator.components.measure.measure import Measure
from impact_engine_orchestrator.config import InitiativeConfig


@pytest.fixture()
def measure_env(tmp_path):
    """Provide helpers to create real Measure instances backed by evaluate_impact.

    Returns (make_initiative, make_measure) where:
    - make_initiative(id, cost) creates an InitiativeConfig with a working measure config
    - make_measure() creates a Measure adapter wired to the temp storage
    """
    products_df = pd.DataFrame(
        {
            "product_id": [f"prod_{i:03d}" for i in range(5)],
            "name": [f"Product {i}" for i in range(5)],
            "category": ["Electronics"] * 5,
            "price": [99.99, 149.99, 79.99, 59.99, 199.99],
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
                            "start_date": "2024-01-01",
                            "end_date": "2024-01-31",
                        },
                    },
                    "TRANSFORM": {
                        "FUNCTION": "aggregate_by_date",
                        "PARAMS": {"metric": "revenue"},
                    },
                },
                "MEASUREMENT": {
                    "MODEL": "interrupted_time_series",
                    "PARAMS": {
                        "dependent_variable": "revenue",
                        "intervention_date": "2024-01-15",
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

    return make_initiative, make_measure
