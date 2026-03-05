#Simulating Synthetic KRA-Style Dataset (10,000+ records)
#The following code can be used to generates 12 months × ~900 taxpayers ≈ 10,800 rows (you can scale up). It produces realistic fields for revenue, tax due/paid, late filing, penalties, audits, plus sector/region/segment.
# ============================================================
# KRA-STYLE SYNTHETIC DATASET GENERATOR (10,000+ rows)
# ============================================================

# You will need specific packages to generate the day. The following packages are necessary tidyverse, lubridate, janitor.
#yes
#The necessary packages should be loaded before using them. The code below can be used to load the packages

library(tidyverse)
library(lubridate)
library(janitor)
library(dplyr)
library(scales)


set.seed(42)
# set.seed(42) is used to make random number generation reproducible. Setting a seed fixes the starting point of the random number generator so that the same sequence of random numbers is produced each time the code is executed.
# ---------------------------
# A) Configure size
# ---------------------------
n_taxpayers <- 900              # Increase to 2000+ if you want much larger
months <- seq.Date(as.Date("2025-01-01"), as.Date("2025-12-01"), by = "month")

# ---------------------------
# B) Create taxpayer master table
# ---------------------------
sectors <- c("Retail","Manufacturing","Hospitality","Transport","ICT","Professional Services",
             "Agriculture","Real Estate","Wholesale","Health","Education","Construction")

regions <- c("Nairobi","Central","Coast","Rift Valley","Western","Nyanza","Eastern","North Eastern")

segments <- c("SME","Corporate","Individual")

taxpayers <- tibble(
  PIN = sprintf("P%07d", 1:n_taxpayers),
  Sector = sample(sectors, n_taxpayers, replace = TRUE,
                  prob = c(0.15,0.08,0.08,0.07,0.08,0.07,0.08,0.08,0.10,0.07,0.06,0.06)),
  Region = sample(regions, n_taxpayers, replace = TRUE,
                  prob = c(0.22,0.12,0.10,0.18,0.10,0.10,0.12,0.06)),
  Segment = sample(segments, n_taxpayers, replace = TRUE, prob = c(0.55,0.25,0.20)),
  IndustryRisk = sample(1:5, n_taxpayers, replace = TRUE, prob = c(0.10,0.20,0.30,0.25,0.15))
)

# Sector baseline revenue multipliers
sector_mult <- tibble(
  Sector = sectors,
  base_mult = c(1.0,2.2,1.3,1.4,1.8,1.7,1.1,2.0,1.6,1.4,1.2,1.9)
)

# Segment baseline revenue multipliers
segment_mult <- tibble(
  Segment = segments,
  seg_mult = c(1.0, 3.2, 0.5)
)

# ---------------------------
# C) Create monthly filings dataset
# ---------------------------
df <- expand_grid(PIN = taxpayers$PIN, FilingMonth = months) |>
  left_join(taxpayers, by = "PIN") |>
  left_join(sector_mult, by = "Sector") |>
  left_join(segment_mult, by = "Segment") |>
  mutate(
    # Seasonality: peaks around Mar/Jun/Sep/Dec (VAT/quarterly-like effects)
    season = 1 + 0.10*sin(2*pi*month(FilingMonth)/12) + 0.08*(month(FilingMonth) %in% c(3,6,9,12)),
    # Base revenue by segment & sector
    Revenue = round(rlnorm(n(), meanlog = log(450000 * base_mult * seg_mult * season), sdlog = 0.55)),
    # Tax due proxy (e.g., VAT-ish rate + noise)
    TaxDue = round(Revenue * runif(n(), 0.13, 0.17)),
    # Late filing probability higher for higher risk + SMEs
    p_late = pmin(0.75, 0.08 + 0.06*(IndustryRisk - 1) + if_else(Segment=="SME", 0.06, 0) + if_else(Region=="North Eastern",0.05,0)),
    LateFiling = rbinom(n(), 1, p_late),
    # Payment behavior: some underpay especially if late/high risk
    pay_ratio = pmax(0, pmin(1, rnorm(n(), mean = 0.92 - 0.12*LateFiling - 0.05*(IndustryRisk-1), sd = 0.12))),
    TaxPaid = round(TaxDue * pay_ratio),
    ComplianceGap = TaxDue - TaxPaid,
    # Penalty if late (simple proxy)
    Penalty = if_else(LateFiling==1, round(TaxDue * runif(n(), 0.02, 0.07)), 0),
    # Audit flag likelihood increases with gap + risk + late
    audit_score = 0.10*(IndustryRisk) + 0.000002*pmax(ComplianceGap,0) + 0.25*LateFiling,
    AuditFlag = rbinom(n(), 1, pmin(0.60, audit_score))
  ) |>
  select(PIN, Sector, Region, Segment, IndustryRisk, FilingMonth, Revenue, TaxDue, TaxPaid, ComplianceGap, Penalty, LateFiling, AuditFlag) |>
  clean_names()

