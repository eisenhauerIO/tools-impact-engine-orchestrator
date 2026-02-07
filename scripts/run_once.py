"""Run the Impact Engine Orchestrator once with mock components.

Usage:
    python scripts/run_once.py --config config.yaml
"""

import argparse

import yaml

from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.evaluate.mock import MockEvaluate
from impact_engine_orchestrator.components.measure.mock import MockMeasure
from impact_engine_orchestrator.config import InitiativeConfig, PipelineConfig
from impact_engine_orchestrator.orchestrator import Orchestrator


def load_config(path: str) -> PipelineConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return PipelineConfig(
        budget=raw["budget"],
        scale_sample_size=raw.get("scale_sample_size", 5000),
        max_workers=4,
        initiatives=[InitiativeConfig(**i) for i in raw["initiatives"]],
    )


def print_reports(result):
    print("\n" + "=" * 70)
    print("OUTCOME REPORTS")
    print("=" * 70)

    for report in result["outcome_reports"]:
        print(f"\n{report['initiative_id']}")
        print("-" * 40)
        print(f"  Predicted: {report['predicted_return']:.2%}")
        print(f"  Actual:    {report['actual_return']:.2%}")
        print(f"  Error:     {report['prediction_error']:+.2%}")
        print(f"  Confidence: {report['confidence_score']:.2f} ({report['model_type']})")
        print(f"  Budget:    ${report['budget_allocated']:,.0f}")
        print(f"  Samples:   {report['sample_size_pilot']} → {report['sample_size_scale']}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Initiatives evaluated: {len(result['pilot_results'])}")
    print(f"  Initiatives selected:  {len(result['outcome_reports'])}")
    if not result["outcome_reports"]:
        print("  No initiatives selected for scaling.")
        return
    total_budget = sum(r["budget_allocated"] for r in result["outcome_reports"])
    print(f"  Total budget used:     ${total_budget:,.0f}")
    avg_error = sum(abs(r["prediction_error"]) for r in result["outcome_reports"]) / len(result["outcome_reports"])
    print(f"  Avg prediction error:  {avg_error:.2%}")


def main():
    parser = argparse.ArgumentParser(description="Run Impact Engine Orchestrator once")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)

    orchestrator = Orchestrator(
        measure=MockMeasure(),
        evaluate=MockEvaluate(),
        allocate=MockAllocate(),
        config=config,
    )

    result = orchestrator.run()
    print_reports(result)


if __name__ == "__main__":
    main()
