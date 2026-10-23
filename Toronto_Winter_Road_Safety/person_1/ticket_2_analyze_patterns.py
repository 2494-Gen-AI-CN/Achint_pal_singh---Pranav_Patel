"""Ticket A2: calculate monthly, hourly and weekday collision patterns."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ticket_1_prepare_data import (
    DEFAULT_CSV, MONTHS, WEEKDAYS, YEARS, load_temporal_data, print_inspection,
)


def collisions_by_month(df):
    """Return 24 rows: every year/month pair in chronological order."""
    yearly_tables = []

    for year in YEARS:
        year_data = df[df["OCC_YEAR"] == year]
        counts = year_data["OCC_MONTH"].value_counts()
        counts = counts.reindex(MONTHS, fill_value=0)

        table = counts.rename_axis("OCC_MONTH").reset_index(name="collisions")
        table.insert(0, "OCC_YEAR", year)
        yearly_tables.append(table)

    return pd.concat(yearly_tables, ignore_index=True)


def collisions_by_hour(df):
    """Count the combined 2024-2025 records for each hour, 00 through 23."""
    counts = df["OCC_HOUR"].value_counts()
    counts = counts.reindex(np.arange(24), fill_value=0)
    return counts.rename_axis("OCC_HOUR").reset_index(name="collisions")


def collisions_by_weekday(df):
    """Count the combined records, ordered Monday through Sunday."""
    counts = df["OCC_DOW"].value_counts()
    counts = counts.reindex(WEEKDAYS, fill_value=0)
    return counts.rename_axis("OCC_DOW").reset_index(name="collisions")


def verify_group_totals(df):
    """Reconcile each grouping against records with a usable grouping value."""
    summaries = [
        ("Month", "OCC_MONTH", collisions_by_month(df)),
        ("Hour", "OCC_HOUR", collisions_by_hour(df)),
        ("Weekday", "OCC_DOW", collisions_by_weekday(df)),
    ]
    checks = []
    for label, column, summary in summaries:
        eligible = int(df[column].notna().sum())
        grouped = int(summary["collisions"].sum())
        if eligible != grouped:
            raise ValueError(f"{label} counts do not reconcile: {grouped} != {eligible}.")
        checks.append({
            "grouping": label, "eligible_records": eligible,
            "excluded_records": len(df) - eligible, "grouped_total": grouped,
        })
    return pd.DataFrame(checks)


def key_findings(df):
    """Generate evidence-supported text; include all ties for the top count."""
    counts = df.groupby("OCC_YEAR").size().reindex(YEARS, fill_value=0)
    change = int(counts.loc[2025] - counts.loc[2024])
    if counts.loc[2024]:
        percent = change / counts.loc[2024] * 100
        annual = (
            f"Reported records changed from {counts.loc[2024]:,} in 2024 to "
            f"{counts.loc[2025]:,} in 2025 ({change:+,}; {percent:+.2f}%)."
        )
    else:
        annual = "No 2024 records are available for a year-over-year comparison."

    monthly = collisions_by_month(df)
    findings = [annual]
    if monthly["collisions"].sum() == 0:
        findings.append("No valid month values are available.")
    else:
        maximum = monthly["collisions"].max()
        peaks = monthly[monthly["collisions"] == maximum]
        month_names = []
        for _, row in peaks.iterrows():
            month_names.append(f"{row['OCC_MONTH']} {row['OCC_YEAR']}")
        month_labels = ", ".join(month_names)
        findings.append(
            f"Highest-count year/month: {month_labels}, with {int(maximum):,} records each."
        )
    for label, column, summary in [
        ("hour", "OCC_HOUR", collisions_by_hour(df)),
        ("weekday", "OCC_DOW", collisions_by_weekday(df)),
    ]:
        if not summary["collisions"].sum():
            findings.append(f"No valid {label} values are available.")
            continue
        maximum = int(summary["collisions"].max())
        values = summary.loc[summary["collisions"] == maximum, column]
        names = []
        for value in values:
            if label == "hour":
                names.append(f"{int(value):02d}:00-{int(value):02d}:59")
            else:
                names.append(str(value))
        labels = ", ".join(names)
        findings.append(
            f"Highest-count {label}: {labels}, with {maximum:,} records each "
            "across 2024-2025."
        )
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Original full CSV path")
    args = parser.parse_args()
    df = load_temporal_data(args.csv)
    print_inspection(df)
    print("\nReconciliation\n" + verify_group_totals(df).to_string(index=False))
    for title, summary in [
        ("Monthly", collisions_by_month(df)),
        ("Hourly", collisions_by_hour(df)),
        ("Weekday", collisions_by_weekday(df)),
    ]:
        print(f"\n{title}\n{summary.to_string(index=False)}")
    print("\nFindings")
    for finding in key_findings(df):
        print("- " + finding)


if __name__ == "__main__":
    main()