# Ensure >10,000 rows
nrow(df)
# write out
write_csv(df, "KRA_Synthetic_Filings_2025.csv")

#NOTE: Output file: KRA_Synthetic_Filings_2025.csv (created in your working directory)


#R Code for conducting EDA on the KRA Dataset

#1.	Load Dataset + Quick Overview
library(tidyverse)
library(lubridate)
library(janitor)

kra <- read_csv("KRA_Synthetic_Filings_2025.csv") |> clean_names()

# Quick structure check
glimpse(kra)

# Basic sanity checks
kra |> summarise(
  rows = n(),
  taxpayers = n_distinct(pin),
  months = n_distinct(filing_month),
  late_rate = mean(late_filing),
  avg_gap = mean(compliance_gap)
)

#2.	Statistical Summarization — Mean, Median, Mode, Variance
# Mean/Median/Variance for revenue and taxpaid
kra |> summarise(
  mean_revenue = mean(revenue),
  median_revenue = median(revenue),
  var_revenue = var(revenue),
  mean_taxpaid = mean(tax_paid),
  median_taxpaid = median(tax_paid),
  var_taxpaid = var(tax_paid)
)

# MODE helper (most frequent value)
get_mode <- function(x){
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

# Mode examples
get_mode(kra$sector)   # most common sector
get_mode(kra$region)   # most common region

# Sector-level summaries (useful for KRA decisions)
kra |> group_by(sector) |>
  summarise(
    taxpayers = n_distinct(pin),
    mean_revenue = mean(revenue),
    median_revenue = median(revenue),
    var_revenue = var(revenue),
    mean_late_rate = mean(late_filing),
    mean_gap = mean(compliance_gap),
    .groups = "drop"
  ) |>
  arrange(desc(mean_gap))

#3.	Identifying Trends (Time Series)
# Monthly revenue trend overall
kra_monthly <- kra |>
  group_by(filing_month) |>
  summarise(
    total_revenue = sum(revenue),
    total_taxpaid = sum(tax_paid),
    late_rate = mean(late_filing),
    avg_gap = mean(compliance_gap),
    .groups = "drop"
  )

# Plot trends
ggplot(kra_monthly, aes(x = filing_month, y = total_taxpaid)) +
  geom_line() +
  geom_point() +
  labs(title = "Monthly Tax Paid Trend (KRA Synthetic)", x = "Month", y = "Total Tax Paid")

ggplot(kra_monthly, aes(x = filing_month, y = late_rate)) +
  geom_line() +
  geom_point() +
  scale_y_continuous(labels = comma) +  # <- converts 5.0e+06 to 5,000,000
  
  labs(title = "Monthly Late Filing Rate Trend", x = "Month", y = "Late Filing Rate")

#4.	Patterns (Sector/Region Comparisons)
# Sector patterns: late filing and compliance gap
sector_pattern <- kra |>
  group_by(sector) |>
  summarise(
    late_rate = mean(late_filing),
    avg_gap = mean(compliance_gap),
    avg_revenue = mean(revenue),
    .groups="drop"
  ) |>
  arrange(desc(late_rate))

sector_pattern

# Region patterns
region_pattern <- kra |>
  group_by(region) |>
  summarise(
    late_rate = mean(late_filing),
    avg_gap = mean(compliance_gap),
    total_taxpaid = sum(tax_paid),
    .groups="drop"
  ) |>
  arrange(desc(avg_gap))

region_pattern

#5.	Outliers (Rule-Based + Visualization)
# Outlier detection using IQR on compliance_gap (positive gaps matter)
gaps <- kra |> filter(compliance_gap > 0)

q1 <- quantile(gaps$compliance_gap, 0.25)
q3 <- quantile(gaps$compliance_gap, 0.75)
iqr <- q3 - q1
upper <- q3 + 1.5*iqr

outliers <- gaps |> filter(compliance_gap > upper) |>
  arrange(desc(compliance_gap)) |>
  select(pin, sector, region, filing_month, revenue, tax_due, tax_paid, compliance_gap, late_filing, audit_flag)

outliers |> head(10)

#6.	Visualizing Distributions — Histogram
ggplot(kra, aes(x = revenue)) +
  geom_histogram(bins = 40) +
  labs(title = "Revenue Distribution (Histogram)", x = "Revenue", y = "Count")

# Log scale to handle skew (common in revenue)
ggplot(kra, aes(x = revenue)) +
  geom_histogram(bins = 40) +
  scale_x_log10() +
  labs(title = "Revenue Distribution (Log Scale)", x = "Revenue (log10)", y = "Count")

#7.	Visualizing Distributions — Boxplot
# Tax paid by sector to spot spread and outliers
ggplot(kra, aes(x = sector, y = tax_paid)) +
  geom_boxplot() +
  coord_flip() +
  labs(title = "Tax Paid by Sector (Boxplot)", x = "Sector", y = "Tax Paid")

#8.	Visualizing Distributions — Density Plot
ggplot(kra, aes(x = compliance_gap)) +
  geom_density() +
  labs(title = "Compliance Gap Distribution (Density)", x = "Compliance Gap", y = "Density")

#9.	 Scatter Plot (Pattern Recognition)
# Revenue vs tax paid: should be roughly linear
ggplot(kra, aes(x = revenue, y = tax_paid)) +
  geom_point(alpha = 0.3) +
  scale_y_continuous(labels = label_number(scale = 1e-6, suffix = "M")) +
  labs(title = "Revenue vs Tax Paid", x = "Revenue", y = "Tax Paid")

# Add a trend line for clearer pattern
ggplot(kra, aes(x = revenue, y = tax_paid)) +
  geom_point(alpha = 0.25) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_y_continuous(labels = label_number(scale = 1e-6, suffix = "M")) +
  scale_x_continuous(labels = label_number(scale = 1e-6, suffix = "M")) +
  labs(title = "Revenue vs Tax Paid (with Trend Line)", x = "Revenue", y = "Tax Paid")

#10.	EDA Insight Checklist (Auto-derived summary table)
insights <- kra |>
  summarise(
    total_revenue = sum(revenue),
    total_taxpaid = sum(tax_paid),
    overall_late_rate = mean(late_filing),
    avg_gap = mean(compliance_gap),
    share_audited = mean(audit_flag),
    top_sector_by_gap = (kra |> group_by(sector) |> summarise(m=mean(compliance_gap), .groups="drop") |> arrange(desc(m)) |> slice(1) |> pull(sector)),
    top_region_by_gap = (kra |> group_by(region) |> summarise(m=mean(compliance_gap), .groups="drop") |> arrange(desc(m)) |> slice(1) |> pull(region))
  )

insights

