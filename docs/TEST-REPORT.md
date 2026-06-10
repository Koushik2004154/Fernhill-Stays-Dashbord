# Test Report

This report records the verification performed on the cleaned bookings pipeline and dashboard.

## Data Validation Tests

Result: pass

Checks performed:

- cleaned row count is 226
- duplicate booking IDs in `data/cleaned_bookings.csv` are zero
- check-in dates are all ISO formatted as `YYYY-MM-DD`
- impossible stays with `nights <= 0` are removed

Observed output:

- original records: 238
- cleaned records: 226
- duplicate records removed: 8
- rows removed: 12

## Revenue Validation

Result: pass

Checks performed:

- realized revenue excludes `Cancelled` and `No-show` bookings
- `total_amount_inr = nightly_rate_inr * nights` for cleaned rows
- no negative or formula-mismatched revenue records remain

Observed output:

- revenue corrections applied: 11
- realized revenue in cleaned data: `2,356,571`

## Health Score Validation

Result: pass

Checks performed:

- health scores were calculated for all 5 properties in the cleaned dataset
- scores were normalized to a 0-100 scale
- leaderboard order is stable and sorted descending
- the score formula uses the documented weights:
  - 40% Revenue Performance
  - 25% Occupancy Demand
  - 20% Booking Reliability
  - 15% Channel Diversity

Observed output:

- score count: 5
- highest score: `Marigold Suites` at `92.95`
- lowest score: `Birchwood Stay` at `46.24`

## Empty State Tests

Result: implemented and code-path verified

Checks performed:

- `src/components/EmptyState.jsx` renders when the bookings array is empty
- the empty state message tells the user to generate `data/cleaned_bookings.csv`

Limitation:

- no browser runtime was available for a visual screenshot test in this session

## Error State Tests

Result: implemented and code-path verified

Checks performed:

- `src/components/ErrorState.jsx` renders when CSV parsing or validation fails
- error content is shown in a dedicated state instead of a broken dashboard

Limitation:

- no browser runtime was available for a visual screenshot test in this session

## Build Verification

Result: pass

Commands run:

```powershell
npm.cmd install
npm.cmd run build
```

Observed output:

- Vite production build completed successfully
- build artifacts were generated in `dist/`
- final build completed without warnings after manual chunking was added

## Additional Checks

- `scripts/data_audit.py` completed successfully after the source CSV was provided
- `scripts/clean_data.py` completed successfully and generated:
  - `data/cleaned_bookings.csv`
  - `docs/CLEANING_SUMMARY.md`
- the local Vite dev server responded with HTTP 200 at `http://127.0.0.1:5173`
