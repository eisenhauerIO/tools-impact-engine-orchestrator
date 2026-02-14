"""Run the Impact Engine Orchestrator once.

Usage:
    hatch run python docs/source/impact-loop/run_once.py
    hatch run python docs/source/impact-loop/run_once.py --config path/to/config.yaml
"""

import argparse
from pathlib import Path

from impact_engine_orchestrator.config import load_config
from impact_engine_orchestrator.orchestrator import Orchestrator


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
        print(f"  Confidence: {report['confidence_score']:.2f} ({report['model_type'].value})")
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
    default_config = Path(__file__).parent / "config.yaml"
    parser = argparse.ArgumentParser(description="Run Impact Engine Orchestrator once")
    parser.add_argument("--config", type=str, default=str(default_config), help="Path to YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)
    orchestrator = Orchestrator.from_config(config)
    result = orchestrator.run()
    print_reports(result)


if __name__ == "__main__":
    main()
