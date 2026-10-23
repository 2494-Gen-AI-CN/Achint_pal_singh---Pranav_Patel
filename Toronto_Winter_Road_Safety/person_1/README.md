# Person 1: Toronto collision patterns over time

This folder implements tickets **A1-A4** from the independent tickets PDF.
It answers: **when were Toronto Police collision records reported most frequently
in 2024 and 2025?** It runs without any Person 2 code or results.

## Start here

1. A1: `ticket_1_prepare_data.py` loads the CSV and checks the time fields.
2. A2: `ticket_2_analyze_patterns.py` calculates counts and findings.
3. A3: `ticket_3_create_charts.py` saves the three charts.
4. A4: `ticket_4_temporal_report.ipynb` presents the tables, charts and findings.

Run them in ticket order. A2 uses A1's loader, A3 uses A1 and A2,
and the A4 notebook brings the three scripts together. They remain independent
of Person 2's work.

## How to explain the code

- **A1 - load and prepare:** `read_csv` loads four columns. `isin` keeps 2024
  and 2025. Calendar categories put months and weekdays in order. Hours outside
  the whole numbers 0-23 become missing. The original file stays unchanged.
- **A2 - count:** `value_counts` counts records in each month, hour or weekday.
  `reindex` puts those counts in calendar order and includes any empty bins.
  Monthly analysis repeats the same steps once for each year.
- **Check the totals:** the grouped counts must add up to the records with a
  valid value for that particular time field.
- **A3 - plot:** `plot` draws one monthly line per year. `bar` draws the hourly
  and weekday charts. `save_chart` adds the common labels and saves each PNG.
- **A4 - report:** the notebook calls these functions and displays their results.
  Its finding sentences are calculated from the data rather than typed-in totals.

`df.attrs["inspection"]` is a dictionary attached to the DataFrame. It stores
the row counts and missing-value checks for the report; it does not add data rows.
The `if __name__ == "__main__"` block runs the command-line part only when you
run that file directly, so importing functions into the notebook does not run it.

## Source CSV

Use the original full dataset supplied for this project:

`../data/raw/collisions/Traffic Collisions - 4326 (1).csv`

That path is relative to this folder. The loader resolves its default path from
the script's location, so the command can run from a different working directory.
For a differently named or relocated file, pass `--csv "C:\path\to\your.csv"`.
In the notebook, change `CSV_PATH` in the setup cell.

Source: [Toronto Police Service Motor Vehicle Collisions](https://data.torontopolice.on.ca/datasets/bc4c72a793014a55a674984ef175a6f3_0/explore).
The supplied CSV is the local input; do not substitute the old Q1-only export.
Both collaborators obtain their own copy, and raw data is excluded by the
project-level `.gitignore`. No raw CSV is overwritten or exported by these scripts.

Verified baseline for this file:

| Coverage | Records |
| --- | ---: |
| Entire original CSV | 825,265 |
| 2024 | 70,181 |
| 2025 | 67,546 |
| Selected total | 137,727 |

These are snapshot checks, not constants used to manufacture summary values.
The loader prints a notice if another source snapshot has different totals.

## Setup and commands (Windows PowerShell)

Open a terminal in `Toronto_Winter_Road_Safety/person_1`.
Use Python 3.12 for the verified project environment. An environment is already installed here on this machine.
On another machine, create it first:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name toronto-winter-person1 --display-name "Toronto Winter Road Safety (person_1)"
```

Run A1 to inspect and prepare the data:

```powershell
.\.venv\Scripts\python.exe ticket_1_prepare_data.py
```

Run A2 for the reconciliations, summaries and findings:

```powershell
.\.venv\Scripts\python.exe ticket_2_analyze_patterns.py
```

Save all three charts:

```powershell
.\.venv\Scripts\python.exe ticket_3_create_charts.py
```

Open the notebook using this environment:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab ticket_4_temporal_report.ipynb
```

Choose **Toronto Winter Road Safety (person_1)** in the notebook's **Select Kernel**
menu, then **Restart Kernel and Run All**. In VS Code, use **Python: Select
Interpreter** and choose `person_1/.venv/Scripts/python.exe` for running `.py` files.
If VS Code already remembered another interpreter, select this one explicitly;
the workspace default only applies when no interpreter has been selected.
An error such as `No module named 'pandas'` or `No module named 'matplotlib'`
usually means the notebook or script is running under another Python installation.
The notebook imports only the three Person 1 modules, creates its own data frame,
checks all totals, regenerates the three PNGs and displays the resulting findings.
It works with the notebook launched from the project root or this folder.

Run the checks:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

`requirements.txt` gives supported dependency ranges. `requirements-lock.txt`
records the exact installed environment used for the delivered run.

## Data rules and assumptions

- Select `OCC_YEAR` 2024 and 2025; load only `OCC_YEAR`, `OCC_MONTH`, `OCC_DOW`
  and `OCC_HOUR` for this independent workstream.
- Use the source calendar labels and occurrence hour directly. `OCC_DATE` in this
  full CSV uses Unix milliseconds, but its timestamp is not the occurrence-hour
  field. This workflow does not derive hour or weekday from that timestamp.
- Order months January-December and weekdays Monday-Sunday. Hours must be integers
  from 0 through 23.
- Strip surrounding whitespace from month and weekday labels in memory. Treat
  unknown labels, missing values, fractional hours and out-of-range hours as
  missing for that field. Print their counts; never silently discard a whole row.
- Each grouping omits only records without a usable value for that grouping.
  Its sum must equal the number of eligible records. Include all calendar bins,
  showing zero where no eligible record was counted for a bin.
- Keep records with unknown locations or zero coordinates: location is not a
  filter for citywide temporal counts.
- Count rows as published collision records. Only the four specified temporal
  columns are loaded, so this workflow does not independently deduplicate events.
- Monthly curves compare the years separately. Hourly and weekday bars pool both
  years. Highest-count findings include ties.

## Limits of the conclusions

Counts measure recorded frequency, not individual crash risk. Traffic volumes,
distance travelled and road-user exposure are absent. Months have different
lengths, 2024 is a leap year, and weekday frequencies differ slightly across
calendar years; plots show raw counts, not per-day or per-vehicle rates.
The CSV has no snowfall or crash-cause field. No weather attribution, route
recommendation, machine learning or mapping is included. Unknown locations remain
in temporal totals, so these are totals for the publisher's records, not a new
geographic validation of every occurrence. Reporting practices and data revisions
can affect comparisons.

## Deliverables

- `ticket_1_prepare_data.py`: A1 loading, preparation and inspection.
- `ticket_2_analyze_patterns.py`: A2 summary functions and findings.
- `ticket_3_create_charts.py`: A3 chart generation.
- `figures/monthly_collisions_2024_vs_2025.png`
- `figures/hourly_collisions_2024_2025.png`
- `figures/weekday_collisions_2024_2025.png`
- `ticket_4_temporal_report.ipynb`: A4 standalone report with computed findings.
- `tests/test_tickets.py`: validation and reconciliation checks.

Before presenting, review the year filter, calendar ordering, grouping totals,
missing-data handling, and limitations of collision counts.
