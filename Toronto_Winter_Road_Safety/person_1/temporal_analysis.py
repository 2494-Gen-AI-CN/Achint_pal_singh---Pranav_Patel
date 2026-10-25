"""Person 1: inspect and count Toronto collisions by recorded calendar fields.

The input CSV is read only. No code from Person 2 is required.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PERSON_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = (      
    PERSON_DIR.parent / "data" / "raw" / "collisions"
    / "Traffic Collisions - 4326 (1).csv"
)
YEARS = [2024, 2025]
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]
TIME_COLUMNS = ["OCC_YEAR", "OCC_MONTH", "OCC_DOW", "OCC_HOUR"]
REFERENCE_COUNTS = {2024: 70181, 2025: 67546}


def load_temporal_data(csv_path=DEFAULT_CSV):
    """Read four time columns and prepare the 2024-2025 subset.

    Invalid/missing month, weekday and hour values become missing in memory.
    Their records remain available for other groupings. Each summary omits only
    rows missing its own grouping field. Inspection counts are in df.attrs.
    We use the published year/month/weekday/hour, not a derived OCC_DATE hour.
    """
    # A1, step 1: read only the four columns needed for time analysis.
    source = Path(csv_path).expanduser().resolve()
    raw = pd.read_csv(source, usecols=TIME_COLUMNS, dtype="string")

    # A1, step 2: turn years into numbers and keep 2024 and 2025.
    raw["OCC_YEAR"] = pd.to_numeric(raw["OCC_YEAR"], errors="coerce")
    df = raw[raw["OCC_YEAR"].isin(YEARS)].copy()
    if df.empty:
        raise ValueError("The CSV contains no records for 2024 or 2025.")
    df["OCC_YEAR"] = df["OCC_YEAR"].astype("int64")

    # A1, step 3: give months and weekdays a calendar order.
    df["OCC_MONTH"] = pd.Categorical(
        df["OCC_MONTH"].str.strip(), categories=MONTHS, ordered=True,
    )
    df["OCC_DOW"] = pd.Categorical(
        df["OCC_DOW"].str.strip(), categories=WEEKDAYS, ordered=True,
    )

    # A1, step 4: only whole hours from 0 to 23 are valid.
    # Invalid hours become missing; the other values in that row stay usable.
    hours = pd.to_numeric(df["OCC_HOUR"], errors="coerce")
    hours = hours.where(hours.isin(range(24)))
    df["OCC_HOUR"] = hours.astype("Int64")
    df = df.reset_index(drop=True)

    # Save a small inspection summary alongside the DataFrame for the report.
    rows_by_year = {}
    for year in YEARS:
        rows_by_year[year] = int((df["OCC_YEAR"] == year).sum())

    missing_values = {}
    for column in ["OCC_MONTH", "OCC_HOUR", "OCC_DOW"]:
        missing_values[column] = int(df[column].isna().sum())

    df.attrs["inspection"] = {
        "source_file": str(source),
        "source_rows": len(raw),
        "selected_rows": len(df),
        "rows_by_year": rows_by_year,
        "missing_or_invalid": missing_values,
        "reference_counts_match": rows_by_year == REFERENCE_COUNTS,
    }
    return df


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


def print_inspection(df):
    """Print a compact quality check for ticket A1."""
    info = df.attrs["inspection"]
    print(f"Source: {info['source_file']}")
    print(f"Source records: {info['source_rows']:,}")
    print(f"Selected 2024-2025 records: {info['selected_rows']:,}")
    for year, count in info["rows_by_year"].items():
        print(f"  {year}: {count:,}")
    for field, count in info["missing_or_invalid"].items():
        print(f"  Missing/invalid {field}: {count:,}")
    if not info["reference_counts_match"]:
        print("NOTICE: counts differ from the supplied PDF snapshot; review source coverage.")


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
