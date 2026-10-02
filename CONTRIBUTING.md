# Contributing to GridPulse

## Scope

Contributions should preserve the project boundaries: historical backtest claims must remain distinct from deployment claims, candidate risks must not be described as faults, and theoretical storage results must not be described as savings or operational authorization.

## Development Setup

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

For changes that affect experiment outputs, run the relevant pipeline stage and then:

```powershell
python scripts/final_preflight.py
```

## Pull Request Expectations

1. Keep changes focused and document the problem being solved.
2. Add or update tests when shared behavior changes.
3. Do not commit `data/raw/`, `data/processed/`, model binaries, local caches, or credentials.
4. Record any new dataset, package, or reference material in `THIRD_PARTY_NOTICES.md`.
5. Explain information availability for any new prediction feature.
6. State whether a result was selected on validation data or only reported on frozen test data.
7. Update documentation and presentation numbers when an experiment result changes.

## Reporting Issues

Use the GitHub issue templates for reproducible bugs or enhancement proposals. Do not include personal data, credentials, or unpublished competition materials.
