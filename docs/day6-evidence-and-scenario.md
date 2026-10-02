# Day 6 Evidence Refinement and Storage Scenario

## Fixed experimental boundary

All ablations reuse the Day 2 frozen test start: `2019-08-09 21:00 UTC`. No test result was used to select a threshold or tune a hyperparameter.

## Feature ablations on the frozen test period

| Variant | Test MAE (MW) | Change vs. full model |
|---|---:|---:|
| Full histogram gradient boosting | 1,019.87 | Reference |
| Without renewable lags | 1,120.04 | +100.17 |
| Without rolling statistics | 1,035.03 | +15.16 |
| Calendar only | 9,160.43 | +8,140.56 |

The comparison supports three cautious observations for this single dataset and time period: recent net-load history carries most predictive information; renewable lags add measurable value; rolling statistics add a smaller, positive contribution. These are not causal or universal claims.

## Theoretical storage peak-shaving simulation

The simulation uses the Day 3 one-step prediction to trigger a simple, deterministic storage policy. It does not represent a real dispatch system.

### State and policy

- State: hourly battery state of charge (SOC).
- Initial SOC: 50% of nominal capacity.
- Charge/discharge efficiency: 92% in each direction.
- Maximum discharge: 2,500 MW; maximum charge: 1,250 MW.
- A capacity/24-hour effective discharge limit is used as a conservative daily energy-spreading proxy.
- Discharge trigger: forecast net load at or above the validation-calibrated peak threshold of 55,406.34 MW.
- Thirty percent of capacity is held as a reserve during ordinary peak alerts and released for a validation-calibrated extreme forecast.
- Charge trigger: forecast net load at or below the validation-period 25th percentile (29,466.50 MW).
- Capacity sensitivity: 10,000, 20,000, and 30,000 MWh.

### Executed sensitivity results

| Capacity | Discharge hours | Controlled test P95 (MW) | Baseline test P95 (MW) | Full-period maximum reduction (MW) |
|---|---:|---:|---:|---:|
| 10,000 MWh | 297 | 54,186.8 | 54,213.1 | 416.7 |
| 20,000 MWh | 300 | 54,185.0 | 54,213.1 | 833.3 |
| 30,000 MWh | 304 | 54,185.0 | 54,213.1 | 1,250.0 |

The reserve-aware policy reduces both P95 and the single largest actual test-period net-load value under the stated assumptions. The capacity/24-hour limit is a deliberately conservative proxy, not a dispatch optimization; results still depend on forecast timing and SOC availability.

## Interpretation boundary

These are theoretical scenario outputs only. They do not demonstrate actual cost saving, carbon reduction, grid reliability improvement, deployed storage control, or feasible market operation. The simulation omits network limits, storage degradation, price signals, reserve obligations, forecast availability beyond one step, and operator approval.

## Outputs

- Storage simulator: `src/scenarios.py`
- Runner: `scripts/run_storage_scenario.py`
- Sensitivity metrics: `outputs/scenarios/storage_scenario_metrics.json`
- Hourly state traces: `outputs/scenarios/storage_*mwh_timeseries.csv`
