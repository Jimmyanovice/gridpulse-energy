# Day 6 Evidence Refinement and Risk-Aware Storage Planning

## Fixed experimental boundary

All forecast, interval, alert, and storage-policy evaluation uses the frozen Day 2 test start: `2019-08-09 21:00 UTC`. Thresholds, direct-horizon model configurations, interval radii, and policy weights are established without using final-test outcomes for tuning.

## Feature ablations on the frozen test period

| Variant | Test MAE (MW) | Change vs. full model |
|---|---:|---:|
| Full histogram gradient boosting | 1,019.87 | Reference |
| Without renewable lags | 1,120.04 | +100.17 |
| Without rolling statistics | 1,035.03 | +15.16 |
| Calendar only | 9,160.43 | +8,140.56 |

Recent net-load history carries most predictive information in this dataset; renewable lags add measurable value; rolling statistics add a smaller positive contribution. These are dataset-specific predictive observations, not universal causal claims.

## Direct 1--6 Hour Planning Forecasts

The risk-aware storage policy uses six direct models. For a target at `t+h`, the `h`-hour model uses observations no later than `t`; all six models retain validation-calibrated 90% empirical intervals. This creates a causally available intraday planning window without claiming a direct 24-hour forecast.

| Horizon | Test MAE (MW) | Test interval coverage (%) |
|---|---:|---:|
| 1 hour | 1,019.87 | 86.92 |
| 2 hours | 1,898.34 | 87.07 |
| 3 hours | 2,650.71 | 86.50 |
| 4 hours | 3,333.81 | 86.37 |
| 5 hours | 3,934.67 | 86.87 |
| 6 hours | 4,420.12 | 85.65 |

Longer horizons are less accurate because this public-data prototype has no forecast-time weather or renewable-production input. The policy therefore treats wider empirical intervals as a reason to retain more SOC instead of pretending that long-horizon point forecasts are equally certain.

## Fixed-Reserve Baseline and Risk-Aware Policy

The original fixed policy holds 30% SOC during ordinary peak alerts. The new policy solves a six-hour linear min-max problem every hour, using forecast upper bounds as the peak-stress input. Its dynamic reserve fraction starts at 15%, adds up to 20 percentage points for forecast severity and up to 15 points for interval width, and caps at 60%. It executes only the current first action before forecasts and reserve targets are recomputed.

Both policies use initial SOC of 50%, 92% charge/discharge efficiency, maximum discharge of 2,500 MW, maximum charge of 1,250 MW, and a capacity/24-hour conservative discharge limit. Neither represents a real dispatch system.

## Executed Frozen-Test Comparison

| Capacity | Fixed P95 (MW) | Risk-aware P95 (MW) | Difference (MW) | Fixed / risk-aware equivalent full cycles |
|---|---:|---:|---:|---:|
| 10,000 MWh | 54,186.8 | 54,188.3 | +1.5 | 12.59 / 0.84 |
| 20,000 MWh | 54,185.0 | 54,150.2 | -34.9 | 12.03 / 0.86 |
| 30,000 MWh | 54,185.0 | 54,077.7 | -107.3 | 11.65 / 0.89 |

The risk-aware policy solves optimally for 100% of evaluated planning windows. For 20/30 GWh capacities it lowers controlled P95 while using much less theoretical throughput and maintaining nonzero SOC. It does not chase the single largest actual test-period peak, so its full-period maximum reduction is zero while the fixed policy achieves 416.7, 833.3, and 1,250.0 MW respectively. This is an explicit risk-reserve versus extreme-peak tradeoff, not evidence that either policy dominates under all objectives.

## Interpretation Boundary

The outputs are theoretical historical scenarios only. They do not demonstrate actual cost saving, carbon reduction, battery lifetime, grid reliability improvement, feasible market operation, or deployed storage control. The simulation omits network limits, battery degradation, price signals, reserve obligations, weather forecasts, and operator approval.

## Outputs

- Direct forecast implementation: `src/multihorizon.py`
- Direct forecast runner: `scripts/train_multihorizon.py`
- Storage policies: `src/scenarios.py`
- Scenario runner: `scripts/run_storage_scenario.py`
- Detailed formulation: `docs/risk-aware-control.md`
- Metrics: `outputs/models/multihorizon_metrics.json`, `outputs/scenarios/storage_scenario_metrics.json`
