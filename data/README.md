# SBI Forex Historical Data

This directory contains the automatically updated SBI forex rates (all 8 rates) fetched daily by GitHub Actions.

## Files

- **`SBI_FOREX_CARD_RATES_USD.csv`** - Complete historical USD/INR forex rates from SBI
  - Columns: `DATE`, `TT BUY`, `TT SELL`, `BILL BUY`, `BILL SELL`, `FOREX TRAVEL CARD BUY`, `FOREX TRAVEL CARD SELL`, `CN BUY`, `CN SELL`
  - Updated daily at 9:00 PM IST
  - Data sources:
    1. Latest rates from SBI official PDF (all 8 rates)
    2. Historical rates from GitHub backup

## Automation

The data is automatically updated by the GitHub Actions workflow:
- **Schedule**: Daily at 9:00 PM IST (3:30 PM UTC)
- **Workflow**: `.github/workflows/fetch_sbi_ttbr.yml`
- **Bot**: GitHub Actions Bot commits new data automatically
- **Date Validation**: Only inserts SBI PDF data if it has today's date (prevents stale data)

## Manual Updates

You can also manually trigger the workflow:
1. Go to: **Actions** → **Fetch SBI TTBR Rates Daily**
2. Click **Run workflow**

## Data Usage

The ITR FA Generator (`itr_fa_engine.py`) automatically reads this CSV file if available (uses `TT BUY` column), otherwise it fetches data on-demand using `sbi_forex_fetcher.py`.

## Data Format

```csv
DATE,TT BUY,TT SELL,BILL BUY,BILL SELL,FOREX TRAVEL CARD BUY,FOREX TRAVEL CARD SELL,CN BUY,CN SELL
2025-01-01,83.50,84.42,83.45,84.50,83.45,84.50,82.50,85.00
2025-01-02,83.55,84.45,83.50,84.55,83.50,84.55,82.55,85.05
...
```

All dates are in ISO 8601 format (YYYY-MM-DD) for clean, unambiguous parsing.
