# GridPulse

> Renewable-aware net-load forecasting, uncertainty-aware risk review, and risk-aware theoretical storage planning.

GridPulse is a reproducible energy decision-support prototype built with public German power-system data. It connects data quality checks, causal net-load forecasts, empirical prediction intervals, candidate operational-risk screening, and a constrained theoretical storage-planning comparison.

**This is a historical backtest prototype, not a deployed dispatch system, fault-diagnosis system, or direct 24-hour forecasting product.**

## Why GridPulse

When wind and solar output changes, system operators care about the residual demand that other resources must cover:

```text
net load = total load - solar generation - wind generation
```

GridPulse turns this quantity into an auditable workflow:

```text
Public data -> quality checks -> causal features -> forecast + interval
            -> candidate risks + review queue -> risk-aware storage planning
```

## Competition Positioning

This repository is prepared for the **Technology Innovation Group** track. The primary
application direction is **new-energy consumption and grid-connection intelligent
control**: renewable-aware net-load forecasting provides an early signal, uncertainty
and risk rules produce an auditable human-review queue, and a constrained storage
scenario illustrates a possible peak-shaving response. The prototype is designed to
show a complete, reproducible engineering path with public data; it does not claim
real-time dispatch, confirmed fault diagnosis, realized savings, or deployed-grid
performance.

The requirement-to-evidence matrix is in
[docs/competition-alignment.md](docs/competition-alignment.md). It records which
competition requirements are implemented, which are manual submission tasks, and
which require data or authorization that are not present in a public historical
dataset.

## Current Evidence

Figures below come from repository scripts. Original results use the OPSD Germany release; the separately frozen 2021 temporal holdout uses Energy-Charts.info.

| Evidence | Current result | Boundary |
|---|---:|---|
| Normalized hourly records | 50,400 | 2015-2020 public historical data |
| Duplicate / missing timestamps | 0 / 0 | Data-quality checks, not source certification |
| Selected-model frozen-test MAE | 1,019.87 MW | One-step-ahead causal backtest |
| Strong persistence baseline MAE | 2,382.60 MW | Same 10,035 timestamps; selected model improves MAE by 57.20% |
| Rolling backtest | 5/5 folds beat seasonal naive | Five fixed 30-day expanding windows |
| Rolling-model MAE mean | 837.30 MW | Same region and data release only |
| Empirical test interval coverage | 86.92% | Validation-calibrated symmetric interval |
| Candidate-risk rows | 972 | Screening signals, not confirmed faults |
| Human-review queue | 1,135 | Includes 163 interval-only peak watches |
| Original continuous direct-forecast policies: full-period peak reduction | 0 MW | Both original fixed and dynamic reserve leave the single highest point unchanged |
| Risk-aware 30 GWh P95 vs. same-information fixed reserve | -99.66 MW | Direct 1--6h forecast and rolling-optimizer ablation; only the reserve rule differs |
| Risk-aware 30 GWh equivalent full cycles | 0.89 vs. 0.84 | Dynamic reserve improves P95 with slightly higher theoretical throughput; not battery-lifetime evidence |
| Original daily balanced dynamic vs. fixed P95 | -15.09 MW | 417 complete UTC days; same daily start/end 50% SOC and hard 15% minimum |
| Original daily balanced dynamic vs. fixed throughput | -59,996.65 MWh | Recovery charge and losses included; original dynamic leaves the maximum peak unchanged, fixed lowers it |
| New dynamic peak-response maximum reduction | 645.85 MW | Matched daily exploratory test: 69,256.00 to 68,610.15 MW; highest point shifts to another day |
| New dynamic peak-response P95 / throughput vs. old dynamic | -170.10 MW / +300,172.74 MWh | Losses also increase; new fixed achieves the same maximum and lower P95 with higher throughput |
| Frozen 2021 temporal holdout maximum reduction | 1,250.00 MW | 365 complete days; 70,449.90 to 69,199.90 MW; no holdout retraining or recalibration |
| 2021 mean daily peak reduction | 237.39 MW [184.73, 293.93] | Paired 7-day block, 2,000 resamples; conditional on observed days |
| 2021 P95 / throughput vs. old dynamic | +72.97 MW / +592,789.18 MWh | P95 advantage did not replicate; Q3 maximum worsened 230.18 MW |
| 2021 finite-instance peak optimum | 69,199.90 MW; controller gap 0 MW | Power lower bound attained; fixed physical model and maximum-only objective |
| Offline lexicographic minimum throughput at that peak | 5,380.88 MWh | Exact rational lower-bound/attainment certificate; full future information, no online savings claim |
| Old exploratory-test controller optimality gap | 604.15 MW | Offline optimum 68,006 MW; existing controller is not globally peak-optimal on this instance |

