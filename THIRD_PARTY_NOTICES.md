# Third-Party Notices

This file records external material used by GridPulse. It is intentionally separate from the original project implementation.

## SmartBuild-AI

- Location: `references/SmartBuild-AI/`
- Source: https://github.com/Mahmoud-Faraj/SmartBuild-AI
- License: MIT, as provided in that repository's `LICENSE` file
- Intended use: engineering reference for modular organization, chronological evaluation, residual screening, tests, and cautious dashboard wording
- Not used as: GridPulse data, reported results, submission prose, UI copy, or copied implementation

## Competition materials

- Source: https://www.aicomp.cn/tracks/4726.html
- Relevant material: 2026 AIC AI+Energy algorithm theme, Technology Innovation Group rules and report outline
- Intended use: competition requirements and evaluation alignment

## Dataset records

### Open Power System Data - Time series

- Canonical URL: https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv
- Dataset DOI: https://doi.org/10.25832/time_series/2020-10-06
- Publisher citation: Open Power System Data. 2020. *Data Package Time series*. Version 2020-10-06.
- Access date: 2026-09-29
- Region and period used: Germany, 2015-01-01 through 2020-09-30, UTC-normalized
- Frequency and unit: hourly; load and generation fields in MW
- Fields used: `DE_load_actual_entsoe_transparency`, `DE_solar_generation_actual`, `DE_wind_generation_actual`
- Transformation: source field renaming, numeric coercion, timestamp sorting, removal of one all-empty placeholder row, and derived `net_load_mw`
- Terms note: retain the dataset's published attribution and verify the release's current data-use terms again before final public submission; the OPSD website states its website text is CC BY 4.0, while the underlying primary-data terms may vary by source.
