# Day 1 Data Evidence

## Scope

The first data slice uses Germany-level hourly OPSD observations from 2015-01-01 through 2020-09-30. The standardized table has 50,400 valid timestamp rows and five fields: timestamp, total load, solar generation, wind generation, and derived net load. One all-empty source placeholder row before the first valid observation is removed explicitly during normalization.

## Reproducible outputs

- Raw source: `data/raw/opsd_time_series_60min_singleindex.csv`
- Standard table: `data/processed/net_load_hourly.csv`
- Quality report: `outputs/metrics/data-quality-report.json`
- EDA figures: `outputs/figures/01_*.png` through `06_*.png`

## Initial evidence from the executed quality check

- Coverage is 2,100 days at a 60-minute inferred frequency.
- There are no duplicate timestamps and no missing timestamp intervals in the standardized table.
- Load has 1 missing value; solar has 104; wind has 75; derived net load has 106 missing rows because it requires all three inputs.
- No negative values were observed in the four numeric fields in this release slice.
- The maximum absolute error in the stored net-load formula is 0 MW.

## Modeling implications

The data supports a historical net-load forecasting prototype, but the missing renewable/load observations must be handled explicitly before training. The implemented model is a one-step-ahead causal backtest; a direct 24-hour forecast requires inputs known at issuance time. A first model protocol should either restrict training/evaluation to complete rows or use a documented, leakage-safe imputation policy. Threshold calibration and all feature decisions must be completed on validation data only.

These are data-quality findings, not claims about forecast performance or real operational benefit.
