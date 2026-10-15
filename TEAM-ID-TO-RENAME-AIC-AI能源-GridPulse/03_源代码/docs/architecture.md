# Architecture

## Purpose

GridPulse is organized as a reproducible evidence pipeline rather than a monolithic dashboard. Each stage writes explicit artifacts that the following stage consumes or references.

```text
OPSD source
  -> ingest.py / build_dataset.py
  -> quality.py / quality_report.py / eda_report.py
  -> features.py / baseline.py / models.py / multihorizon.py
  -> rolling_backtest.py / train_models.py
  -> alerts.py / run_alerts.py
  -> scenarios.py / run_storage_scenario.py
  -> app.py / report / defense deck / final_preflight.py
```

## Components

| Area | Main files | Responsibility | Output boundary |
|---|---|---|---|
| Ingestion | `src/ingest.py`, `scripts/build_dataset.py` | Download, normalize, and derive net load | Standardized snapshot included; raw source downloaded separately |
| Quality and EDA | `src/quality.py`, `scripts/quality_report.py`, `scripts/eda_report.py` | Validate timestamps, values, formula, and distributions | Recreated metrics and figures |
| Baseline | `src/baseline.py`, `scripts/run_baseline.py` | Timestamp-aligned 24-hour seasonal-naive comparator | Evaluation baseline only |
| Features and models | `src/features.py`, `src/models.py`, `src/multihorizon.py`, `scripts/train_models.py`, `scripts/train_multihorizon.py` | Causal one-step and direct 1--6 hour features, chronological training, intervals | No direct 24-hour claim |
| Robustness | `scripts/rolling_backtest.py` | Fixed expanding-window temporal check | Not model selection on final test |
| Risk review | `src/alerts.py`, `scripts/run_alerts.py` | Validation-calibrated candidate risks and review queue | Not fault diagnosis |
| Storage scenario | `src/scenarios.py`, `scripts/run_storage_scenario.py` | Fixed-reserve baseline and uncertainty-aware rolling linear planning | Not dispatch authorization |
| Balanced episodes and temporal validation | `src/balanced_storage.py`, `src/independent_validation.py`, `scripts/run_independent_validation.py` | Daily energy restoration, frozen later-year evaluation | Frozen files cannot be changed while retaining original evidence |
| Optimality audit | `src/optimality.py`, `scripts/certify_optimality.py` | Exact rational and LP primal-dual finite-instance certificates | Offline full-information bounds; not an online controller |
| Controller development | `src/efficient_storage.py`, `scripts/run_controller_development.py` | Two-stage online planning with explicit peak tolerance and throughput minimization | Post-hoc development; known years are not new independent validation |
| Presentation | `app.py`, `docs/`, `outputs/` | Human-readable review, demo, report, and defense materials | Does not change scientific results |

## Information-Availability Rule

Every observed target, solar, and wind feature is shifted before model use. For a prediction at time `t`, the model uses measurements available no later than `t - 1 hour`. Calendar features are known at issuance time. This prevents target leakage in the stated one-step task.

## Artifact Ownership

- Source code and documentation are version-controlled.
- Standardized data, frozen model binaries, figures, metrics and experiment trajectories are included in the delivered snapshot; raw downloads and caches are excluded.
- The report preview and defense deck are tracked review deliverables; their numeric claims must be regenerated and reconciled before a formal submission.
- Local verification receipts, temporary files, test caches and dependency directories are excluded from the submission.

## Verification Path

1. Run the scripts in [reproducibility.md](reproducibility.md).
2. Run `python -m pytest -q`.
3. Run `python scripts/final_preflight.py`.
4. Compare regenerated metrics against tracked report and defense materials.

The automated checks establish internal consistency. Data licenses, operational validity, public claims, and anonymous-submission rules require human review.
