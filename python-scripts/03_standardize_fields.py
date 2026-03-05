"""
Standardize Inconsistent Fields Scenario — Data Cleaning Script 03

Purpose:
    Demonstrates normalization of text fields that have inconsistent casing or
    extra whitespace (e.g. "NAIROBI" vs "Nairobi", "  Retail  " vs "Retail").
    Standardization makes grouping and filtering reliable and improves readability.

Scenario: Inconsistent fields (mixed case, leading/trailing spaces).

Input:  kra_dirty_data.csv (current working directory)
Output: kra_after_standardization.csv  — dataset with Region, Sector, Taxpayer_Name standardized
        standardization_report.txt    — columns standardized; no rows removed

Run:    python 03_standardize_fields.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load the raw dataset
# ---------------------------------------------------------------------------
INPUT_FILE = "kra_dirty_data.csv"
OUTPUT_CSV = "kra_after_standardization.csv"
OUTPUT_REPORT = "standardization_report.txt"

# Columns to standardize: strip whitespace and apply title case for consistency.
COLUMNS_TO_STANDARDIZE = ["Region", "Sector", "Taxpayer_Name"]

df = pd.read_csv(INPUT_FILE)
rows_before = len(df)

# ---------------------------------------------------------------------------
# Standardize text: strip and title-case
# ---------------------------------------------------------------------------
# str.strip() removes leading/trailing spaces; str.title() normalizes casing.
# NaN values are preserved (str accessor returns NaN for missing values).
for col in COLUMNS_TO_STANDARDIZE:
    if col in df.columns:
        df[col] = df[col].str.strip().str.upper()

# No rows are dropped in this scenario; we only transform values.
df_clean = df
rows_after = len(df_clean)

# ---------------------------------------------------------------------------
# Write report and cleaned dataset
# ---------------------------------------------------------------------------
report_lines = [
    "Standardization Scenario — Report",
    "==================================",
    "",
    f"Input file: {INPUT_FILE}",
    f"Rows before: {rows_before}",
    f"Rows after:  {rows_after} (no rows removed)",
    "",
    f"Columns standardized (strip + title case): {COLUMNS_TO_STANDARDIZE}",
    "",
    "This script only normalizes text; it does not drop rows.",
]

with open(OUTPUT_REPORT, "w") as f:
    f.write("\n".join(report_lines))

df_clean.to_csv(OUTPUT_CSV, index=False)

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print("Columns standardized: Region, Sector, Taxpayer_Name (strip + title case)")
print(f"Rows: {rows_before} (unchanged)")
print(f"Cleaned dataset saved as '{OUTPUT_CSV}'.")
print(f"Report saved as '{OUTPUT_REPORT}'.")
