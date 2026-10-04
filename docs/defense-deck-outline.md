# Defense Deck Outline

## Slide 1: GridPulse

Project title, Technology Innovation Group, and a one-line scope: renewable-aware net-load forecasting and candidate risk screening. Do not show school, instructor, or logo.

## Slide 2: Engineering problem

Explain why wind and solar fluctuations complicate net-load management. Define the net-load formula and intended decision-support role.

## Slide 3: Data and quality evidence

Show OPSD Germany fields, 2015-2020 hourly coverage, missingness controls, and the EDA time-series figure.

## Slide 4: Causal forecasting design

Show the one-step evidence path, then the direct 1--6 hour planning models and their causal information boundary.

## Slide 5: Forecasting results

Show MAE comparison and the actual-versus-predicted chart. State the frozen test period.

## Slide 6: Risk screening

Show the three rules, validation-only threshold calibration, and the evidence carried by each alert. State that candidate risks are not confirmed faults.

## Slide 7: Ablation evidence

Show full model versus renewable-free, rolling-free, and calendar-only variants. Link the renewable ablation to the project claim.

## Slide 8: Risk-aware storage planning

Show the fixed-reserve baseline against dynamic SOC reserve rolling optimization. Compare P95 and equivalent full cycles, and state the extreme-peak versus risk-reserve tradeoff plainly.

## Slide 9: Prototype and next steps

Show the Streamlit MVP, the fixed rolling evidence (5/5 folds beating baseline; mean MAE 837.30 MW), the calibrated test coverage (86.92%), the reproducibility path, and the next research gate: direct 24-hour forecast inputs with prices, degradation, and network constraints.
