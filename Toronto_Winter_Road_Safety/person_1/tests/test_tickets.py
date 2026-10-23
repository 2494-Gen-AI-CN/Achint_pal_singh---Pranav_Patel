"""Checks for missing data, chronological ordering and count reconciliation.

Small temporary CSVs exercise error cases; they are test fixtures, not project data.
"""

from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ticket_1_prepare_data import (
    DEFAULT_CSV, MONTHS, REFERENCE_COUNTS, WEEKDAYS, load_temporal_data,
)
from ticket_2_analyze_patterns import (
    collisions_by_hour, collisions_by_month, collisions_by_weekday,
    key_findings, verify_group_totals,
)


@pytest.fixture
def example_csv(tmp_path):
    """Deliberately mix order, years, missing fields and invalid hours."""
    frame = pd.DataFrame({
        "OCC_YEAR": [2025, 2024, 2024, 2025, 2024, 2024, 2023, 2026],
        "OCC_MONTH": ["March", "January", "December", "Bad month", "February", "June", "January", "January"],
        "OCC_DOW": ["Sunday", "Monday", "Friday", "Tuesday", None, "Saturday", "Monday", "Monday"],
        "OCC_HOUR": [23, 0, 25, 8.5, -1, None, 12, 12],
    })
    path = tmp_path / "validation_fixture.csv"
    frame.to_csv(path, index=False)
    return path


def test_loader_retains_rows_and_reports_invalid_fields(example_csv):
    before = example_csv.read_bytes()
    df = load_temporal_data(example_csv)
    assert len(df) == 6
    assert df.attrs["inspection"]["missing_or_invalid"] == {
        "OCC_MONTH": 1, "OCC_HOUR": 4, "OCC_DOW": 1,
    }
    assert df["OCC_HOUR"].dropna().tolist() == [23, 0]
    assert df["OCC_MONTH"].cat.categories.tolist() == MONTHS
    assert df["OCC_DOW"].cat.categories.tolist() == WEEKDAYS
    assert df.attrs["inspection"]["rows_by_year"] == {2024: 4, 2025: 2}
    assert example_csv.read_bytes() == before


def test_order_zero_bins_and_group_specific_exclusions(example_csv):
    df = load_temporal_data(example_csv)
    original = df.copy(deep=True)
    monthly = collisions_by_month(df)
    hourly = collisions_by_hour(df)
    weekdays = collisions_by_weekday(df)
    assert monthly["OCC_YEAR"].tolist() == [2024] * 12 + [2025] * 12
    assert monthly["OCC_MONTH"].tolist() == MONTHS * 2
    assert monthly["collisions"].sum() == 5
    assert monthly.loc[monthly["OCC_MONTH"].eq("April"), "collisions"].sum() == 0
    assert hourly["OCC_HOUR"].tolist() == list(range(24))
    assert hourly["collisions"].sum() == 2
    assert weekdays["OCC_DOW"].tolist() == WEEKDAYS
    assert weekdays["collisions"].sum() == 5
    checks = verify_group_totals(df).set_index("grouping")
    assert checks["excluded_records"].to_dict() == {"Month": 1, "Hour": 4, "Weekday": 1}
    pd.testing.assert_frame_equal(df, original)


def test_findings_report_ties(example_csv):
    df = load_temporal_data(example_csv)
    findings = key_findings(df)
    assert "00:00-00:59" in findings[2]
    assert "23:00-23:59" in findings[2]


def test_empty_period_is_explicit_error(tmp_path):
    path = tmp_path / "wrong_period.csv"
    pd.DataFrame({
        "OCC_YEAR": [2023], "OCC_MONTH": ["January"],
        "OCC_DOW": ["Monday"], "OCC_HOUR": [12],
    }).to_csv(path, index=False)
    with pytest.raises(ValueError, match="no records for 2024 or 2025"):
        load_temporal_data(path)


def test_missing_column_is_explicit_error(tmp_path):
    path = tmp_path / "missing_column.csv"
    pd.DataFrame({"OCC_YEAR": [2024]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Usecols"):
        load_temporal_data(path)


@pytest.mark.skipif(not DEFAULT_CSV.exists(), reason="Original local CSV not downloaded")
def test_real_source_totals_reconcile():
    df = load_temporal_data()
    assert df.attrs["inspection"]["rows_by_year"] == REFERENCE_COUNTS
    assert len(df) == 137727
    checks = verify_group_totals(df)
    assert checks["excluded_records"].eq(0).all()
    assert checks["grouped_total"].eq(len(df)).all()
    monthly = collisions_by_month(df)
    assert monthly.groupby("OCC_YEAR")["collisions"].sum().to_dict() == REFERENCE_COUNTS
