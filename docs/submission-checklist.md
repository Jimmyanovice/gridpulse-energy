# Submission Checklist

The acceptance basis for this checklist is the participant-provided competition
brief in [competition-alignment.md](competition-alignment.md). The matrix separates
repository evidence from manual submission work and external inputs that cannot be
proven by the OPSD historical dataset.

## Track and scope

- [x] Primary track selected: Technology Innovation Group.
- [x] Primary direction selected: new-energy consumption and grid-connection intelligent control.
- [x] Application scenario, method, evidence, limitations, and expected-benefit boundary are stated.
- [x] No claim of confirmed faults, real dispatch, realized savings, or deployed performance.

## Technical report

- [x] Repository-grounded technical report draft exists at `docs/technical-report-draft.md`.
- [x] PDF preview exported to `outputs/report/gridpulse-technical-report-v0.1.pdf`.
- [x] PDF preview exists; verify size against the official submission limit before upload.
- [ ] Report follows the final official Technology Innovation Group outline (the screenshot is not the full attachment).
- [ ] Every metric, figure, and table can be regenerated from a repository command.
- [ ] Citation includes OPSD DOI and required attribution.
- [ ] No unverified savings, carbon reduction, user, deployment, or fault claims appear.
- [ ] One-step causal backtest and theoretical storage scenario boundaries are visible.
- [ ] No school name, logo, instructor name, email, or personally identifying information appears.

## Defense PPT

- [x] Editable PPT exists at `outputs/presentation/gridpulse-defense-v1.pptx`.
- [ ] Export or retain the format required by the final official notice.
- [ ] Verify the PDF has no school, instructor, or team-identifying content.
- [ ] Confirm every chart metric matches `outputs/models/day3_model_metrics.json` or `outputs/scenarios/storage_scenario_metrics.json`.
- [ ] Rehearse using the duration and Q&A rules in the final official notice.

## Video

- [ ] Record the Streamlit workflow using `docs/demo-script.md`.
- [ ] Keep duration between 3 and 5 minutes.
- [ ] Export MP4 below 300 MB.
- [ ] Show the local application, risk evidence, limitations, and reproducibility path.
- [ ] Do not show local account names, school identifiers, browser tabs, or unrelated files.

## Other materials link

- [x] Include source code, reproducibility instructions, report source, deck, and data-acquisition instructions.
- [ ] Use the official team-number naming convention in the shared folder.
- [ ] Set the Baidu Netdisk link to permanent access with an automatically generated extraction code.
- [ ] Open the link in a logged-out or separate browser session before submission.

## Final preflight

- [ ] Rerun the full pipeline in `docs/reproducibility.md`.
- [ ] Compare regenerated JSON metrics with the report and PPT.
- [ ] Read the current official competition page and attachments once more for deadline or format changes.
