"""Ticket A2: read A1's prepared CSV and calculate collision patterns."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Save plots without requiring a separate Windows GUI.
import matplotlib.pyplot as plt

from ticket_A1 import MONTHS, WEEKDAYS

# COLLISON HAS BEEN OCCUR IN THE MONTHS 
def collisions_by_month(df):
    """Count each year/month pair, ordered January to December."""
    data = df.copy()
    data["OCC_MONTH"] = pd.Categorical(data["OCC_MONTH"], categories=MONTHS, ordered=True)
    counts = data.groupby(["OCC_YEAR", "OCC_MONTH"], observed=False).size() # TO SEE IF WE ARE GETTING ALL THE MONTHS 
    return counts.reset_index(name="collisions")


def collisions_by_hour(df):
    """Count each hour, ordered 0 to 23, combining both years."""
    counts = df["OCC_HOUR"].value_counts()
    counts = counts.reindex(np.arange(24), fill_value=0)
    return counts.rename_axis("OCC_HOUR").reset_index(name="collisions")


def collisions_by_weekday(df):
    """Count each weekday, ordered Monday to Sunday, combining both years."""
    counts = df["OCC_DOW"].value_counts()
    counts = counts.reindex(WEEKDAYS, fill_value=0)
    return counts.rename_axis("OCC_DOW").reset_index(name="collisions")


def collisions_by_year(df):
    counts = df["OCC_YEAR"].value_counts().reindex([2024, 2025], fill_value=0)
    return counts.rename_axis("OCC_YEAR").reset_index(name="collisions")


def verify_group_totals(df):
    """Check each count table against rows with that time value present."""
    checks = []
    for name, column, table in [
        ("Month", "OCC_MONTH", collisions_by_month(df)),
        ("Hour", "OCC_HOUR", collisions_by_hour(df)),
        ("Weekday", "OCC_DOW", collisions_by_weekday(df)),
    ]:
        eligible = int(df[column].notna().sum())
        total = int(table["collisions"].sum())
        if total != eligible:
            raise ValueError(f"{name} total does not match the eligible records.")
        checks.append({"grouping": name, "eligible_records": eligible,
                       "excluded_records": len(df) - eligible, "grouped_total": total})
    return pd.DataFrame(checks)

# VERIFYING THE DATA IS WORKING GOOD ARE HOW MUCH ACCURATE  
def key_findings(df):
    """Compare the years and show each highest-count table, including ties."""
    # 1. Count the records in each year and subtract the two totals.
    total_2024 = len(df[df["OCC_YEAR"] == 2024])
    total_2025 = len(df[df["OCC_YEAR"] == 2025])
    difference = total_2025 - total_2024

    # 2. Keep the year/month rows with the largest count.
    monthly = collisions_by_month(df)
    valid_months = monthly[monthly["collisions"] > 0]
    top_months = valid_months[valid_months["collisions"] == valid_months["collisions"].max()]

    # 3. Do the same for hours.
    hourly = collisions_by_hour(df)
    valid_hours = hourly[hourly["collisions"] > 0]
    top_hours = valid_hours[valid_hours["collisions"] == valid_hours["collisions"].max()]

    # 4. Do the same for weekdays.
    weekdays = collisions_by_weekday(df)
    valid_days = weekdays[weekdays["collisions"] > 0]
    top_days = valid_days[valid_days["collisions"] == valid_days["collisions"].max()]

    # Empty peak tables mean no valid records were available for that field.
    return [
        f"2024: {total_2024:,}; 2025: {total_2025:,}; difference: {difference:+,} records.",
        "Highest-count year/month:\n" + top_months.to_string(index=False),
        "Highest-count hour (0-23):\n" + top_hours.to_string(index=False),
        "Highest-count weekday:\n" + top_days.to_string(index=False),
    ]


def plot_monthly_comparison(monthly):
    """Save one monthly comparison plot. A3 remains the full chart task."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for year in [2024, 2025]:
        rows = monthly[monthly["OCC_YEAR"] == year]
        ax.plot(rows["OCC_MONTH"].astype(str), rows["collisions"], marker="o", label=str(year))
    ax.set_title("Toronto monthly collision records: 2024 vs 2025")
    ax.set_xlabel("Month")
    ax.set_ylabel("Reported collision records")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_ylim(bottom=0)
    ax.legend()
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.text(0.02, 0.02, "Source: Toronto Police Service. Raw counts; not adjusted for traffic volume.", fontsize=9)
    output = "ticket_A2_monthly_comparison.png"
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


if __name__ == "__main__":
    # Run from person_1. This reads the separate CSV saved by ticket_A1.py.
    data = pd.read_csv("ticket_A1_prepared_data.csv", dtype={"OCC_YEAR": "Int64", "OCC_HOUR": "Int64"})
    data = data[data["OCC_YEAR"].isin([2024, 2025])].copy()
    if data.empty:
        raise ValueError("No 2024 or 2025 records found. Check the A1 CSV.")

    monthly = collisions_by_month(data)
    hourly = collisions_by_hour(data)
    weekday = collisions_by_weekday(data)
    yearly = collisions_by_year(data)

    print("Selected records:", len(data))
    print("\nCount checks:\n", verify_group_totals(data).to_string(index=False))
    for title, table in [("Monthly", monthly), ("Hourly", hourly), ("Weekday", weekday), ("Yearly", yearly)]:
        print(f"\n{title}:\n{table.to_string(index=False)}")
    print("\nFindings:")
    for finding in key_findings(data):
        print(finding)
    print("\nSaved plot:", plot_monthly_comparison(monthly))
