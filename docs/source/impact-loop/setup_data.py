"""Generate simulated product catalogs for each initiative.

This is a setup step that runs BEFORE the orchestrator.
Each initiative gets a products.csv that serves as its input data.

Usage:
    hatch run python docs/source/impact-loop/setup_data.py
    hatch run python docs/source/impact-loop/setup_data.py --config path/to/config.yaml
"""

import argparse
from pathlib import Path

import yaml
from online_retail_simulator.simulate import simulate_products

from impact_engine_orchestrator.config import load_config

SIMULATOR_CONFIGS_DIR = Path(__file__).parent / "configs" / "simulator"


def _get_products_path(measure_config_path: str) -> str:
    """Read the products output path from a measure config."""
    with open(measure_config_path) as f:
        measure_config = yaml.safe_load(f)
    return measure_config["DATA"]["SOURCE"]["CONFIG"]["path"]


def main():
    default_config = Path(__file__).parent / "config.yaml"
    parser = argparse.ArgumentParser(description="Generate initiative input data")
    parser.add_argument("--config", type=str, default=str(default_config))
    args = parser.parse_args()

    config = load_config(args.config)

    for initiative in config.initiatives:
        iid = initiative.initiative_id
        sim_config = SIMULATOR_CONFIGS_DIR / f"{iid}.yaml"

        if not sim_config.exists():
            print(f"  SKIP {iid} — no simulator config at {sim_config}")
            continue

        print(f"  Generating data for {iid} ...")
        job_info = simulate_products(str(sim_config))
        products = job_info.load_df("products")

        # Write products.csv to the path the measure config expects
        output_path = Path(_get_products_path(initiative.measure_config))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        products.to_csv(output_path, index=False)

        print(f"  OK   {iid} — {len(products)} products → {output_path}")

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
