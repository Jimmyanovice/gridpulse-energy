# Rolling Backtest

The repository now includes a fixed expanding-window robustness check in `scripts/rolling_backtest.py`.

- Five fold starts are declared in source code: January and July 2018, January and July 2019, and January 2020.
- Each fold trains on all eligible observations before the fold start and evaluates the next 30 calendar days.
- The selected Histogram Gradient Boosting configuration is compared with the 24-hour seasonal-naive baseline.
- No fold is selected because of its score, and no fold result changes the frozen Day 3 test metric.

The output is `outputs/models/rolling_backtest_metrics.json`. It reports fold-level MAE/RMSE/MAPE/sMAPE, mean and standard deviation across folds, and the number of folds where the model beats the baseline.

The current run beats the seasonal-naive baseline in all five folds. The model MAE mean is 837.30 MW with a 174.41 MW sample standard deviation; this supports temporal robustness within the same public release, not geographic generalization.
