import pandas as pd

# Load the dirty dataset
df = pd.read_csv("kra_dirty_data.csv")

# 1. Detect Missing Values
print("Missing values per column:")
print(df.isnull().sum())

# Handling missing values
# Strategy:
# - Critical fields (VAT_Paid, Taxpayer_PIN, Risk_Level) -> remove or flag
# - Optional fields -> impute or leave
df['VAT_Paid'] = pd.to_numeric(df['VAT_Paid'], errors='coerce')  # Convert numeric fields
df['Filing_Date'] = pd.to_datetime(df['Filing_Date'], errors='coerce')  # Convert dates

# Remove rows with critical missing data
df_clean = df.dropna(subset=['VAT_Paid', 'Taxpayer_PIN', 'Risk_Level'])

# 2. Detect Duplicates
print("\nDuplicate rows count:", df_clean.duplicated().sum())
df_clean = df_clean.drop_duplicates()  # Remove exact duplicates

# 3. Standardize Inconsistent Fields
# Remove leading/trailing spaces and unify capitalization
df_clean['Region'] = df_clean['Region'].str.strip().str.title()
df_clean['Sector'] = df_clean['Sector'].str.strip().str.title()
df_clean['Taxpayer_Name'] = df_clean['Taxpayer_Name'].str.strip().str.title()

# 4. Handle Negative VAT values
# Set negative VAT_Paid to NaN for review
df_clean.loc[df_clean['VAT_Paid'] < 0, 'VAT_Paid'] = None
# Optionally, drop rows with negative VAT or impute
df_clean = df_clean.dropna(subset=['VAT_Paid'])

# Validate cleaned dataset
print("\nData types after cleaning:")
print(df_clean.dtypes)
print("\nSummary statistics:")
print(df_clean.describe())

# Save cleaned dataset
df_clean.to_csv("kra_clean_data.csv", index=False)
print("\nClean dataset saved as 'kra_clean_data.csv'.")