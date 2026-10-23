"""Ticket A1: a simple Pandas and NumPy version. The original CSV stays unchanged."""

import pandas as pd
import numpy as np

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]


def load_temporal_data(csv_path):
    # 1. Read the four columns needed for time analysis.
    columns = ["OCC_YEAR", "OCC_MONTH", "OCC_DOW", "OCC_HOUR"]
    df = pd.read_csv(csv_path, usecols=columns)

    # 2. Keep only 2024 and 2025.
    df["OCC_YEAR"] = pd.to_numeric(df["OCC_YEAR"], errors="coerce")
    df = df[df["OCC_YEAR"].isin([2024, 2025])].copy()
    if df.empty:
        raise ValueError("No records found for 2024 or 2025.")
    df["OCC_YEAR"] = df["OCC_YEAR"].astype(int)

    # 3. Put months and weekdays in calendar order; unknown labels become missing.
    df["OCC_MONTH"] = pd.Categorical(df["OCC_MONTH"].str.strip(), categories=MONTHS, ordered=True)
    df["OCC_DOW"] = pd.Categorical(df["OCC_DOW"].str.strip(), categories=WEEKDAYS, ordered=True)

    # 4. Keep whole hours 0-23. Invalid hours become missing, not deleted rows.
    hours = pd.to_numeric(df["OCC_HOUR"], errors="coerce")
    df["OCC_HOUR"] = np.where(hours.isin(np.arange(24)), hours, np.nan)
    df["OCC_HOUR"] = df["OCC_HOUR"].astype("Int64")

    # 5. Return the prepared table with fresh row numbers.
    return df.reset_index(drop=True)


if __name__ == "__main__":
    # Run from the person_1 folder. Change this path if your CSV is elsewhere.
    csv_path = "../data/raw/collisions/Traffic Collisions - 4326 (1).csv"
    data = load_temporal_data(csv_path)

    print("Records by year:")
    print(data["OCC_YEAR"].value_counts().sort_index())
    print("\nTotal selected records:", len(data))
    print("\nMissing or invalid values:")
    print(data.isna().sum())
    print("\nFirst five rows:")
    print(data.head())

    # Save a separate CSV without adding the DataFrame's row numbers.
    output_csv = "ticket_A1_prepared_data.csv"
    data.to_csv(output_csv, index=False)

    # Read it again and verify that the saved rows and values match.
    saved_data = pd.read_csv(output_csv, dtype={"OCC_YEAR": "Int64", "OCC_HOUR": "Int64"})
    pd.testing.assert_frame_equal(data, saved_data, check_dtype=False, check_categorical=False)
    print("\nExport verified: saved rows and values match the prepared data.")
    print("Saved CSV:", output_csv)
