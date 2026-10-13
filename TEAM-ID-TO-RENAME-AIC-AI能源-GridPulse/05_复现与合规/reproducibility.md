# Reproducibility Guide

## Environment

Use Python 3.11 or newer. Install dependencies from the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Full pipeline

The supplied submission is a frozen evidence snapshot. To check it without modifying any results, run `python scripts/audit_development.py`, `python scripts/audit_later_year.py` and `python scripts/final_preflight.py`. Run training pipelines only in a separate copy: they overwrite model/calibration artifacts and may invalidate frozen hashes. The original pipeline below builds the base project; delivered extensions listed later must also exist before final preflight or dashboard launch.

Run the following commands from the repository root, in order:

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
python scripts/export_report_pdf.py
python scripts/check_app.py
python scripts/anonymous_preflight.py
python scripts/final_preflight.py
```

The defense deck build requires the local presentation runtime documented in `scripts/ppt/README.md`; the checked PPTX/PDF is included in the submission package. It is not needed to reproduce the data and model results. After the final checks pass, assemble the anonymous package with `python scripts/build_submission_package.py --team-id <official-team-id>`.

Launch the dashboard separately with `python -m streamlit run app.py`; it runs until stopped. The packaged source includes all runtime artifacts, so launching the supplied package does not require retraining. Run `python scripts/archive_submission_package.py --package submission/<official-team-id>-AIC-AI能源-GridPulse` to create a ZIP and test the application after extraction.

Chinese plot labels require Microsoft YaHei, SimHei, Noto Sans CJK SC or WenQuanYi Zen Hei. PDF font discovery accepts `GRIDPULSE_FONT_PATH` and `GRIDPULSE_BOLD_FONT_PATH` when system fonts are unavailable.

`build_dataset.py` downloads OPSD data only when the expected raw file is absent. To redownload it, use `python scripts/build_dataset.py --force-download`.

## Expected artifacts

| Stage | Artifact |
|---|---|
| Data evidence | `outputs/metrics/data-quality-report.json`, `outputs/figures/*.png` |
| Baseline | `outputs/metrics/seasonal_naive_metrics.json`, `outputs/predictions/seasonal_naive_test.csv` |
| Models | `outputs/models/day3_model_metrics.json`, `outputs/models/multihorizon_metrics.json`, test predictions, feature importance, saved models |
| Alerts | `outputs/alerts/alert_evaluation.json`, `outputs/alerts/test_candidate_risks.csv` |
| Scenario | `outputs/scenarios/storage_scenario_metrics.json`, fixed-rule and risk-aware hourly SOC traces |
| Supplemental evidence | `outputs/models/reference_baseline_metrics.json`, `outputs/scenarios/reserve_ablation_metrics.json` |
| Daily energy accounting | `outputs/scenarios/daily_energy_balance_metrics.json`, `daily_*_timeseries.csv` (four matched variants) |
| Peak-response diagnosis | `outputs/scenarios/peak_response_metrics.json`, `peak_validation_*` and `peak_test_*` hourly traces |
| Frozen temporal validation | `outputs/validation/independent_2021_*`, `data/processed/independent_de_2021_hourly.csv` |
| Post-hoc optimality audit | `outputs/optimality/certificates.json`, two `*_oracle.csv` traces; see `docs/global-optimality.md` |
| Final preflight | `.codex-finalizer/gridpulse-final-preflight.json` |
| Anonymous material scan | `python scripts/anonymous_preflight.py` -> `.codex-finalizer/gridpulse-anonymous-preflight.json` |

## Reproduction boundaries

- The OPSD source URL, DOI, field mapping, and attribution requirements are recorded in `THIRD_PARTY_NOTICES.md`.
- The model uses fixed chronological validation and test start points. Do not alter them to improve reported test metrics.
- Prediction intervals use only validation residuals and are carried unchanged into test reporting; they are empirical calibration bands, not deployment guarantees.
- Supplemental reserve experiments were added after reviewing original test outcomes. They calibrate hourly radii and the uncertainty scale on validation data only, but do not constitute an untouched confirmatory test. Original and supplemental results are kept separate.
- Daily energy experiments compare the same 417 complete UTC days. Every episode starts at 50% SOC with a common hard 15% minimum. Balanced mode restores 50% SOC, caps SOC at 50%, and allows recovery charging at any hour. All charge load and losses count. Open daily resets are an experimental control, not sustainable operation. Cross-mode changes cannot be attributed solely to the terminal equality. Advisory reserve targets remain soft; this is exploratory, single-region evidence.
- Peak-response experiments separately ablate the planning objective (upper band vs. point forecast) and advisory-reserve release at a window point forecast reaching the direct one-hour validation q99 threshold. Intervals still determine dynamic reserves and discharge gates. Both fixed and dynamic policies retain the same physical and daily energy constraints. Validation diagnostics reuse validation calibration, and the design follows inspection of the old test peak, so neither result is independent confirmation. No test-threshold search is used.
- Generated data and outputs are intentionally ignored by Git. Rerun the pipeline to regenerate them.
- Before public submission, verify current dataset terms and include the required source attribution.
- The repository contains an independent `references/` checkout for comparison only. `pytest.ini` restricts test collection to this project's `tests/` directory so duplicate test module names in that checkout cannot contaminate the result.
## 2021 temporal holdout validation

This extension retains the original models and all original calibration values. It evaluates a later, previously unused calendar year from Energy-Charts.info. Read `docs/independent-validation.md` before running.

```powershell
python scripts/run_independent_validation.py freeze
python scripts/run_independent_validation.py download
python scripts/run_independent_validation.py evaluate
python scripts/summarize_independent_validation.py
```

Run `freeze` only once before the first full-data download. Delivered packages already include the frozen protocol and can start at `download` or directly `evaluate` using the attached standardized snapshot. Frozen hashes are checked before downloading/evaluating. Revised API snapshots may differ from the original raw SHA-256. No holdout retraining or threshold fitting is permitted under this protocol. The data source attributes Energy-Charts.info under CC BY 4.0. Source interval-start timestamps become UTC hourly means; issuance occurs at the end of the latest observed hour. Additional publication latency is not modeled.

## 2022 locked replication

The additional year keeps the original six policies; development candidates and rolling intervals are excluded from selection. See `docs/later-year-validation.md` for the protocol, all quarter failures and costs. Delivered packages contain the hourly snapshot, predictions and six traces. Verify them with `python scripts/audit_later_year.py`. Only a genuinely new checkout without any 2022 artifacts may run `python scripts/validate_later_year.py freeze`; then run `download` and `evaluate`. Do not recreate a protocol after looking at its observations.

## Post-hoc offline certificate commands

```powershell
python scripts/certify_optimality.py
python scripts/certify_optimality.py --verify-only
```

This separate extension leaves all frozen inputs unchanged. The first command computes full-information offline optima, lexicographic minimum throughput, primal-dual witnesses and exact rational certificates. The second reconstructs and checks saved witnesses without calling a solver. A zero finite-instance maximum gap is not evidence of optimal future online operation or optimal P95. Both old and new load sequences are already known at this stage; new controller tuning needs a new frozen validation period.

## Controller development and engineering checks

The ordered development workflow, all outcomes and limitations are in [controller-development.md](controller-development.md). Run `run_controller_development.py`, then `run_operating_stress.py`, then `audit_energy_and_intervals.py`. Existing delivered traces can be checked directly with `python scripts/audit_development.py`. All new artifacts are under `outputs/development/`; none replaces frozen results. The validation-only admission rule rejected all candidates, so the primary frozen controller remains unchanged.

Fresh Windows installation was checked in an isolated Python 3.13.5 environment. See `outputs/development/clean_environment_verification.json` and the complete dependency snapshot. This verifies installation, tests and existing artifacts, not a complete redownload and model retraining. The Streamlit app reports missing required artifacts explicitly. OPSD download uses atomic validated replacement; the frozen Energy-Charts runner is retained byte-for-byte.
