# AI Workflow

This project was built with Codex as the implementation agent. The workflow used AI for code generation, data validation, and documentation, but the outputs were checked against actual dataset findings and build/test results.

## How AI Was Used

- Generated the audit script in `scripts/data_audit.py`.
- Generated the cleaning script in `scripts/clean_data.py`.
- Built the React + Vite dashboard, including pages, charts, state handling, and CSV parsing.
- Used the cleaned dataset and validation outputs to write project documentation.

## Example Prompts Used

- `Analyze data/bookings_jan_may_2026.csv. Create scripts/data_audit.py and docs/DATA_AUDIT.md.`
- `Using docs/DATA_AUDIT.md, create scripts/clean_data.py. Generate data/cleaned_bookings.csv and docs/CLEANING_SUMMARY.md.`
- `Build a production-ready React + Vite dashboard using data/cleaned_bookings.csv.`
- `Create and populate docs/DECISIONS.md, docs/AI-WORKFLOW.md, docs/TEST-REPORT.md, README.md.`

## AI Mistake Detected And Corrected

One implementation mistake was the initial Health Score breakdown chart. It was first rendered as a stacked bar chart, which incorrectly implied that the four component scores should sum to the total. That is not how the score works because the components are weighted, normalized inputs, not additive parts.

Correction:

- changed the chart to grouped bars so each component remains visible on its own 0-100 scale
- kept the leaderboard and numeric score as the primary ranking surface

## Validation Steps Used To Catch Issues

- compared generated outputs against `docs/DATA_AUDIT.md`
- ran the cleaning script and checked the removed-row log and revenue-correction log
- verified the cleaned CSV had 226 rows
- checked the cleaned dataset for:
  - duplicate booking IDs
  - invalid ISO dates
  - zero or negative nights
  - revenue formula mismatches
- ran `npm.cmd run build` to confirm the dashboard compiled successfully

## Notes On AI Limits

- AI produced the first-pass implementation quickly, but the audit-driven counts and cleaning rules were verified against the actual dataset.
- Browser-based visual QA was attempted, but the in-app browser backend was unavailable in this session, so the final verification relied on build output and data checks.
- The dashboard and data-cleaning logic are deterministic, but the Health Score is relative to the current dataset and will change as the dataset changes.
