# GridPulse Innovation Brief

## Current product claim

GridPulse is not a generic load-forecasting dashboard. The implemented contribution is a renewable-aware, uncertainty-aware decision-support prototype that links a causal one-step-ahead net-load backtest to explainable operational-risk signals and cautious rule-based actions. A direct 24-hour forecast is future work and requires issuance-time forecast inputs.

## Research hypotheses

### H1: Renewable-aware net load is the correct target

Subtracting solar and wind generation from total load should make the target more useful for peak-risk screening than forecasting demand alone. This must be tested with an ablation that removes renewable terms or renewable-derived features.

### H2: Uncertainty contains operational information

A forecast interval or calibrated prediction set should identify high-risk periods more usefully than a point forecast residual alone. We will report interval coverage, interval width, and risk-event precision/recall where event labels are available only in stress tests.

### H3: Joint risk rules are more actionable than one residual threshold

Combining forecast deviation, net-load percentile, and renewable ramp rate should produce more interpretable event categories than a single residual threshold. The threshold policy must be fitted on validation data and frozen before final testing.

### H4: A simple dispatch policy can be evaluated without claiming real savings

A constrained, rule-based storage or peak-shaving simulation can show whether warnings arrive early enough to support an action. Results will be labeled theoretical scenario results, with assumptions and no claim of real deployment or realized savings.

## Candidate technical contributions

The following are candidates, not yet proven contributions:

1. An implemented leakage-controlled one-step-ahead net-load forecasting pipeline built from real public data; a direct 24-hour multi-step pipeline remains future work.
2. Validation-calibrated prediction intervals or conformalized residual bounds.
3. A risk taxonomy that separates peak stress, renewable ramp-down, and sustained deviation, with an evidence trace for each alert.
4. A dispatch-suggestion layer that maps risk evidence to auditable actions and constraints.
5. Stress-test protocols that measure early warning, false alarms, missed events, and robustness by event severity.

## Experiment gates

We will not describe a candidate as an innovation until the following evidence exists:

- The data source and license are recorded.
- A seasonal-naive baseline is implemented.
- Train, validation, and final test periods are chronological and frozen.
- The candidate improves a predeclared metric or adds a measurable operational benefit without unacceptable tradeoffs.
- At least one ablation explains which component caused the improvement.
- No result uses final-test data for threshold or model selection.

## First implementation milestone

Day 1 is limited to source selection, ingestion, schema normalization, quality checks, a data dictionary, and exploratory figures for load, solar, wind, and net load. Model choice and innovation claims remain provisional until this evidence is available.
