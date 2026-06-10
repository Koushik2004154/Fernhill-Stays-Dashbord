# Fernhill Stays Dashboard

Production-ready React + Vite dashboard for analyzing booking performance from the cleaned January-May 2026 bookings dataset.

## What It Shows

- Overview KPI cards
- Revenue and booking trends
- Property performance rankings
- Channel contribution and cancellation analysis
- Health Score leaderboard and score breakdown

## Data Pipeline

1. `data/bookings_jan_may_2026.csv` was audited in `scripts/data_audit.py`.
2. `scripts/clean_data.py` produced `data/cleaned_bookings.csv`.
3. The dashboard reads the cleaned CSV directly and calculates metrics in the frontend.

## Data Audit Results

- Original records: 238
- Cleaned records: 226
- Duplicate records removed: 8
- Revenue corrections: 11
- Rows removed: 12

## Dashboard Rules

- Realized revenue excludes `Cancelled` and `No-show` bookings.
- ISO dates are used throughout the dashboard.
- Property, channel, and status labels are standardized before analysis.
- Health Score is normalized to a 0-100 scale.

## Health Score

Health Score combines four normalized components:

- 40% Revenue Performance
- 25% Occupancy Demand
- 20% Booking Reliability
- 15% Channel Diversity

The current cleaned dataset ranks `Marigold Suites` highest and `Birchwood Stay` lowest.

## Assumptions And Limits

- The dataset covers January through May 2026.
- Duplicate booking IDs are resolved by keeping the first occurrence.
- `Unknown` is used for missing booking channels when the source field cannot be inferred safely.
- Health Score is relative to the current dataset and will shift as the dataset changes.
- The dashboard has no backend; it reads the cleaned CSV directly at build/runtime.

## Tech Stack

- React 19
- Vite 7
- Tailwind CSS
- Recharts

## Setup

```powershell
npm.cmd install
npm.cmd run dev
```

Open the local app at `http://127.0.0.1:5173`.

## Build

```powershell
npm.cmd run build
```

## Verification

- Data validation passed on the cleaned CSV.
- Revenue formula checks passed.
- Health Score validation passed for all 5 properties.
- Production build passed successfully.

- Architecture

  CSV / Database
      ↓
Backend API (Python/FastAPI or Node.js)
      ↓
Calculate Metrics
      ↓
Return JSON
      ↓
React Frontend
      ↓
Display Results

## Key Files

- [scripts/data_audit.py](scripts/data_audit.py)
- [scripts/clean_data.py](scripts/clean_data.py)
- [docs/DATA_AUDIT.md](docs/DATA_AUDIT.md)
- [docs/CLEANING_SUMMARY.md](docs/CLEANING_SUMMARY.md)
- [docs/DECISIONS.md](docs/DECISIONS.md)
- [docs/AI-WORKFLOW.md](docs/AI-WORKFLOW.md)
- [docs/TEST-REPORT.md](docs/TEST-REPORT.md)
