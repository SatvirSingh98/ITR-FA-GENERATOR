# Reference Sheet - Daily Rates

## Overview
The Excel file `schedule_fa_{YEAR}-{YEAR+1}.xlsx` contains a third sheet called **"Reference - Daily Rates"** with complete daily data for the entire year {YEAR}.

## Sheet Columns

| Column | Description |
|--------|-------------|
| **Date** | Every day of {YEAR} (365 rows) |
| **AMD Stock Price (USD)** | Daily closing price of AMD stock |
| **SBI TTBR Rate (USD to INR)** | State Bank of India TT Buying Rate |
| **AMD Value per Share (INR)** | Calculated: USD Price × TTBR |
| **Peak** | Marked with ⭐ PEAK on the highest INR value day |

## Peak Value Calculation

**IMPORTANT:** Peak is calculated **per holding**, NOT for the entire year!

For each holding, peak = maximum (Stock Price × TTBR) during the **holding window**:
- **Holding window = max(Jan 1, acquisition date) to min(Dec 31, sale date)**
- Example 1: Acquired Nov 2024, still holding → Window: Jan 1 to Dec 31 {YEAR}
- Example 2: Acquired May {YEAR}, still holding → Window: May {YEAR} to Dec 31 {YEAR}
- Example 3: Acquired Nov 2024, sold Jun {YEAR} → Window: Jan 1 to Jun {YEAR}

This means:
- Different holdings can have different peak dates
- Peak is specific to when YOU held the shares during the calendar year
- The ⭐ PEAK marker in Reference sheet shows the overall year peak (for reference only)

**Note:** Peak INR value depends on both stock price AND TTBR:
- Could occur when stock price is high OR TTBR is high (or both)

## How to Use

### Verify Your Holdings
1. Open the Reference sheet
2. Find the acquisition date of any tranche
3. Check the AMD price and TTBR on that date
4. Verify: Initial Value = Quantity × AMD Price (USD) × TTBR

### Example Verification
For ESPP Shares (6 shares) acquired on {DATE}:
- Look up {DATE} in Reference sheet
- AMD Price: ~$147.37 USD
- TTBR: ~83.65
- Initial Value: 6 × 147.37 × 83.65 = ₹74,421 ✓

### Find Peak Value
- Look for the row with ⭐ PEAK marker
- This shows when AMD reached its highest INR value
- All open holdings use this peak value

## Data Sources

- **AMD Prices:** Live web scraped from Yahoo Finance (~250 trading days per year)
- **SBI TTBR:** Loaded from historical CSV data (SBI_FOREX_CARD_RATES_USD.csv)
  - Updated daily via GitHub Actions at 9:00 PM IST
  - Sources: SBI official PDF + sbi-fx-ratekeeper archive
- **Non-trading days:** Backward-filled from most recent preceding trading day (per tax law)

## Notes

- **Weekends and holidays:** Values are backward-filled (uses most recent preceding trading day)
  - Per tax law: Use nearest PRECEDING working day, not after
  - Example: Sunday uses Friday's rate
- **Peak value date:** May differ from peak USD price date due to TTBR fluctuation
  - Peak INR value = Stock Price × TTBR
  - Could occur when USD price is high OR when TTBR is high
- **Rounding:** All values rounded to 2 decimal places for readability

