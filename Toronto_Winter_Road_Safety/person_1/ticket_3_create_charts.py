"""Ticket A3: create the monthly, hourly and weekday charts."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ticket_A1 import MONTHS

PERSON_DIR = Path(__file__).resolve().parent
YEARS = [2024, 2025]
from ticket_2_analyze_patterns import (
    collisions_by_month, collisions_by_hour, collisions_by_weekday,
    verify_group_totals,
)


def save_chart(fig, ax, filename, df, column):
    """Add chart information and save the figure."""

    ax.grid(axis="y", alpha=0.2)
    ax.set_ylim(bottom=0)
    ax.set_axisbelow(True)

    usable = df[column].notna().sum()
    missing = len(df) - usable

    fig.subplots_adjust(bottom=0.25)

    fig.text(
        0.1, 0.08,
        f"2024-2025 | {usable:,} usable records | "
        f"{missing:,} missing/invalid values excluded.\n"
        "Reported collision counts; no adjustment for traffic volume.",
        fontsize=9
    )

    fig.text(
        0.1, 0.03,
        "Source: Toronto Police Service | Public Safety Data Portal",
        fontsize=9
    )

    fig.savefig(
        filename,
        dpi=180,
        metadata={
            "Source": "https://data.torontopolice.on.ca/"
        }
    )

    plt.close(fig)
    return filename


def save_temporal_charts(df, output_dir=PERSON_DIR):

    verify_group_totals(df)

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {}

    # Chart 1: Monthly collisions (2024 vs 2025)
    monthly = collisions_by_month(df)

    fig, ax = plt.subplots(figsize=(11, 6))

    for year in YEARS:
        data = monthly[monthly["OCC_YEAR"] == year]

        ax.plot(
            np.arange(12),
            data["collisions"],
            marker="o",
            label=str(year)
        )

    ax.set_xticks(np.arange(12), [m[:3] for m in MONTHS])
    ax.set_title("Toronto collisions by month: 2024 and 2025")
    ax.set_xlabel("Recorded calendar month")
    ax.set_ylabel("Reported collision records")
    ax.legend()

    paths["monthly"] = save_chart(
        fig, ax,
        output_dir / "monthly_collisions_2024_vs_2025.png",
        df, "OCC_MONTH"
    )

    # Chart 2: Hourly collisions
    hourly = collisions_by_hour(df)

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(
        hourly["OCC_HOUR"],
        hourly["collisions"]
    )

    ax.set_xticks(np.arange(24))
    ax.set_title("Toronto collisions by hour: 2024-2025 combined")
    ax.set_xlabel("Recorded occurrence hour (00-23)")
    ax.set_ylabel("Reported collision records")

    paths["hourly"] = save_chart(
        fig, ax,
        output_dir / "hourly_collisions_2024_2025.png",
        df, "OCC_HOUR"
    )

    # Chart 3: Weekday collisions
    weekdays = collisions_by_weekday(df)

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(
        weekdays["OCC_DOW"],
        weekdays["collisions"]
    )

    ax.set_title("Toronto collisions by weekday: 2024-2025 combined")
    ax.set_xlabel("Recorded day of week")
    ax.set_ylabel("Reported collision records")

    paths["weekday"] = save_chart(
        fig, ax,
        output_dir / "weekday_collisions_2024_2025.png",
        df, "OCC_DOW"
    )

    return paths


def main():
    df = pd.read_csv(PERSON_DIR / "ticket_A1_prepared_data.csv",
                     dtype={"OCC_YEAR": "Int64", "OCC_HOUR": "Int64"})
    df = df[df["OCC_YEAR"].isin(YEARS)].copy()
    if df.empty:
        raise ValueError("No 2024 or 2025 records found. Run ticket_A1.py first.")

    charts = save_temporal_charts(df)

    for name, path in charts.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
