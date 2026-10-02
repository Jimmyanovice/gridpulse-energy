# Reproducibility Guide

## Environment

Use Python 3.11 or newer. Install dependencies from the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Full pipeline

Run the following commands from the repository root, in order:

```powershell
python scripts/build_dataset.py
python scripts/quality_report.py
python scripts/eda_report.py
python scripts/run_baseline.py
python scripts/train_models.py
python scripts/rolling_backtest.py
python scripts/run_alerts.py
python scripts/run_storage_scenario.py
python -m streamlit run app.py
python scripts/final_preflight.py
python scripts/export_report_pdf.py
```

`build_dataset.py` downloads OPSD data only when the expected raw file is absent. To redownload it, use `python scripts/build_dataset.py --force-download`.

## Expected artifacts

| Stage | Artifact |
|---|---|
| Data evidence | `outputs/metrics/data-quality-report.json`, `outputs/figures/*.png` |
| Baseline | `outputs/metrics/seasonal_naive_metrics.json`, `outputs/predictions/seasonal_naive_test.csv` |
| Models | `outputs/models/day3_model_metrics.json`, test predictions, feature importance, saved models |
| Alerts | `outputs/alerts/alert_evaluation.json`, `outputs/alerts/test_candidate_risks.csv` |
| Scenario | `outputs/scenarios/storage_scenario_metrics.json`, hourly SOC traces |
| Final preflight | `.codex-finalizer/gridpulse-final-preflight.json` |

## Reproduction boundaries

- The OPSD source URL, DOI, field mapping, and attribution requirements are recorded in `THIRD_PARTY_NOTICES.md`.
- The model uses fixed chronological validation and test start points. Do not alter them to improve reported test metrics.
- Prediction intervals use only validation residuals and are carried unchanged into test reporting; they are empirical calibration bands, not deployment guarantees.
- Generated data and outputs are intentionally ignored by Git. Rerun the pipeline to regenerate them.
- Before public submission, verify current dataset terms and include the required source attribution.
- The repository contains an independent `references/` checkout for comparison only. `pytest.ini` restricts test collection to this project's `tests/` directory so duplicate test module names in that checkout cannot contaminate the result.
