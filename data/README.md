# SBI TTBR Historical Data

This directory contains the automatically updated SBI TTBR (TT Buying Rate) data fetched daily by GitHub Actions.

## Files

- **`sbi_ttbr_rates.csv`** - Historical USD/INR exchange rates from SBI
  - Columns: `Date` (YYYY-MM-DD), `TTBR` (exchange rate)
  - Updated daily at 9:00 PM IST
  - Data sources:
    1. Latest rate from SBI official PDF
    2. Historical rates from GitHub backup

## Automation

The data is automatically updated by the GitHub Actions workflow:
- **Schedule**: Daily at 9:00 PM IST (3:30 PM UTC)
- **Workflow**: `.github/workflows/fetch_sbi_ttbr.yml`
- **Bot**: GitHub Actions Bot commits new data automatically

## Manual Updates

You can also manually trigger the workflow:
1. Go to: **Actions** → **Fetch SBI TTBR Rates Daily**
2. Click **Run workflow**

## Data Usage

The ITR FA Generator (`itr_fa_engine.py`) automatically reads this CSV file if available, otherwise it fetches data on-demand using `sbi_ttbr_fetcher.py`.

## Data Format

```csv
Date,TTBR
2025-01-01,83.50
2025-01-02,83.55
...
```

All dates are in ISO 8601 format (YYYY-MM-DD) for unambiguous parsing.
