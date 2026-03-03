"""
Negative VAT (Invalid Numeric) Scenario — Data Cleaning Script 04

Purpose:
    Demonstrates handling of invalid numeric values where VAT_Paid is negative.
    VAT paid should be non-negative; negative values are data errors. This script
    coerces VAT_Paid to numeric, identifies negative values, and drops those rows
    (same strategy as the integrated exercise).

Scenario: Invalid numeric values (e.g. negative VAT_Paid).

Input:  kra_dirty_data.csv (current working directory)
Output: kra_after_vat_validation.csv  — dataset with negative-VAT rows removed
        negative_vat_report.txt        — count of negative-VAT rows and before/after counts

Run:    python 04_negative_vat.py
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Load the raw dataset
# ---------------------------------------------------------------------------
INPUT_FILE = "kra_dirty_data.csv"
OUTPUT_CSV = "kra_after_vat_validation.csv"
OUTPUT_REPORT = "negative_vat_report.txt"

df = pd.read_csv(INPUT_FILE)
rows_before = len(df)

# ---------------------------------------------------------------------------
# Coerce VAT_Paid to numeric
# ---------------------------------------------------------------------------
# VAT_Paid may be stored as text or have invalid values; coerce to numeric
# so that non-numeric entries become NaN and we can reliably compare with 0.
df["VAT_Paid"] = pd.to_numeric(df["VAT_Paid"], errors="coerce")

# ---------------------------------------------------------------------------
# Identify and count rows with negative VAT
# ---------------------------------------------------------------------------
# Rows with VAT_Paid < 0 are invalid for analysis; we record how many before dropping.
negative_mask = df["VAT_Paid"] < 0
num_negative = negative_mask.sum()

# ---------------------------------------------------------------------------
# Set negative VAT to None and drop those rows
# ---------------------------------------------------------------------------
# Setting to None (NaN) then dropna(subset=['VAT_Paid']) removes both
# originally missing and negative-VAT rows in one step.
df.loc[negative_mask, "VAT_Paid"] = None
df_clean = df.dropna(subset=["VAT_Paid"])
rows_after = len(df_clean)
rows_dropped = rows_before - rows_after

# ---------------------------------------------------------------------------
# Write report and cleaned dataset
# ---------------------------------------------------------------------------
report_lines = [
    "Negative VAT Scenario — Report",
    "==============================",
    "",
    f"Input file: {INPUT_FILE}",
    f"Rows before cleaning:     {rows_before}",
    f"Rows with negative VAT:   {num_negative}",
    f"Rows after cleaning:     {rows_after}",
    f"Rows dropped:            {rows_dropped}",
    "",
    "Note: Rows with VAT_Paid < 0 were set to missing and then dropped.",
]

with open(OUTPUT_REPORT, "w") as f:
    f.write("\n".join(report_lines))

df_clean.to_csv(OUTPUT_CSV, index=False)

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print(f"Rows with negative VAT: {num_negative}")
print(f"Rows before: {rows_before}, after: {rows_after}, dropped: {rows_dropped}")
print(f"Cleaned dataset saved as '{OUTPUT_CSV}'.")
print(f"Report saved as '{OUTPUT_REPORT}'.")
