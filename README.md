# GridPulse

> Renewable-aware net-load forecasting, uncertainty-aware risk review, and theoretical storage peak-shaving scenarios.

GridPulse is a reproducible energy decision-support prototype built with public German power-system data. It connects data quality checks, causal one-step-ahead net-load forecasting, empirical prediction intervals, candidate operational-risk screening, and a constrained theoretical storage scenario.

**This is a historical backtest prototype, not a deployed dispatch system, fault-diagnosis system, or direct 24-hour forecasting product.**

## Why GridPulse

When wind and solar output changes, system operators care about the residual demand that other resources must cover:

```text
net load = total load - solar generation - wind generation
```

GridPulse turns this quantity into an auditable workflow:

```text
Public data -> quality checks -> causal features -> forecast + interval
            -> candidate risks + review queue -> theoretical storage scenario
```

## Current Evidence

All figures below are generated from the scripts in this repository and scoped to the selected OPSD Germany historical release.

| Evidence | Current result | Boundary |
|---|---:|---|
| Normalized hourly records | 50,400 | 2015-2020 public historical data |
| Duplicate / missing timestamps | 0 / 0 | Data-quality checks, not source certification |
| Selected-model frozen-test MAE | 1,019.87 MW | One-step-ahead causal backtest |
| Rolling backtest | 5/5 folds beat seasonal naive | Five fixed 30-day expanding windows |
| Rolling-model MAE mean | 837.30 MW | Same region and data release only |
| Empirical test interval coverage | 86.92% | Validation-calibrated symmetric interval |
| Candidate-risk rows | 1,023 | Screening signals, not confirmed faults |
| Human-review queue | 1,184 | Includes 161 interval-only peak watches |
| Theoretical 30 GWh peak reduction | 1,250 MW | Assumption-driven scenario, not deployment evidence |

## What Is Implemented

- Public OPSD data acquisition, normalization, data dictionary, quality checks, and EDA.
- Leakage-controlled, one-step-ahead causal features with fixed chronological splits.
- Seasonal-naive baseline, Random Forest, and Histogram Gradient Boosting comparison.
- Fixed rolling robustness backtest and validation-calibrated empirical prediction intervals.
- Candidate peak-load, solar-drop, and sustained-deviation rules with evidence traces.
- Separate candidate-risk export and uncertainty-aware human-review queue.
- Theoretical SOC-constrained storage sensitivity simulation with explicit assumptions.
- Streamlit dashboard, technical-report draft, defense deck, and automated preflight checks.

## Repository Map

```text
app.py                 Streamlit demo application
src/                   Core ingestion, quality, features, models, alerts, scenarios
scripts/               Reproducible pipeline and validation commands
tests/                 Unit tests for causal features, baseline, and storage bounds
docs/                  Methods, evidence notes, architecture, report, and demo materials
outputs/presentation/  Editable defense deck tracked for review
outputs/report/        Generated technical-report preview tracked for review
data/                  Local download and processed-data locations (not committed)
```

Read [the architecture guide](docs/architecture.md) for component ownership and data flow. Read [the reproducibility guide](docs/reproducibility.md) before regenerating results.

## Quick Start

### 1. Install

Python 3.11+ is required.

```powershell
python -m pip install -r requirements.txt
```

### 2. Run the full evidence pipeline

```powershell
python scripts/build_dataset.py
python scripts/quality_report.py
python scripts/eda_report.py
python scripts/run_baseline.py
python scripts/train_models.py
python scripts/rolling_backtest.py
python scripts/run_alerts.py
python scripts/run_storage_scenario.py
python scripts/final_preflight.py
```

### 3. Launch the dashboard

```powershell
python -m streamlit run app.py
```

### 4. Verify the repository state

```powershell
python -m pytest -q
python scripts/final_preflight.py
```

The preflight validates tests, expected evidence artifacts, prediction-interval metadata, storage sensitivity, and the PowerPoint validation receipt. It does not replace human review of competition requirements, anonymous submission, or public-data terms.

## Scientific and Operational Boundaries

- The forecast is **one step ahead** and only uses information available no later than the previous hour.
- A direct 24-hour forecast needs issuance-time weather or renewable-generation forecasts and is future work.
- Prediction intervals are empirical bands calibrated on validation residuals; they are not probabilistic guarantees.
- Alerts are candidate operating signals, not confirmed equipment faults or certified safety warnings.
- The solar-drop rule uses historical observed solar output in backtest; deployment requires real-time measurements or forecast inputs.
- The storage module is a theoretical scenario. It omits network constraints, prices, degradation, reserve obligations, and dispatch authorization.
- No result should be interpreted as realized savings, carbon reduction, reliability improvement, or deployment performance.

## Data and Third-Party Material

The pipeline downloads the Open Power System Data (OPSD) Time Series release rather than committing it to this repository. The source URL, DOI, field mapping, attribution, and third-party boundaries are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Generated raw/processed data, model binaries, derived figures, and large experiment outputs are excluded from Git. They can be recreated using the documented pipeline. The tracked report and deck are review materials, not a substitute for rerunning the evidence chain.

## Documentation

- [Architecture and data flow](docs/architecture.md)
- [Data source decision](docs/data-source-decision.md)
- [Data dictionary](docs/data-dictionary.md)
- [Reproducibility guide](docs/reproducibility.md)
- [Model evidence](docs/day3-model-results.md)
- [Rolling-backtest protocol](docs/rolling-backtest.md)
- [Risk-screening evidence](docs/day4-risk-alerts.md)
- [Storage-scenario evidence](docs/day6-evidence-and-scenario.md)
- [Technical-report draft](docs/technical-report-draft.md)

## Contributing and Security

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and run the local checks before opening a pull request. For security or safety concerns, see [SECURITY.md](SECURITY.md).

## Citation

If this repository supports academic or engineering work, cite the repository metadata in [CITATION.cff](CITATION.cff) and the OPSD dataset as described in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

The original GridPulse source code is available under the [MIT License](LICENSE). This license does not apply to third-party data, third-party repositories, or their respective terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