Read [the optimality proof and scope](docs/global-optimality.md). New offline schedules have exact rational certificates for peak and then minimum throughput, supported by independently verified LP primal-dual witnesses. The frozen controller and holdout evaluation are unchanged. This proves finite physical optimization instances, not universal online-policy or all-metric optimality.

Read [the controller-development audit](docs/controller-development.md) for two-stage peak/throughput comparisons, 68 operating stress traces, renewable/ramp diagnostics and causal rolling interval checks. All candidates failed the validation-period peak admission rule, so the primary controller remains unchanged. These known-year analyses report failures alongside improvements. A fresh isolated Windows/Python installation passed tests and existing-artifact verification.

## What Is Implemented

The browser dashboard now opens on a project overview with 2021/2022 year selection,
six storage policies, annual peak/P95/throughput/loss metrics, interactive daily
net-load and SOC charts, and CSV export. The existing six analysis tabs remain
available. Overview selections are independent of the sidebar's original test-period
date filter. Launch with `python -m streamlit run app.py` and open
`http://localhost:8501`. Chinese plots detect common Windows, macOS and Linux fonts;
set `GRIDPULSE_FONT_PATH` to a Chinese font file if needed.

The separately locked [2022 replication](docs/later-year-validation.md) evaluates all six unchanged policies on 365 shared days. Relative to the original dynamic policy, the new dynamic policy reduces the maximum by 1,250 MW and mean daily peak by 165.83 MW (95% block interval [106.43,227.73]). Annual P95 is 145.49 MW lower, but its interval covers zero and each quarter's P95 worsens. Throughput increases by 300,478.17 MWh; one-hour frozen interval coverage falls to 82.03%. These failures and costs remain visible in the dashboard and report. [Release review](docs/release-review.md) records error handling and strict audit repairs.

- Public OPSD data acquisition, normalization, data dictionary, quality checks, and EDA.
- Leakage-controlled, one-step-ahead causal features with fixed chronological splits.
- Seasonal-naive baseline, Random Forest, and Histogram Gradient Boosting comparison.
- Fixed rolling robustness backtest and validation-calibrated empirical prediction intervals.
- Candidate peak-load, solar-drop, and sustained-deviation rules with evidence traces.
- Separate candidate-risk export and uncertainty-aware human-review queue.
- Direct 1--6 hour causal forecasts and validation-calibrated intervals for storage planning.
- Same-information fixed-30%-reserve baseline versus uncertainty-aware, dynamic-SOC-reserve rolling linear optimization.
- Validation-hour-calibrated exploratory reserve-component ablations and power sensitivity, with terminal SOC and reserve-target shortfalls reported.
- Matched daily energy-restoration comparisons, hard operating SOC floor, explicit losses, recovery charging and hourly conservation audit.
- Separate peak-response mechanism ablations: point-forecast peak planning and validation-triggered advisory reserve release, with fixed and dynamic controls and validation/test traces.
- Offline peak/throughput optimization, exact rational attainment proofs, and independent certificate verification without rerunning a solver.
- Streamlit dashboard, technical report, defense deck/PDF, and automated preflight checks.

## Submission Materials

- Technical report source and final PDF: `docs/technical-report-draft.md` and `outputs/report/gridpulse-technical-report-v0.1.pdf`.
- Editable defense deck and submission PDF: `outputs/presentation/gridpulse-defense-v9.pptx` and `outputs/presentation/gridpulse-defense-v9.pdf`.
- Demonstration runbook for the required short video: `docs/demo-script.md`.
- Competition requirement and acceptance matrix: `docs/competition-alignment.md`.
- Final local verification: `python scripts/final_preflight.py`.
- Build the anonymous submission folder: `python scripts/build_submission_package.py --team-id <official-team-id>`.
- Create its validated ZIP archive: `python scripts/archive_submission_package.py --package submission/<official-team-id>-AIC-AI能源-GridPulse`.

