"""
Duplicates Scenario — Data Cleaning Script 02

Purpose:
    Demonstrates detection and removal of exact duplicate rows in the KRA dirty dataset.
    Duplicates can inflate counts and distort aggregations; this script counts
    full-row duplicates and removes them so each record is unique.

Scenario: Duplicate rows (identical values in every column).

Input:  kra_dirty_data.csv (current working directory)
Output: kra_after_deduplication.csv  — dataset after removing exact duplicates
        duplicates_report.txt         — duplicate count and before/after row counts

Run:    python 02_duplicates.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load the raw dataset
# ---------------------------------------------------------------------------
INPUT_FILE = "kra_dirty_data.csv"
OUTPUT_CSV = "kra_after_deduplication.csv"
OUTPUT_REPORT = "duplicates_report.txt"

df = pd.read_csv(INPUT_FILE)
rows_before = len(df)

# ---------------------------------------------------------------------------
# Detect exact duplicate rows
# ---------------------------------------------------------------------------
# duplicated() marks every occurrence of a duplicate row as True except the
# first; sum() gives the number of duplicate rows (rows we will remove).
num_duplicates = df.duplicated().sum()

# ---------------------------------------------------------------------------
# Remove exact duplicates
# ---------------------------------------------------------------------------
# drop_duplicates() keeps the first occurrence of each unique row and drops
# the rest. No subset is used, so we compare all columns.
df_clean = df.drop_duplicates()
rows_after = len(df_clean)

# ---------------------------------------------------------------------------
# Write report and cleaned dataset
# ---------------------------------------------------------------------------
report_lines = [
    "Duplicates Scenario — Report",
    "============================",
    "",
    f"Input file: {INPUT_FILE}",
    f"Rows before deduplication: {rows_before}",
    f"Duplicate rows found:       {num_duplicates}",
    f"Rows after deduplication:   {rows_after}",
    "",
    "Note: Only exact full-row duplicates were removed (all columns identical).",
]

with open(OUTPUT_REPORT, "w") as f:
    f.write("\n".join(report_lines))

df_clean.to_csv(OUTPUT_CSV, index=False)

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print(f"Duplicate rows count: {num_duplicates}")
print(f"Rows before: {rows_before}, after: {rows_after}")
print(f"Cleaned dataset saved as '{OUTPUT_CSV}'.")
print(f"Report saved as '{OUTPUT_REPORT}'.")
