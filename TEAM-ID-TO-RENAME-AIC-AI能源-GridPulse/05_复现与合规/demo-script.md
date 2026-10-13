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

## 2:55-3:35 Risk-aware planning and limits

Open the Risk-Aware Control tab. Contrast the fixed 30% reserve baseline with the direct 1--6 hour forecast-interval policy. Explain that the new policy raises the SOC reserve when the upper forecast or interval width increases, re-plans each hour, and only executes the first action. State that all three capacity scenarios reduce P95 under the same-information comparison, while theoretical throughput rises slightly; neither policy reduces the single maximum peak. This is a stated tradeoff, not a savings, lifetime, or reliability claim.

Then show the separate daily energy-restoration table and SOC traces. Over 417 matched complete days with 50% start/end SOC and a shared hard 15% floor, dynamic P95 is 15.09 MW lower and throughput is 59,996.65 MWh lower than fixed. Fixed performs better on the highest peak. Explain that recovery charging and losses count, reserve targets remain soft, and daily mode also changes charging permission and the SOC cap. These exploratory results do not establish long-term deployment benefit.

Show the extreme-peak response table next. Point-forecast planning and validation-q99 advisory-reserve release lower the whole-test maximum by 645.85 MW, with unchanged hard floor and daily energy restoration. Explain the shifted maximum: the original peak hour drops by 1,250 MW, but the highest point moves to another day. Dynamic throughput and losses rise relative to the old policy. New fixed achieves the same maximum and lower P95, while new dynamic uses less throughput. The comparison follows inspection of prior test outcomes and remains exploratory.

## 3:35-4:00 Close

“The next research step is to extend the implemented 1--6 hour planning window to a direct 24-hour information set with forecast-time weather inputs, prices, degradation and network constraints. Every result and figure can be regenerated from the included scripts.”
## 新增独立时间留出演示

在“风险感知调控”页展示 2021 年冻结验证区块。说明协议先于下载锁定，模型和阈值保持原值，六组使用 365 天。展示最高点降低 1,250 MW，以及平均日最高点削减 237.39 MW 的配对区间。随后展示全年 P95 上升 72.97 MW、Q3 极值失败及更高吞吐，避免把局部改善介绍为全面优势。最后说明仍缺少在线数据版本、额外发布延迟和网络/价格/退化验证。