## Repository Map

```text
app.py                 Streamlit demo application
src/                   Core ingestion, quality, features, models, alerts, scenarios
scripts/               Reproducible pipeline and validation commands
tests/                 Unit tests for causal features, baseline, and storage bounds
docs/                  Methods, evidence notes, architecture, report, and demo materials
outputs/presentation/  Editable defense deck tracked for review
outputs/report/        Generated technical-report PDF tracked for review
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
python scripts/train_multihorizon.py
python scripts/run_storage_scenario.py
python scripts/strengthen_evidence.py
python scripts/run_balanced_storage.py
python scripts/run_peak_response.py
python scripts/competition_figures.py
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

The preflight validates tests, expected evidence artifacts, prediction-interval metadata, the same-information storage ablation, and the PowerPoint validation receipt. It does not replace human review of competition requirements, anonymous submission, or public-data terms.

## Scientific and Operational Boundaries

- The forecast is **one step ahead** and only uses information available no later than the previous hour.
- The risk-aware scenario uses direct **1--6 hour** models; a direct 24-hour forecast still needs issuance-time weather or renewable-generation forecasts.
- Prediction intervals are empirical bands calibrated on validation residuals; they are not probabilistic guarantees.
- Alerts are candidate operating signals, not confirmed equipment faults or certified safety warnings.
- The solar-drop rule uses historical observed solar output in backtest; deployment requires real-time measurements or forecast inputs.
- The storage module is a theoretical scenario. It omits network constraints, prices, degradation, reserve obligations, and dispatch authorization.
- The risk-aware optimizer compares peak/P95/throughput tradeoffs under stated constraints. It does not establish actual battery life, operational safety, or savings.
- The original uncertainty term saturates to a constant. Supplemental component experiments use validation-hour-calibrated intervals and remain exploratory because the original test results were already known. Reserve targets are soft. Original continuous experiments leave terminal SOC unconstrained; the separate daily balanced experiment enforces restoration and a hard 15% floor. Balanced mode also caps SOC at 50% and allows charging at any hour, so changes across modes are not an isolated terminal-constraint effect.
- No result should be interpreted as realized savings, carbon reduction, reliability improvement, or deployment performance.
- The frozen 2021 holdout adds later-year historical evidence for extreme and mean daily peak reduction, with worse annual P95 and higher losses. It is the same country with a different provider, not prospective deployment. Interval-start measurement timestamps are accounted for, but extra publication latency and historical data vintages remain unverified.

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
- [Risk-aware storage planning](docs/risk-aware-control.md)
- [Extreme-peak response and mechanism ablations](docs/peak-response.md)
- [Frozen 2021 temporal holdout validation](docs/independent-validation.md)
- [Originality and provenance review](docs/originality-and-provenance.md)
- [Technical report](docs/technical-report-draft.md)

## Contributing and Security

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and run the local checks before opening a pull request. For security or safety concerns, see [SECURITY.md](SECURITY.md).

## License

The original GridPulse source code is available under the [MIT License](LICENSE). This license does not apply to third-party data, third-party repositories, or their respective terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Forecast-to-dispatch exploratory comparison

Run `python scripts/compare_forecast_dispatch.py` to compare AI, persistence and previous-day forecasts with the same dynamic-reserve controller, common complete UTC days and method-specific calibration using the same validation rules. Results and physically audited trajectories are saved separately under `outputs/experiments/forecast_dispatch/` and displayed in the frontend overview. This uses the already inspected original test period; it is not a new independent holdout or a basis for selecting policies.

In the delivered experiment, AI reduces maximum load by 1191.86 MW and P95 by 243.06 MW versus persistence, while increasing throughput and conversion loss. Versus previous-day forecasts, maximum load is similar and P95/throughput improve, but mean daily peak is higher. These tradeoffs do not establish overall superiority, realized savings or deployment performance. Frozen 2021/2022 evidence is unchanged.
