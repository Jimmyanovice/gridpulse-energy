# Technical Report Outline

This is a writing structure, not a completed report. Populate it only with regenerated figures, metrics, and citations from this repository. Do not add unverified deployment, fault, saving, or user claims.

## Cover and abstract

- Title: GridPulse: Renewable-Aware Net-Load Forecasting and Candidate Operational-Risk Screening.
- Group: Technology Innovation Group.
- Abstract: state the Germany public-data scope, causal one-step evaluation, selected model, three candidate-risk rules, and theoretical storage scenario. Keep the one-step and theoretical-scenario boundaries visible.

## 1. Project background and significance

- Explain net-load variability under wind and solar generation.
- Define the target: `net_load = total_load - solar_generation - wind_generation`.
- Frame the problem as decision support for renewable integration and peak-risk screening.
- Cite OPSD and relevant energy forecasting literature. Add only sources that have been independently checked.

## 2. Technical solution and implementation

### 2.1 Architecture

Describe the path from OPSD download through normalization, quality checks, causal features, model, risk rules, scenario, and Streamlit prototype.

### 2.2 Data processing

Use `data-dictionary.md`, `data-source-decision.md`, and the Day 1 quality report. State UTC usage, source fields, missingness, and formula validation.

### 2.3 Forecasting method

Describe the seasonal-naive reference, Random Forest, and Histogram Gradient Boosting. Explain time split and the historical-only feature policy. State clearly that Day 3 reports one-step-ahead causal backtesting, not a direct 24-hour forecast.

### 2.4 Candidate-risk rules

Describe validation-calibrated peak, solar-drop, and sustained-deviation rules. Use “candidate operational risk,” never “confirmed fault.”

### 2.5 System functions

Show the five Streamlit views and explain the evidence trace stored for each risk event.

## 3. Experiments and analysis

- Environment and reproducibility commands from `reproducibility.md`.
- Baseline comparison: use regenerated results from Day 2 and Day 3 JSON outputs.
- Ablation: cite the three Day 6 variants and their MAE differences.
- Risk stress test: call it an injected deterministic mechanics test, not real detection accuracy.
- Storage scenario: list capacity, SOC, power and efficiency assumptions, then report P95 and maximum outcomes without claiming actual savings.

## 4. Innovation and application value

- Renewable-aware net-load target with explicit solar/wind feature ablation.
- Validation-calibrated, evidence-traceable risk taxonomy.
- A cautious decision-support interface that separates model evidence, candidate risks, and theoretical actions.

## 5. Limitations, ethics, and future work

- One Germany-wide historical data release and no verified fault labels.
- One-step causal backtest rather than direct 24-hour issuance.
- Solar-drop retrospective signal needs operational forecasts or real-time measurements in deployment.
- Storage policy omits market, network, degradation, and authorization constraints.
- Explain the risk of false alerts, potential unequal impacts of automatic recommendations, and need for human approval.

## References and appendix

- Cite OPSD with its DOI and original sources as required.
- Include dependencies and their versions.
- Appendix: data dictionary, quality report, model configuration, reproducibility commands, and output file index.
