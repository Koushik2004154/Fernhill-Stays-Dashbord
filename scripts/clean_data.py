#!/usr/bin/env python3
"""Clean audited booking data and document every cleaning decision."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("data/bookings_jan_may_2026.csv")
DEFAULT_CLEANED = Path("data/cleaned_bookings.csv")
DEFAULT_SUMMARY = Path("docs/CLEANING_SUMMARY.md")
AUDIT_REPORT = Path("docs/DATA_AUDIT.md")

MISSING_MARKERS = {"", "na", "n/a", "null", "none", "nan", "-", "--", "missing", "unknown"}
REPORTING_START = date(2026, 1, 1)
REPORTING_END = date(2026, 5, 31)

PROPERTY_MAP = {
    "marigoldsuites": "Marigold Suites",
    "cedarcourt": "Cedar Court",
    "palmgroveinn": "Palm Grove Inn",
    "lakeviewresidency": "Lakeview Residency",
    "birchwoodstay": "Birchwood Stay",
}

CHANNEL_MAP = {
    "direct": "Direct",
    "otammt": "OTA-MMT",
    "otabooking": "OTA-Booking",
    "corporate": "Corporate",
    "walkin": "Walk-in",
}

STATUS_MAP = {
    "checkedout": "Checked-out",
    "confirmed": "Confirmed",
    "cancelled": "Cancelled",
    "noshow": "No-show",
}

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d %b %Y",
    "%d %B %Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y/%m/%d",
]


@dataclass
class CleaningStats:
    original_row_count: int = 0
    final_row_count: int = 0
    rows_modified: set[int] = field(default_factory=set)
    removed_rows: list[dict[str, Any]] = field(default_factory=list)
    duplicate_records_removed: list[dict[str, Any]] = field(default_factory=list)
    revenue_corrections: list[dict[str, Any]] = field(default_factory=list)
    field_changes: list[dict[str, Any]] = field(default_factory=list)
    missing_value_actions: list[dict[str, Any]] = field(default_factory=list)
    date_conversions: list[dict[str, Any]] = field(default_factory=list)
    rule_counts: Counter = field(default_factory=Counter)
    assumptions: list[str] = field(default_factory=list)

    def record_change(self, csv_line: int, booking_id: str, field_name: str, old: Any, new: Any, rule: str) -> None:
        if str(old) == str(new):
            return
        self.rows_modified.add(csv_line)
        self.rule_counts[rule] += 1
        self.field_changes.append(
            {
                "csv_line": csv_line,
                "booking_id": booking_id,
                "field": field_name,
                "old": old,
                "new": new,
                "rule": rule,
            }
        )


def normalize_key(value: str) -> str:
    value = value.strip().lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "", value)


def is_missing(value: Any) -> bool:
    return value is None or str(value).strip().lower() in MISSING_MARKERS


def parse_decimal(value: Any) -> Decimal | None:
    if is_missing(value):
        return None
    normalized = re.sub(r"[,\s$]", "", str(value))
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal("1")))
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse_int(value: Any) -> int | None:
    parsed = parse_decimal(value)
    if parsed is None or parsed != parsed.to_integral_value():
        return None
    return int(parsed)


def parse_booking_date(value: str) -> tuple[date | None, str]:
    if is_missing(value):
        return None, "missing"

    candidates: list[tuple[date, str]] = []
    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt).date()
        except ValueError:
            continue
        candidates.append((parsed, fmt))

    if not candidates:
        return None, "unparseable"

    in_period = [(parsed, fmt) for parsed, fmt in candidates if REPORTING_START <= parsed <= REPORTING_END]
    pool = in_period or candidates

    priority = {
        "%Y-%m-%d": 0,
        "%d %b %Y": 1,
        "%d %B %Y": 1,
        "%d/%m/%Y": 2,
        "%d-%m-%Y": 2,
        "%m/%d/%Y": 3,
        "%m-%d-%Y": 3,
        "%Y/%m/%d": 4,
    }
    parsed, fmt = sorted(pool, key=lambda item: (priority.get(item[1], 99), item[0]))[0]
    return parsed, fmt


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no header row")
        return list(reader), reader.fieldnames


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def standardize_label(
    row: dict[str, str],
    csv_line: int,
    column: str,
    mapping: dict[str, str],
    fallback_title: bool,
    stats: CleaningStats,
    rule: str,
) -> None:
    old = row[column]
    if is_missing(old):
        return
    key = normalize_key(old)
    new = mapping.get(key)
    if new is None and fallback_title:
        new = re.sub(r"\s+", " ", old.strip()).title()
    if new and old != new:
        row[column] = new
        stats.record_change(csv_line, row["booking_id"], column, old, new, rule)


def handle_missing_values(row: dict[str, str], csv_line: int, stats: CleaningStats) -> None:
    booking_id = row["booking_id"]

    if is_missing(row["booking_channel"]):
        old = row["booking_channel"]
        row["booking_channel"] = "Unknown"
        stats.record_change(csv_line, booking_id, "booking_channel", old, "Unknown", "missing_booking_channel")
        stats.missing_value_actions.append(
            {
                "csv_line": csv_line,
                "booking_id": booking_id,
                "field": "booking_channel",
                "action": "Set to Unknown instead of dropping the booking.",
            }
        )

    nights = parse_decimal(row["nights"])
    nightly_rate = parse_decimal(row["nightly_rate_inr"])
    total_amount = parse_decimal(row["total_amount_inr"])

    if is_missing(row["nightly_rate_inr"]) and total_amount is not None and nights is not None and nights > 0:
        new_rate = total_amount / nights
        new_value = format_decimal(new_rate)
        row["nightly_rate_inr"] = new_value
        stats.record_change(csv_line, booking_id, "nightly_rate_inr", "", new_value, "missing_nightly_rate")
        stats.missing_value_actions.append(
            {
                "csv_line": csv_line,
                "booking_id": booking_id,
                "field": "nightly_rate_inr",
                "action": "Derived as total_amount_inr divided by nights.",
            }
        )
        nightly_rate = new_rate

    if is_missing(row["total_amount_inr"]) and nightly_rate is not None and nights is not None and nights > 0:
        new_total = nightly_rate * nights
        new_value = format_decimal(new_total)
        row["total_amount_inr"] = new_value
        stats.record_change(csv_line, booking_id, "total_amount_inr", "", new_value, "missing_total_amount")
        stats.missing_value_actions.append(
            {
                "csv_line": csv_line,
                "booking_id": booking_id,
                "field": "total_amount_inr",
                "action": "Derived as nightly_rate_inr multiplied by nights.",
            }
        )


def correct_revenue(row: dict[str, str], csv_line: int, stats: CleaningStats) -> None:
    booking_id = row["booking_id"]
    nights = parse_decimal(row["nights"])
    nightly_rate = parse_decimal(row["nightly_rate_inr"])
    total_amount = parse_decimal(row["total_amount_inr"])

    if nights is None or nights <= 0 or nightly_rate is None:
        return

    if nightly_rate < 0:
        old = row["nightly_rate_inr"]
        nightly_rate = abs(nightly_rate)
        row["nightly_rate_inr"] = format_decimal(nightly_rate)
        stats.record_change(csv_line, booking_id, "nightly_rate_inr", old, row["nightly_rate_inr"], "negative_rate_abs")

    expected_total = nightly_rate * nights
    if total_amount is None or total_amount != expected_total:
        old = row["total_amount_inr"]
        new = format_decimal(expected_total)
        row["total_amount_inr"] = new
        stats.record_change(csv_line, booking_id, "total_amount_inr", old, new, "revenue_formula_correction")
        stats.revenue_corrections.append(
            {
                "csv_line": csv_line,
                "booking_id": booking_id,
                "old_total_amount_inr": old,
                "new_total_amount_inr": new,
                "nightly_rate_inr": row["nightly_rate_inr"],
                "nights": row["nights"],
                "reason": "Corrected total_amount_inr to nightly_rate_inr * nights.",
            }
        )


def clean_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], CleaningStats]:
    stats = CleaningStats(original_row_count=len(rows))
    cleaned: list[dict[str, str]] = []
    seen_booking_ids: set[str] = set()

    stats.assumptions.extend(
        [
            "The source file represents stays from January through May 2026, so ambiguous dates are parsed to a date in that window when possible.",
            "For dates that remain ambiguous after the reporting-window check, day-first parsing is preferred because the property context is India.",
            "The first occurrence of a duplicate booking_id is treated as the system of record; later occurrences are removed and documented.",
            "Missing booking_channel values are retained as Unknown because channel cannot be inferred from other fields.",
            "Missing nightly_rate_inr and total_amount_inr are derived only when nights and the counterpart revenue field make the calculation deterministic.",
            "Revenue totals should equal nightly_rate_inr multiplied by nights; total_amount_inr is corrected to that formula when the inputs are valid.",
            "Rows with zero or negative nights are invalid stays and are removed rather than imputed.",
        ]
    )

    for source_index, original in enumerate(rows, start=2):
        row = dict(original)
        booking_id = row["booking_id"].strip()
        row["booking_id"] = booking_id

        nights = parse_int(row["nights"])
        if nights is None or nights <= 0:
            stats.removed_rows.append(
                {
                    "csv_line": source_index,
                    "booking_id": booking_id,
                    "reason": "Removed impossible stay with zero, negative, missing, or non-integer nights.",
                    "nights": row["nights"],
                }
            )
            continue

        if booking_id in seen_booking_ids:
            removal = {
                "csv_line": source_index,
                "booking_id": booking_id,
                "reason": "Removed duplicate booking_id after retaining the first occurrence.",
            }
            stats.duplicate_records_removed.append(removal)
            stats.removed_rows.append(removal)
            continue
        seen_booking_ids.add(booking_id)

        standardize_label(row, source_index, "property", PROPERTY_MAP, True, stats, "standardize_property")
        standardize_label(row, source_index, "booking_channel", CHANNEL_MAP, False, stats, "standardize_channel")
        standardize_label(row, source_index, "status", STATUS_MAP, False, stats, "standardize_status")

        parsed_date, date_rule = parse_booking_date(row["check_in_date"])
        if parsed_date is None:
            stats.removed_rows.append(
                {
                    "csv_line": source_index,
                    "booking_id": booking_id,
                    "reason": "Removed row because check_in_date could not be parsed safely.",
                    "check_in_date": row["check_in_date"],
                }
            )
            seen_booking_ids.remove(booking_id)
            continue

        iso_date = parsed_date.isoformat()
        if row["check_in_date"] != iso_date:
            old = row["check_in_date"]
            row["check_in_date"] = iso_date
            stats.record_change(source_index, booking_id, "check_in_date", old, iso_date, "iso_date_conversion")
            stats.date_conversions.append(
                {
                    "csv_line": source_index,
                    "booking_id": booking_id,
                    "old_check_in_date": old,
                    "new_check_in_date": iso_date,
                    "parse_rule": date_rule,
                }
            )

        handle_missing_values(row, source_index, stats)
        correct_revenue(row, source_index, stats)

        cleaned.append(row)

    stats.final_row_count = len(cleaned)
    return cleaned, stats


def documented_rows(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- None"
    lines = []
    for item in items:
        lines.append("- " + "; ".join(f"{key}: {value}" for key, value in item.items()))
    return "\n".join(lines)


def rule_table(stats: CleaningStats) -> str:
    rationale = {
        "standardize_property": "Creates one property dimension per real property so revenue and occupancy are not split across casing or spacing variants.",
        "standardize_channel": "Creates reliable channel attribution for source mix, commissions, and acquisition reporting.",
        "standardize_status": "Creates consistent lifecycle labels for confirmed, stayed, cancelled, and no-show analysis.",
        "iso_date_conversion": "Makes dates sortable, joinable, and safe for monthly trend reporting.",
        "missing_booking_channel": "Retains the booking while preserving the fact that attribution is unknown.",
        "missing_nightly_rate": "Backfills a deterministic rate from total amount and nights without inventing new commercial terms.",
        "missing_total_amount": "Backfills deterministic booking revenue from nightly rate and nights.",
        "negative_rate_abs": "Treats a negative rate as a sign error before calculating total revenue.",
        "revenue_formula_correction": "Aligns booking revenue to the auditable formula nightly_rate_inr * nights.",
    }
    lines = ["| Rule | Records changed | Business rationale |", "| --- | ---: | --- |"]
    for rule, reason in rationale.items():
        lines.append(f"| {rule} | {stats.rule_counts.get(rule, 0)} | {reason} |")
    lines.extend(
        [
            "| remove_duplicate_booking_id | "
            f"{len(stats.duplicate_records_removed)} | Prevents duplicate bookings from overstating revenue, occupancy, and guest volume. |",
            "| remove_impossible_stay | "
            f"{sum(1 for row in stats.removed_rows if 'impossible stay' in row['reason'])} | Removes records that cannot represent a real stay because nights is zero, negative, missing, or non-integer. |",
            "| remove_unparseable_date | "
            f"{sum(1 for row in stats.removed_rows if 'check_in_date' in row['reason'])} | Avoids assigning revenue and occupancy to an unsafe reporting period. |",
        ]
    )
    return "\n".join(lines)


def write_summary(path: Path, stats: CleaningStats, input_path: Path, output_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    modified_rows_count = len(stats.rows_modified)
    removed_count = len(stats.removed_rows)

    lines = [
        "# Cleaning Summary: Bookings Jan-May 2026",
        "",
        "This summary documents every cleaning decision made by `scripts/clean_data.py`.",
        "",
        "## Inputs and Outputs",
        "",
        f"- Source CSV: `{input_path.as_posix()}`",
        f"- Audit report used: `{AUDIT_REPORT.as_posix()}`",
        f"- Cleaned CSV: `{output_path.as_posix()}`",
        "",
        "## Required Metrics",
        "",
        f"- Original row count: {stats.original_row_count}",
        f"- Final row count: {stats.final_row_count}",
        f"- Rows modified: {modified_rows_count}",
        f"- Rows removed: {removed_count}",
        f"- Revenue corrections: {len(stats.revenue_corrections)}",
        f"- Duplicate records removed: {len(stats.duplicate_records_removed)}",
        "",
        "## Assumptions Made",
        "",
        *[f"- {item}" for item in stats.assumptions],
        "",
        "## Business Rationale by Cleaning Rule",
        "",
        rule_table(stats),
        "",
        "## Rows Removed",
        "",
        "No records were silently dropped. Removed records are listed below.",
        "",
        documented_rows(stats.removed_rows),
        "",
        "## Revenue Corrections",
        "",
        documented_rows(stats.revenue_corrections),
        "",
        "## Missing Value Handling",
        "",
        documented_rows(stats.missing_value_actions),
        "",
        "## Date Conversions",
        "",
        documented_rows(stats.date_conversions),
        "",
        "## Field-Level Standardization and Corrections",
        "",
        documented_rows(stats.field_changes),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean audited bookings data and write a summary report.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_CLEANED)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    rows, fieldnames = read_rows(args.input)
    cleaned, stats = clean_rows(rows)
    write_rows(args.output, cleaned, fieldnames)
    write_summary(args.summary, stats, args.input, args.output)
    print(f"Wrote cleaned data to {args.output}")
    print(f"Wrote cleaning summary to {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
