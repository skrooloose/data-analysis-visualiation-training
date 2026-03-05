"""
Missing Values Scenario — Data Cleaning Script 01

Purpose:
    Demonstrates detection and handling of missing values in the KRA dirty dataset.
    Missing data can bias analysis and break aggregations; this script identifies
    missing values, coerces types so invalid entries become NaN, and drops rows
    where critical fields (VAT_Paid, Taxpayer_PIN, Risk_Level) are missing.

Scenario: Missing values (nulls, empty, or invalid types that should be numeric/dates).

Input:  kra_dirty_data.csv (current working directory)
Output: kra_after_missing_values.csv  — dataset after removing rows with critical missing data
        missing_values_report.txt     — before/after counts and missing counts per column

Run:    python 01_missing_values.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load the raw dataset
# ---------------------------------------------------------------------------
# We need the dirty data as-is first to measure missingness before any cleaning.
INPUT_FILE = "kra_dirty_data.csv"
OUTPUT_CSV = "kra_after_missing_values.csv"
OUTPUT_REPORT = "missing_values_report.txt"

df = pd.read_csv(INPUT_FILE)
rows_before = len(df)

# ---------------------------------------------------------------------------
# Detect missing values (before type coercion)
# ---------------------------------------------------------------------------
# Count nulls per column. In CSV, empty cells and some invalid values may not
# be read as NaN until we coerce types; we report raw null count first.
missing_before = df.isnull().sum()

# ---------------------------------------------------------------------------
# Coerce types so invalid values become NaN
# ---------------------------------------------------------------------------
# VAT_Paid might be stored as text or have non-numeric values; coercing to
# numeric turns them into NaN for consistent handling. Same for dates.
df["VAT_Paid"] = pd.to_numeric(df["VAT_Paid"], errors="coerce")
df["Filing_Date"] = pd.to_datetime(df["Filing_Date"], errors="coerce")

# Re-count missing after coercion (includes newly created NaNs from bad values).
missing_after_coerce = df.isnull().sum()

# ---------------------------------------------------------------------------
# Drop rows with critical missing data
# ---------------------------------------------------------------------------
# Rows missing VAT_Paid, Taxpayer_PIN, or Risk_Level are not usable for
# downstream analysis (e.g. risk or revenue), so we remove them rather than impute.
CRITICAL_COLUMNS = ["VAT_Paid", "Taxpayer_PIN", "Risk_Level"]
df_clean = df.dropna(subset=CRITICAL_COLUMNS)
rows_after = len(df_clean)
rows_dropped = rows_before - rows_after

# ---------------------------------------------------------------------------
# Write report and cleaned dataset
# ---------------------------------------------------------------------------
report_lines = [
    "Missing Values Scenario — Report",
    "==================================",
    "",
    f"Input file: {INPUT_FILE}",
    f"Rows before cleaning: {rows_before}",
    f"Rows after cleaning:  {rows_after}",
    f"Rows dropped:         {rows_dropped}",
    "",
    "Missing counts per column (before type coercion):",
]
for col in df.columns:
    report_lines.append(f"  {col}: {missing_before.get(col, 0)}")
report_lines.extend([
    "",
    "Missing counts per column (after coercing VAT_Paid and Filing_Date to numeric/datetime):",
])
for col in df.columns:
    report_lines.append(f"  {col}: {missing_after_coerce.get(col, 0)}")
report_lines.extend([
    "",
    f"Critical columns used for dropna: {CRITICAL_COLUMNS}",
])

with open(OUTPUT_REPORT, "w") as f:
    f.write("\n".join(report_lines))

df_clean.to_csv(OUTPUT_CSV, index=False)

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print("Missing values per column (before cleaning):")
print(missing_before)
print(f"\nRows before: {rows_before}, after: {rows_after}, dropped: {rows_dropped}")
print(f"Cleaned dataset saved as '{OUTPUT_CSV}'.")
print(f"Report saved as '{OUTPUT_REPORT}'.")
