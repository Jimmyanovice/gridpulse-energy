# Demonstration Script (About 4 Minutes)

## 0:00-0:25 Project framing

“GridPulse studies renewable-aware net load for a Germany-wide public-data prototype. It forecasts the next immediate time step from historical information, screens for candidate operational risks, and presents cautious rule-based suggestions. The current version is a historical backtest, not a deployed dispatch system.”

## 0:25-0:55 Data evidence

Open the Data Overview tab. Point to the hourly load, solar, wind, and net-load curves. Explain that the pipeline downloads and normalizes one OPSD release, checks timestamp coverage, duplicates, missingness, negative values, and the net-load formula.

## 0:55-1:35 Forecast evidence

Open Forecast Backtest. Select one week. Explain the seasonal-naive reference and the causal feature boundary. State that histogram gradient boosting reached 1,019.87 MW MAE on the frozen test period, while the seasonal-naive reference reached 8,760.67 MW. Do not call this a 24-hour result.

## 1:35-2:20 Risk evidence

Open Risk Events. Select a candidate event. Explain the three categories: peak load, solar drop, and sustained residual deviation. Point out the trigger evidence. State that the rule thresholds came only from validation data and that the events are screening signals, not confirmed faults.
Mention that the review queue also includes interval-only peak watches: cases where the point forecast is below the threshold but the calibrated upper bound reaches it.

## 2:20-2:55 Explainability and suggestions

Open Feature Explanation, then Dispatch Suggestions. Explain that recent net load is the strongest validation-period feature and that solar/wind lag ablation worsened test MAE by 100.17 MW. Read one suggested action and its operational constraint.

## 2:55-3:35 Scenario and limits

Show the storage scenario result in the report or deck. Explain the explicit SOC, power, efficiency, reserve, and capacity assumptions. State that the reserve-aware policy reduces P95 and the largest test peak in this theoretical backtest, but it does not support a savings or reliability claim.

## 3:35-4:00 Close

“The next research step is to replace the one-step backtest input with a real direct 24-hour information set and develop an SOC-aware risk-prioritization policy. Every result and figure can be regenerated from the included scripts.”
