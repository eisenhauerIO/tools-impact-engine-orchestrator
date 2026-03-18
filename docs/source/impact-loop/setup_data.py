"""Generate simulated product catalogs for each initiative.

This is a setup step that runs BEFORE the orchestrator.
Each initiative gets a products.csv that serves as its input data.

Usage:
    hatch run python docs/source/impact-loop/setup_data.py
    hatch run python docs/source/impact-loop/run_once.py --config path/to/config.yaml
"""

import argparse
from pathlib import Path

import yaml
from online_retail_simulator.simulate.products_rule_based import simulate_products_rule_based

from impact_engine_orchestrator.config import load_config

NUM_PRODUCTS = 100


def main():
    default_config = Path(__file__).parent / "config.yaml"
    parser = argparse.ArgumentParser(description="Generate initiative input data")
    parser.add_argument("--config", type=str, default=str(default_config))
    args = parser.parse_args()

    config = load_config(args.config)

    for initiative in config["initiatives"]:
        iid = initiative["initiative_id"]

        with open(initiative["measure_config"]) as f:
            measure_config = yaml.safe_load(f)

        source_config = measure_config["DATA"]["SOURCE"]["CONFIG"]
        seed = source_config["seed"]
        output_path = Path(source_config["path"])

        print(f"  Generating data for {iid} ...")
        products = simulate_products_rule_based(
            {"RULE": {"PRODUCTS": {"PARAMS": {"num_products": NUM_PRODUCTS, "seed": seed}}}}
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        products.to_csv(output_path, index=False)

        print(f"  OK   {iid} — {len(products)} products → {output_path}")

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
