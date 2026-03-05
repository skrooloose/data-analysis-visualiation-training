import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker()

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

rows = 300
data = []

sectors = ["Retail", "Manufacturing", "Services", "Agriculture"]
regions = ["Nairobi", "Mombasa", "Kisumu", "Nakuru","Eldort"]
risk_levels = ["Low", "Medium", "High"]

for i in range(rows):
    # Introduce 30% clean rows
    if i < 90:  # clean rows
        taxpayer_name = fake.company()
        taxpayer_pin = fake.bothify(text="P########")
        filing_date = fake.date_between(start_date="-1y", end_date="today")
        vat_paid = round(random.uniform(1000, 50000), 2)
        sector = random.choice(sectors)
        region = random.choice(regions)
        risk_level = random.choice(risk_levels)
    else:  # dirty rows
        # Randomly introduce missing values
        taxpayer_name = fake.company() if random.random() > 0.05 else None
        taxpayer_pin = fake.bothify(text="P########") if random.random() > 0.1 else None
        filing_date = (fake.date_between(start_date="-1y", end_date="today").strftime("%Y-%m-%d")
                       if random.random() > 0.1 else "invalid_date")
        # VAT_Paid sometimes numeric, sometimes text, sometimes negative
        if random.random() < 0.1:
            vat_paid = -round(random.uniform(100, 1000), 2)
        elif random.random() < 0.2:
            vat_paid = str(round(random.uniform(1000, 50000), 2))
        else:
            vat_paid = round(random.uniform(1000, 50000), 2)
        sector = random.choice(sectors).lower() if random.random() < 0.2 else random.choice(sectors)
        region = random.choice(regions).upper() if random.random() < 0.15 else random.choice(regions)
        risk_level = random.choice(risk_levels) if random.random() > 0.3 else None

    data.append([taxpayer_name, taxpayer_pin, filing_date, vat_paid, sector, region, risk_level])

# Introduce duplicates (5 exact, 5 partial)
for _ in range(10):
    row = random.choice(data)
    data.append(row)  # exact duplicate

for _ in range(20):
    row = random.choice(data)
    # partial duplicate with different formatting
    new_row = [row[0].upper(), row[1], row[2], row[3], row[4].upper(), row[5], row[6]]
    data.append(new_row)

columns = ["Taxpayer_Name", "Taxpayer_PIN", "Filing_Date", "VAT_Paid", "Sector", "Region", "Risk_Level"]
df = pd.DataFrame(data, columns=columns)

# Save as CSV for practical exercises
df.to_csv("kra_dirty_data.csv", index=False)
print("Sample dirty dataset saved as 'kra_dirty_data.csv'.")