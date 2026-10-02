from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    checks: list[dict[str, object]] = []

    test = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    checks.append(
        {
            "name": "pytest",
            "passed": test.returncode == 0,
            "detail": (test.stdout + test.stderr).strip().splitlines()[-1:] or ["no output"],
        }
    )

    required = [
        "data/processed/net_load_hourly.csv",
        "outputs/metrics/data-quality-report.json",
        "outputs/models/day3_model_metrics.json",
        "outputs/models/rolling_backtest_metrics.json",
        "outputs/alerts/alert_evaluation.json",
        "outputs/scenarios/storage_scenario_metrics.json",
        "outputs/presentation/gridpulse-defense-v1.pptx",
        ".codex-finalizer/gridpulse-defense-v1.validation.json",
    ]
    for relative in required:
        checks.append({"name": f"artifact:{relative}", "passed": (ROOT / relative).is_file()})

    model = read_json("outputs/models/day3_model_metrics.json")
    scenario = read_json("outputs/scenarios/storage_scenario_metrics.json")
    receipt = read_json(".codex-finalizer/gridpulse-defense-v1.validation.json")
    model_mae = model["models"]["hist_gradient_boosting"]["test"]["mae_mw"]
    checks.append(
        {
            "name": "model-metric-boundary",
            "passed": model.get("forecast_design") == "one_step_ahead_causal",
            "detail": model.get("forecast_design"),
        }
    )
    interval = model["models"]["hist_gradient_boosting"].get("prediction_interval", {})
    checks.append(
        {
            "name": "prediction-interval-calibration",
            "passed": 0 < interval.get("radius_mw", 0) and 0 <= interval.get("test", {}).get("coverage_pct", -1) <= 100,
            "detail": {
                "radius_mw": interval.get("radius_mw"),
                "test_coverage_pct": interval.get("test", {}).get("coverage_pct"),
            },
        }
    )
    checks.append(
        {
            "name": "storage-sensitivity",
            "passed": all(
                scenario["sensitivity"][key]["theoretical_max_reduction_mw"] >= 0
                for key in ("storage_10000mwh", "storage_20000mwh", "storage_30000mwh")
            ),
            "detail": {
                key: scenario["sensitivity"][key]["theoretical_max_reduction_mw"]
                for key in ("storage_10000mwh", "storage_20000mwh", "storage_30000mwh")
            },
        }
    )
    checks.append(
        {
            "name": "ppt-validation",
            "passed": receipt.get("packageIntegrity", {}).get("status") == "pass"
            and receipt.get("firstPartyImport", {}).get("passed") is True,
            "detail": {
                "package": receipt.get("packageIntegrity", {}).get("status"),
                "node": receipt.get("firstPartyImport", {}).get("nodeExecutable"),
                "modules": receipt.get("firstPartyImport", {}).get("runtimeNodeModules"),
            },
        }
    )

    pending = {
        "technical_report_pdf": not any((ROOT / "outputs").rglob("*.pdf")),
        "defense_ppt_pdf": not (ROOT / "outputs/presentation/gridpulse-defense-v1.pdf").is_file(),
        "demo_video": not any((ROOT / "outputs").glob("*.mp4")),
        "official_submission_link": True,
        "anonymous_final_review": True,
    }
    report = {
        "schemaVersion": "gridpulse-final-preflight.v1",
        "passed": all(bool(item["passed"]) for item in checks),
        "core_metric": {"hist_gradient_boosting_test_mae_mw": model_mae},
        "checks": checks,
        "pending_external_or_manual_items": pending,
        "interpretation": "Core repository evidence is ready when passed=true; pending items require final competition packaging or human review.",
    }
    output = ROOT / ".codex-finalizer/gridpulse-final-preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
