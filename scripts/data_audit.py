#!/usr/bin/env python3
"""Audit booking CSV data without modifying source records."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import median
from typing import Any


DEFAULT_INPUT = Path("data/bookings_jan_may_2026.csv")
DEFAULT_OUTPUT = Path("docs/DATA_AUDIT.md")
MISSING_MARKERS = {"", "na", "n/a", "null", "none", "nan", "-", "--", "missing", "unknown"}

DATE_PATTERNS = [
    ("%Y-%m-%d", re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")),
    ("%d-%m-%Y", re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")),
    ("%m-%d-%Y", re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")),
    ("%d/%m/%Y", re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")),
    ("%m/%d/%Y", re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")),
    ("%Y/%m/%d", re.compile(r"^\d{4}/\d{1,2}/\d{1,2}$")),
    ("%d %b %Y", re.compile(r"^\d{1,2}\s+[A-Za-z]{3}\s+\d{4}$")),
    ("%d %B %Y", re.compile(r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$")),
]


def clean_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def display_header(fieldnames: list[str], cleaned: str | None) -> str:
    if not cleaned:
        return "Not found"
    for name in fieldnames:
        if clean_header(name) == cleaned:
            return name
    return cleaned


def is_missing(value: Any) -> bool:
    return value is None or str(value).strip().lower() in MISSING_MARKERS


def normalize_label(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"\b(com|co|in|org|net)\b", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def infer_column(fieldnames: list[str], candidates: list[str]) -> str | None:
    cleaned = {clean_header(name): name for name in fieldnames}
    for candidate in candidates:
        if candidate in cleaned:
            return candidate
    for name in cleaned:
        if any(candidate in name for candidate in candidates):
            return name
    return None


def infer_columns(fieldnames: list[str], needles: list[str]) -> list[str]:
    results = []
    for name in fieldnames:
        cleaned = clean_header(name)
        if any(needle in cleaned for needle in needles):
            results.append(cleaned)
    return results


def get_value(row: dict[str, str], cleaned_column: str | None) -> str:
    if not cleaned_column:
        return ""
    for key, value in row.items():
        if clean_header(key) == cleaned_column:
            return value
    return ""


def parse_decimal(value: str) -> Decimal | None:
    if is_missing(value):
        return None
    normalized = re.sub(r"[,\s$]", "", str(value))
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def detect_date_format(value: str) -> str | None:
    if is_missing(value):
        return None
    text = value.strip()
    for fmt, pattern in DATE_PATTERNS:
        if pattern.match(text):
            return fmt
    return "unrecognized"


def parse_date(value: str) -> datetime | None:
    fmt = detect_date_format(value)
    if not fmt or fmt == "unrecognized":
        return None
    for candidate, _ in DATE_PATTERNS:
        if candidate == fmt:
            try:
                return datetime.strptime(value.strip(), candidate)
            except ValueError:
                return None
    return None


def example_rows(rows: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    return rows[:limit]


def audit(rows: list[dict[str, str]], fieldnames: list[str]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    booking_id_col = infer_column(fieldnames, ["booking_id", "bookingid", "reservation_id", "confirmation_id", "id"])
    property_col = infer_column(fieldnames, ["property_name", "property", "listing_name", "listing", "hotel"])
    channel_col = infer_column(fieldnames, ["booking_channel", "channel", "source", "platform"])
    status_col = infer_column(fieldnames, ["booking_status", "status", "reservation_status"])
    checkin_col = infer_column(fieldnames, ["check_in", "checkin", "arrival", "arrival_date", "start_date"])
    checkout_col = infer_column(fieldnames, ["check_out", "checkout", "departure", "departure_date", "end_date"])
    nights_col = infer_column(fieldnames, ["nights", "night_count", "length_of_stay", "los"])
    revenue_cols = infer_columns(fieldnames, ["revenue", "amount", "total", "price", "rate", "adr"])
    date_cols = sorted(set(infer_columns(fieldnames, ["date", "checkin", "checkout", "arrival", "departure"])))

    metadata = {
        "booking_id_col": display_header(fieldnames, booking_id_col),
        "property_col": display_header(fieldnames, property_col),
        "channel_col": display_header(fieldnames, channel_col),
        "status_col": display_header(fieldnames, status_col),
        "checkin_col": display_header(fieldnames, checkin_col),
        "checkout_col": display_header(fieldnames, checkout_col),
        "nights_col": display_header(fieldnames, nights_col),
        "revenue_cols": ", ".join(display_header(fieldnames, col) for col in revenue_cols) or "Not found",
        "date_cols": ", ".join(display_header(fieldnames, col) for col in date_cols) or "Not found",
    }

    issues: list[dict[str, Any]] = []

    duplicate_examples = []
    if booking_id_col:
        booking_ids = defaultdict(list)
        for index, row in enumerate(rows, start=2):
            value = get_value(row, booking_id_col).strip()
            if not is_missing(value):
                booking_ids[value].append(index)
        duplicates = {value: line_numbers for value, line_numbers in booking_ids.items() if len(line_numbers) > 1}
        duplicate_examples = [
            {"booking_id": value, "csv_lines": line_numbers}
            for value, line_numbers in list(duplicates.items())[:5]
        ]
        duplicate_count = sum(len(lines) for lines in duplicates.values())
    else:
        duplicate_count = 0
        duplicate_examples = [{"detail": "No booking ID column was detected."}]
    issues.append(
        issue(
            "Duplicate booking IDs",
            duplicate_count,
            duplicate_examples,
            "Duplicate IDs can double count revenue, occupancy, cancellations, and guest volume.",
        )
    )

    for issue_name, column, impact in [
        (
            "Inconsistent property names",
            property_col,
            "Variant property names split performance metrics across multiple labels and make property-level reporting unreliable.",
        ),
        (
            "Inconsistent booking channels",
            channel_col,
            "Channel variants distort source mix, commission analysis, and marketing attribution.",
        ),
        (
            "Inconsistent booking statuses",
            status_col,
            "Status variants can misclassify active stays, cancellations, no-shows, and realized revenue.",
        ),
    ]:
        examples, count = label_inconsistencies(rows, column)
        issues.append(issue(issue_name, count, examples, impact))

    missing_examples = []
    missing_count = 0
    for field in fieldnames:
        missing_lines = [index for index, row in enumerate(rows, start=2) if is_missing(row.get(field))]
        if missing_lines:
            missing_count += len(missing_lines)
            missing_examples.append(
                {"column": field, "missing_count": len(missing_lines), "csv_lines": missing_lines[:5]}
            )
    issues.append(
        issue(
            "Missing values",
            missing_count,
            example_rows(missing_examples),
            "Missing values reduce trust in occupancy, guest, revenue, and segmentation reporting; they can also break downstream joins and filters.",
        )
    )

    date_examples = []
    date_issue_count = 0
    for col in date_cols:
        formats = Counter()
        invalid_lines = []
        for index, row in enumerate(rows, start=2):
            value = get_value(row, col)
            if is_missing(value):
                continue
            fmt = detect_date_format(value)
            formats[fmt or "missing"] += 1
            if fmt == "unrecognized" or parse_date(value) is None:
                invalid_lines.append({"csv_line": index, "value": value})
        real_formats = [fmt for fmt in formats if fmt not in {"missing"}]
        if len(real_formats) > 1 or invalid_lines:
            date_issue_count += sum(formats.values())
            date_examples.append(
                {
                    "column": display_header(fieldnames, col),
                    "formats": dict(formats),
                    "invalid_examples": invalid_lines[:5],
                }
            )
    issues.append(
        issue(
            "Invalid or mixed date formats",
            date_issue_count,
            example_rows(date_examples),
            "Mixed or invalid dates can shift bookings into the wrong month, corrupt stay length, and break trend reporting.",
        )
    )

    revenue_examples, revenue_count = revenue_anomalies(rows, fieldnames, revenue_cols, nights_col)
    issues.append(
        issue(
            "Revenue anomalies",
            revenue_count,
            revenue_examples,
            "Revenue anomalies can materially overstate or understate sales, ADR, RevPAR, owner payouts, and tax or commission calculations.",
        )
    )

    stay_examples, stay_count = impossible_stays(rows, fieldnames, checkin_col, checkout_col, nights_col)
    issues.append(
        issue(
            "Impossible stays",
            stay_count,
            stay_examples,
            "Impossible stays cause incorrect occupancy, availability, length-of-stay, and revenue-per-night metrics.",
        )
    )

    return issues, metadata


def issue(issue_type: str, count: int, examples: list[dict[str, Any]], business_impact: str) -> dict[str, Any]:
    return {
        "issue_type": issue_type,
        "count": count,
        "examples": examples,
        "business_impact": business_impact,
    }


def label_inconsistencies(rows: list[dict[str, str]], column: str | None) -> tuple[list[dict[str, Any]], int]:
    if not column:
        return ([{"detail": "Column was not detected."}], 0)
    grouped = defaultdict(Counter)
    for row in rows:
        raw = get_value(row, column).strip()
        if not is_missing(raw):
            grouped[normalize_label(raw)][raw] += 1
    examples = []
    count = 0
    for normalized, variants in grouped.items():
        if len(variants) > 1:
            count += sum(variants.values())
            examples.append(
                {
                    "normalized_value": normalized,
                    "variants": dict(variants.most_common()),
                }
            )
    return example_rows(examples), count


def revenue_anomalies(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    revenue_cols: list[str],
    nights_col: str | None,
) -> tuple[list[dict[str, Any]], int]:
    if not revenue_cols:
        return ([{"detail": "No revenue-like columns were detected."}], 0)

    examples = []
    count = 0
    for col in revenue_cols:
        values = []
        invalid = []
        non_positive = []
        for index, row in enumerate(rows, start=2):
            raw = get_value(row, col)
            if is_missing(raw):
                continue
            parsed = parse_decimal(raw)
            if parsed is None:
                invalid.append({"csv_line": index, "value": raw})
                continue
            values.append((index, parsed, raw))
            if parsed <= 0:
                non_positive.append({"csv_line": index, "value": raw})

        numeric_values = [value for _, value, _ in values]
        outliers = []
        if len(numeric_values) >= 4:
            sorted_values = sorted(numeric_values)
            mid = len(sorted_values) // 2
            lower = sorted_values[:mid]
            upper = sorted_values[mid + (0 if len(sorted_values) % 2 == 0 else 1) :]
            q1 = Decimal(str(median(lower)))
            q3 = Decimal(str(median(upper)))
            iqr = q3 - q1
            upper_bound = q3 + (iqr * Decimal("1.5"))
            lower_bound = q1 - (iqr * Decimal("1.5"))
            for index, value, raw in values:
                if value < lower_bound or value > upper_bound:
                    outliers.append({"csv_line": index, "value": raw, "bounds": f"{lower_bound} to {upper_bound}"})

        column_count = len(invalid) + len(non_positive) + len(outliers)
        if column_count:
            count += column_count
            examples.append(
                {
                    "column": display_header(fieldnames, col),
                    "invalid_numeric_examples": invalid[:5],
                    "non_positive_examples": non_positive[:5],
                    "outlier_examples": outliers[:5],
                }
            )

    nightly_col = next((col for col in revenue_cols if "nightly" in col or "rate" in col), None)
    total_col = next((col for col in revenue_cols if "total" in col or "amount" in col), None)
    if nightly_col and total_col and nights_col:
        mismatches = []
        for index, row in enumerate(rows, start=2):
            nightly = parse_decimal(get_value(row, nightly_col))
            total = parse_decimal(get_value(row, total_col))
            nights = parse_decimal(get_value(row, nights_col))
            if nightly is None or total is None or nights is None:
                continue
            expected = nightly * nights
            if total != expected:
                mismatches.append(
                    {
                        "csv_line": index,
                        display_header(fieldnames, nightly_col): str(nightly),
                        display_header(fieldnames, nights_col): str(nights),
                        display_header(fieldnames, total_col): str(total),
                        "expected_total": str(expected),
                    }
                )
        if mismatches:
            count += len(mismatches)
            examples.append(
                {
                    "check": "total amount should equal nightly rate multiplied by nights",
                    "mismatch_count": len(mismatches),
                    "mismatch_examples": mismatches[:5],
                }
            )
    return example_rows(examples), count


def impossible_stays(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    checkin_col: str | None,
    checkout_col: str | None,
    nights_col: str | None,
) -> tuple[list[dict[str, Any]], int]:
    if not checkin_col:
        return ([{"detail": "Check-in column was not detected."}], 0)

    examples = []
    count = 0
    for index, row in enumerate(rows, start=2):
        checkin_raw = get_value(row, checkin_col)
        checkout_raw = get_value(row, checkout_col) if checkout_col else ""
        nights_raw = get_value(row, nights_col) if nights_col else ""
        checkin = parse_date(checkin_raw)
        checkout = parse_date(checkout_raw) if checkout_col else None
        nights = parse_decimal(nights_raw) if nights_col else None
        row_issues = []
        if nights_col:
            if nights is None and not is_missing(nights_raw):
                row_issues.append(f"nights value {nights_raw} is not numeric")
            elif nights is not None:
                if nights <= 0:
                    row_issues.append(f"nights value {nights_raw} is not positive")
                if nights != nights.to_integral_value():
                    row_issues.append(f"nights value {nights_raw} is not a whole number")
        if checkin and checkout:
            stay_length = (checkout - checkin).days
            if stay_length <= 0:
                row_issues.append("check-out is not after check-in")
            if nights_col:
                if nights is not None and nights != stay_length:
                    row_issues.append(f"nights value {nights_raw} does not match date span {stay_length}")
        elif not checkout_col and nights_col and nights is not None and nights > 0:
            row_issues.append("check-out date is unavailable, so stay end date cannot be validated")
        if row_issues:
            hard_issues = [
                text for text in row_issues if text != "check-out date is unavailable, so stay end date cannot be validated"
            ]
            if not hard_issues:
                continue
            count += len(hard_issues)
            example = {
                "csv_line": index,
                display_header(fieldnames, checkin_col): checkin_raw,
                "issues": hard_issues,
            }
            if checkout_col:
                example[display_header(fieldnames, checkout_col)] = checkout_raw
            if nights_col:
                example[display_header(fieldnames, nights_col)] = nights_raw
            examples.append(
                example
            )
    if not examples and not checkout_col:
        examples.append(
            {
                "detail": "No impossible stays found from check-in plus nights; checkout column is absent, so stay end dates cannot be fully validated."
            }
        )
    return example_rows(examples), count


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")
        rows = list(reader)
        return rows, reader.fieldnames


def markdown_table(issues: list[dict[str, Any]]) -> str:
    lines = [
        "| Issue type | Count | Business impact |",
        "| --- | ---: | --- |",
    ]
    for item in issues:
        impact = str(item["business_impact"]).replace("|", "\\|")
        lines.append(f"| {item['issue_type']} | {item['count']} | {impact} |")
    return "\n".join(lines)


def format_examples(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return "No examples found."
    lines = []
    for example in examples:
        parts = [f"{key}: {value}" for key, value in example.items()]
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def write_report(
    output_path: Path,
    input_path: Path,
    issues: list[dict[str, Any]],
    metadata: dict[str, str],
    row_count: int,
    fieldnames: list[str],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Data Audit: Bookings Jan-May 2026",
        "",
        "This report audits source data quality only. No records were cleaned or modified.",
        "",
        "## Source",
        "",
        f"- File: `{input_path.as_posix()}`",
        f"- Rows audited: {row_count}",
        f"- Columns audited: {len(fieldnames)}",
        f"- Column names: {', '.join(f'`{name}`' for name in fieldnames)}",
        "",
        "## Detected Columns",
        "",
    ]
    for key, value in metadata.items():
        lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    lines.extend(["", "## Summary", "", markdown_table(issues), "", "## Detailed Findings", ""])

    for item in issues:
        lines.extend(
            [
                f"### {item['issue_type']}",
                "",
                f"- Count: {item['count']}",
                f"- Business impact: {item['business_impact']}",
                "- Examples:",
                format_examples(item["examples"]),
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_missing_report(output_path: Path, input_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                "# Data Audit: Bookings Jan-May 2026",
                "",
                "Audit status: blocked because the source CSV was not found.",
                "",
                "Expected source file:",
                "",
                f"- `{input_path.as_posix()}`",
                "",
                "No data was cleaned or modified.",
                "",
                "## Required Audit Coverage",
                "",
                "| Issue type | Count | Examples | Business impact |",
                "| --- | ---: | --- | --- |",
                "| Duplicate booking IDs | Not audited | Source file missing | Duplicate IDs can double count revenue, occupancy, cancellations, and guest volume. |",
                "| Inconsistent property names | Not audited | Source file missing | Variant property names split performance metrics across multiple labels and make property-level reporting unreliable. |",
                "| Inconsistent booking channels | Not audited | Source file missing | Channel variants distort source mix, commission analysis, and marketing attribution. |",
                "| Inconsistent booking statuses | Not audited | Source file missing | Status variants can misclassify active stays, cancellations, no-shows, and realized revenue. |",
                "| Missing values | Not audited | Source file missing | Missing values reduce trust in reporting and can break downstream joins and filters. |",
                "| Invalid or mixed date formats | Not audited | Source file missing | Mixed or invalid dates can shift bookings into the wrong period and corrupt trend reporting. |",
                "| Revenue anomalies | Not audited | Source file missing | Revenue anomalies can materially overstate or understate sales, ADR, RevPAR, payouts, taxes, and commissions. |",
                "| Impossible stays | Not audited | Source file missing | Impossible stays cause incorrect occupancy, availability, stay length, and revenue-per-night metrics. |",
                "",
                "Run the audit after adding the CSV:",
                "",
                "```powershell",
                "py scripts/data_audit.py",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit booking CSV data and write a markdown report.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to source booking CSV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to markdown audit report.")
    parser.add_argument(
        "--write-missing-report",
        action="store_true",
        help="Write a blocked report if the input file is missing.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        if args.write_missing_report:
            write_missing_report(args.output, args.input)
        print(f"ERROR: Source CSV not found: {args.input}", flush=True)
        return 2

    rows, fieldnames = read_csv(args.input)
    issues, metadata = audit(rows, fieldnames)
    write_report(args.output, args.input, issues, metadata, len(rows), fieldnames)
    print(f"Wrote audit report to {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
