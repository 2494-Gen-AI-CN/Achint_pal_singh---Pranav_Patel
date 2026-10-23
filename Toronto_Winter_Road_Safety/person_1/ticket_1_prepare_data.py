"""Ticket A1: load and prepare the Toronto collision time fields.

The input CSV is read only. No code from Person 2 is required.
"""

import argparse
from pathlib import Path

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
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    df = load_temporal_data(args.csv)
    print_inspection(df)
    print("\nFirst five prepared rows:")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
