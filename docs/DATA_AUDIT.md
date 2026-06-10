# Data Audit: Bookings Jan-May 2026

This report audits source data quality only. No records were cleaned or modified.

## Source

- File: `data/bookings_jan_may_2026.csv`
- Rows audited: 238
- Columns audited: 10
- Column names: `booking_id`, `property`, `check_in_date`, `nights`, `room_type`, `guests`, `booking_channel`, `nightly_rate_inr`, `total_amount_inr`, `status`

## Detected Columns

- Booking Id Col: `booking_id`
- Property Col: `property`
- Channel Col: `booking_channel`
- Status Col: `status`
- Checkin Col: `check_in_date`
- Checkout Col: `Not found`
- Nights Col: `nights`
- Revenue Cols: `nightly_rate_inr, total_amount_inr`
- Date Cols: `check_in_date`

## Summary

| Issue type | Count | Business impact |
| --- | ---: | --- |
| Duplicate booking IDs | 16 | Duplicate IDs can double count revenue, occupancy, cancellations, and guest volume. |
| Inconsistent property names | 168 | Variant property names split performance metrics across multiple labels and make property-level reporting unreliable. |
| Inconsistent booking channels | 123 | Channel variants distort source mix, commission analysis, and marketing attribution. |
| Inconsistent booking statuses | 151 | Status variants can misclassify active stays, cancellations, no-shows, and realized revenue. |
| Missing values | 41 | Missing values reduce trust in occupancy, guest, revenue, and segmentation reporting; they can also break downstream joins and filters. |
| Invalid or mixed date formats | 238 | Mixed or invalid dates can shift bookings into the wrong month, corrupt stay length, and break trend reporting. |
| Revenue anomalies | 38 | Revenue anomalies can materially overstate or understate sales, ADR, RevPAR, owner payouts, and tax or commission calculations. |
| Impossible stays | 4 | Impossible stays cause incorrect occupancy, availability, length-of-stay, and revenue-per-night metrics. |

## Detailed Findings

### Duplicate booking IDs

- Count: 16
- Business impact: Duplicate IDs can double count revenue, occupancy, cancellations, and guest volume.
- Examples:
- booking_id: BK1207; csv_lines: [14, 161]
- booking_id: BK1138; csv_lines: [16, 77]
- booking_id: BK1044; csv_lines: [48, 91]
- booking_id: BK1285; csv_lines: [111, 205]
- booking_id: BK1028; csv_lines: [114, 123]

### Inconsistent property names

- Count: 168
- Business impact: Variant property names split performance metrics across multiple labels and make property-level reporting unreliable.
- Examples:
- normalized_value: marigoldsuites; variants: {'Marigold Suites': 52, 'MARIGOLD SUITES': 26}
- normalized_value: cedarcourt; variants: {'cedar court': 20, 'Cedar Court': 14}
- normalized_value: palmgroveinn; variants: {'Palm grove inn': 32, 'Palm Grove Inn': 24}

### Inconsistent booking channels

- Count: 123
- Business impact: Channel variants distort source mix, commission analysis, and marketing attribution.
- Examples:
- normalized_value: direct; variants: {'direct': 32, 'Direct': 28}
- normalized_value: otammt; variants: {'OTA-MMT': 35, 'ota-mmt': 28}

### Inconsistent booking statuses

- Count: 151
- Business impact: Status variants can misclassify active stays, cancellations, no-shows, and realized revenue.
- Examples:
- normalized_value: checkedout; variants: {'Checked-out': 44, 'CHECKED OUT': 36}
- normalized_value: confirmed; variants: {'confirmed': 37, 'Confirmed': 34}

### Missing values

- Count: 41
- Business impact: Missing values reduce trust in occupancy, guest, revenue, and segmentation reporting; they can also break downstream joins and filters.
- Examples:
- column: booking_channel; missing_count: 29; csv_lines: [11, 26, 27, 48, 54]
- column: nightly_rate_inr; missing_count: 9; csv_lines: [21, 42, 99, 102, 112]
- column: total_amount_inr; missing_count: 3; csv_lines: [22, 170, 197]

### Invalid or mixed date formats

- Count: 238
- Business impact: Mixed or invalid dates can shift bookings into the wrong month, corrupt stay length, and break trend reporting.
- Examples:
- column: check_in_date; formats: {'%Y-%m-%d': 57, '%d %b %Y': 56, '%d/%m/%Y': 60, '%d-%m-%Y': 65}; invalid_examples: [{'csv_line': 23, 'value': '03-20-2026'}, {'csv_line': 25, 'value': '03-24-2026'}, {'csv_line': 42, 'value': '03-21-2026'}, {'csv_line': 45, 'value': '05-26-2026'}, {'csv_line': 48, 'value': '04-15-2026'}]

### Revenue anomalies

- Count: 38
- Business impact: Revenue anomalies can materially overstate or understate sales, ADR, RevPAR, owner payouts, and tax or commission calculations.
- Examples:
- column: total_amount_inr; invalid_numeric_examples: []; non_positive_examples: [{'csv_line': 68, 'value': '-28497'}, {'csv_line': 101, 'value': '-21265'}, {'csv_line': 118, 'value': '-9138'}, {'csv_line': 154, 'value': '-28590'}, {'csv_line': 198, 'value': '-24185'}]; outlier_examples: [{'csv_line': 7, 'value': '81750', 'bounds': '-18207.5 to 48836.5'}, {'csv_line': 19, 'value': '53277', 'bounds': '-18207.5 to 48836.5'}, {'csv_line': 34, 'value': '54460', 'bounds': '-18207.5 to 48836.5'}, {'csv_line': 53, 'value': '50890', 'bounds': '-18207.5 to 48836.5'}, {'csv_line': 68, 'value': '-28497', 'bounds': '-18207.5 to 48836.5'}]
- check: total amount should equal nightly rate multiplied by nights; mismatch_count: 16; mismatch_examples: [{'csv_line': 7, 'nightly_rate_inr': '2725', 'nights': '3', 'total_amount_inr': '81750', 'expected_total': '8175'}, {'csv_line': 34, 'nightly_rate_inr': '2723', 'nights': '2', 'total_amount_inr': '54460', 'expected_total': '5446'}, {'csv_line': 68, 'nightly_rate_inr': '4071', 'nights': '7', 'total_amount_inr': '-28497', 'expected_total': '28497'}, {'csv_line': 72, 'nightly_rate_inr': '2915', 'nights': '0', 'total_amount_inr': '2915', 'expected_total': '0'}, {'csv_line': 89, 'nightly_rate_inr': '3664', 'nights': '5', 'total_amount_inr': '183200', 'expected_total': '18320'}]

### Impossible stays

- Count: 4
- Business impact: Impossible stays cause incorrect occupancy, availability, length-of-stay, and revenue-per-night metrics.
- Examples:
- csv_line: 72; check_in_date: 21 Mar 2026; issues: ['nights value 0 is not positive']; nights: 0
- csv_line: 110; check_in_date: 21/04/2026; issues: ['nights value 0 is not positive']; nights: 0
- csv_line: 192; check_in_date: 14 Mar 2026; issues: ['nights value 0 is not positive']; nights: 0
- csv_line: 215; check_in_date: 02-04-2026; issues: ['nights value 0 is not positive']; nights: 0
