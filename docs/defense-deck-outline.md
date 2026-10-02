# Defense Deck Outline

## Slide 1: GridPulse

Project title, Technology Innovation Group, and a one-line scope: renewable-aware net-load forecasting and candidate risk screening. Do not show school, instructor, or logo.

## Slide 2: Engineering problem

Explain why wind and solar fluctuations complicate net-load management. Define the net-load formula and intended decision-support role.

## Slide 3: Data and quality evidence

Show OPSD Germany fields, 2015-2020 hourly coverage, missingness controls, and the EDA time-series figure.

## Slide 4: Causal forecasting design

Show chronological split, seasonal-naive baseline, lag/rolling features, and the one-step-ahead information boundary.

## Slide 5: Forecasting results

Show MAE comparison and the actual-versus-predicted chart. State the frozen test period.

## Slide 6: Risk screening

Show the three rules, validation-only threshold calibration, and the evidence carried by each alert. State that candidate risks are not confirmed faults.

## Slide 7: Ablation evidence

Show full model versus renewable-free, rolling-free, and calendar-only variants. Link the renewable ablation to the project claim.

## Slide 8: Theoretical storage scenario

Show SOC-constrained rule, capacities, P95 outcomes, and the unreduced single maximum. State the limitation plainly.

## Slide 9: Prototype and next steps

Show the Streamlit MVP, the fixed rolling evidence (5/5 folds beating baseline; mean MAE 837.30 MW), the calibrated test coverage (86.92%), the reproducibility path, and the next research gate: direct 24-hour forecast inputs and SOC-aware peak prioritization.
