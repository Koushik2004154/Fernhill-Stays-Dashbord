# Decisions

This project has three linked layers: audit, cleaning, and dashboarding. The decisions below reflect the actual findings in the source CSV and the implemented code in `scripts/clean_data.py` and `src/lib/metrics.js`.

## Data Audit Results

- Original records: 238
- Cleaned records: 226
- Duplicate records removed: 8
- Revenue corrections: 11
- Rows removed: 12

The audit also found inconsistent property names, booking channels, booking statuses, missing values, mixed date formats, revenue anomalies, and impossible stays. Those issues drove the cleaning rules below.

## Cleaning Rules

### Standardize property names

Chosen because the same property appeared under casing and spacing variants such as `Marigold Suites`, `MARIGOLD SUITES`, and `Marigold Suites `. Without normalization, property-level revenue and booking counts split across duplicate labels.

Business effect: preserves a single reporting dimension per real property.

### Standardize booking channels

Chosen because channels such as `Direct`, `direct`, `OTA-MMT`, and `ota-mmt` were inconsistent. Channel reporting is used for acquisition mix, commissions, and source performance, so label drift would distort those views.

Business effect: keeps source attribution consistent.

### Standardize booking statuses

Chosen because statuses appeared as `Checked-out`, `CHECKED OUT`, `Confirmed`, `confirmed`, and similar variants. Status is a control field for realized revenue, cancellation rate, and booking reliability.

Business effect: makes lifecycle reporting comparable across rows.

### Remove duplicate booking IDs

Chosen because the audit found 16 duplicate booking IDs. The cleaner keeps the first occurrence and removes later duplicates so the dataset stays one-row-per-booking.

Business effect: avoids double counting revenue, occupancy, and booking volume.

### Handle missing values safely

Chosen because missing booking channels, nightly rates, and total amounts were present, but the rows were still useful. The script does not drop them by default:

- `booking_channel` is set to `Unknown` when it cannot be inferred.
- `nightly_rate_inr` is derived from `total_amount_inr / nights` when that is deterministic.
- `total_amount_inr` is derived from `nightly_rate_inr * nights` when that is deterministic.

Business effect: preserves valid bookings while documenting uncertainty.

### Convert dates to ISO format

Chosen because the source mixed formats like `2026-03-09`, `9 Mar 2026`, `02/02/2026`, and `03-20-2026`. ISO format is required for safe sorting, joins, monthly grouping, and downstream automation.

Business effect: removes ambiguity and makes trend reporting reliable.

### Detect and fix revenue anomalies

Chosen because the audit found values that were clearly inconsistent with the booking formula, including negative totals and totals that were 10x the expected amount.

Implemented rule:

- `total_amount_inr = nightly_rate_inr * nights`
- if `total_amount_inr` was negative or off by formula, it was corrected to the formula result

Business effect: restores auditable booking revenue.

### Remove impossible stays

Chosen because 4 rows had `nights = 0`, which cannot represent a real stay. The cleaner removes these rows instead of guessing a stay length.

Business effect: prevents invalid occupancy and revenue-per-night metrics.

## Realized Revenue Rule

Cancelled and No-show bookings are excluded from realized revenue.

Reason:

- They do not represent completed stays.
- Including them would inflate revenue, average booking value, and property/channel performance.
- The dashboard separates realized revenue from raw booking volume so operational and financial reporting stay comparable.

Applied in:

- `src/lib/metrics.js`
- Overview, Property Performance, Channel Analysis, and Health Score pages

## Health Score Methodology

Health Score is computed per property with this weighting:

- 40% Revenue Performance
- 25% Occupancy Demand
- 20% Booking Reliability
- 15% Channel Diversity

Normalization:

- Revenue Performance is normalized to 0-100 against the top property revenue in the cleaned dataset.
- Occupancy Demand is normalized to 0-100 against the top property nights in the cleaned dataset.
- Booking Reliability is already a 0-100 rate based on non-cancelled, non-no-show bookings.
- Channel Diversity uses normalized entropy over realized bookings.

Observed results in the cleaned data:

- Best health score: `Marigold Suites` at `92.95`
- Lowest health score: `Birchwood Stay` at `46.24`

## Assumptions

- The source file covers January through May 2026 only.
- The first occurrence of a duplicate booking ID is the canonical record.
- Ambiguous dates are parsed to stay within the reporting period when possible.
- When date ambiguity remained, day-first parsing was preferred because the business context is India.
- Missing booking channels are not inferable from other columns, so they are marked `Unknown`.
- Revenue correction is safe when the nightly rate and nights are present and consistent.

## Limitations

- Some fields still reflect the source record’s original commercial classification, such as `room_type`.
- `Unknown` booking channels preserve records but reduce attribution precision.
- A row can be valid for reporting but still contain uncertainty in individual fields.
- Health Score is relative to this dataset, so scores will shift if new properties or a different date range are added.
- The dashboard is calculated from the cleaned CSV at build/runtime; no backend persistence layer is present.
