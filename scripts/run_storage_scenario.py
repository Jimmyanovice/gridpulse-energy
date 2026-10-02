from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.scenarios import simulate_storage_dispatch
from src.alerts import predict_periods


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    predictions = pd.read_csv(root / "outputs/models/hist_gradient_boosting_test_predictions.csv", parse_dates=["timestamp"])
    predictions = predictions.rename(columns={"hist_gradient_boosting_prediction_mw": "predicted_net_load_mw"})
    thresholds = json.loads((root / "outputs/alerts/alert_evaluation.json").read_text(encoding="utf-8"))["thresholds"]
    validation, _ = predict_periods(
        root / "data/processed/net_load_hourly.csv", root / "outputs/models/hist_gradient_boosting.joblib"
    )
    charge_threshold = float(validation["predicted_net_load_mw"].quantile(0.25))
    emergency_threshold = float(validation["predicted_net_load_mw"].quantile(0.99))
    output_dir = root / "outputs/scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for capacity_mwh in [10000.0, 20000.0, 30000.0]:
        result, metrics = simulate_storage_dispatch(
            predictions,
            peak_threshold_mw=float(thresholds["peak_prediction_threshold_mw"]),
            capacity_mwh=capacity_mwh,
            charge_threshold_mw=charge_threshold,
            emergency_threshold_mw=emergency_threshold,
            reserve_fraction=0.30,
            energy_smoothing_hours=24.0,
        )
        label = f"storage_{int(capacity_mwh)}mwh"
        summaries[label] = metrics
        result.to_csv(output_dir / f"{label}_timeseries.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
    report = {
        "scenario_type": "Deterministic theoretical storage peak-shaving simulation, not deployment evidence or savings claim.",
        "time_resolution": "1 hour",
        "decision_information": "Uses the existing one-step-ahead net-load prediction as the peak trigger.",
        "assumptions": [
            "Initial state of charge is 50% of nominal capacity.",
            "Maximum discharge power is 2,500 MW; maximum charge power is 1,250 MW.",
            "A capacity/24-hour effective discharge limit is used as a conservative daily energy-spreading proxy.",
            "Charge and discharge efficiency are each assumed to be 92%.",
            "Storage discharges only when the forecast crosses the validation-calibrated peak threshold.",
            "Thirty percent of capacity is reserved during ordinary peak alerts and released only for a validation-calibrated extreme forecast.",
            "Storage charges only below the validation-period 25th percentile of forecast net load.",
            "No network constraints, battery degradation, market prices, reserve obligations, or real dispatch authorization are modeled.",
        ],
        "calibration": {
            "charge_forecast_threshold_mw": charge_threshold,
            "emergency_forecast_threshold_mw": emergency_threshold,
            "reserve_fraction": 0.30,
            "calibration_period": "2019-01-12 20:00 UTC to 2019-08-09 20:00 UTC",
        },
        "sensitivity": summaries,
    }
    (output_dir / "storage_scenario_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
