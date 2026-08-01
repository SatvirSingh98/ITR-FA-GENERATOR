# Reference Sheet - Daily Rates

## Overview
The Excel file `schedule_fa_{YEAR}-{YEAR+1}.xlsx` contains a third sheet called **"Reference - Daily Rates"** with complete daily data for the entire year {YEAR}.

## Sheet Columns

### Main Data Columns
| Column | Description |
|--------|-------------|
| **Date** | Every day of {YEAR} (365 rows) |
| **AMD Stock Price (USD)** | Daily closing price of AMD stock (from Yahoo Finance) |
| **SBI TTBR Rate (USD to INR)** | State Bank of India TT Buying Rate |
| **AMD Value per Share (INR)** | Calculated: USD Price × TTBR |

### Side Panel: "PEAK PER-SHARE INFO"
A summary box showing:
- Peak Date: When AMD per-share INR value was highest
- Stock Price (USD): Price on that date
- TTBR: Exchange rate on that date
- Peak Value (INR): Maximum per-share value

**Note:** This is just reference information. Actual peak values for holdings are calculated per-holding (see below).

## Peak Value Calculation (Per Holding)

**IMPORTANT:** Peak is calculated **per holding**, NOT for the entire year!

### How It Works
For each holding, peak = maximum (Stock Price × TTBR) during the **holding window**:

**Holding window = max(Jan 1, acquisition date) to min(Dec 31, sale date)**

### Examples
1. **Acquired Nov 2024, still holding** → Window: Jan 1 to Dec 31 {YEAR}
2. **Acquired May {YEAR}, still holding** → Window: May {YEAR} to Dec 31 {YEAR}
3. **Acquired Nov 2024, sold Jun {YEAR}** → Window: Jan 1 to Jun {YEAR}

### Key Points
- Different holdings can have **different peak dates**
- Peak is specific to **when YOU held** the shares during the calendar year
- The "PEAK PER-SHARE INFO" panel in this sheet is **reference only**
- For actual **account-level peak**, see **"A2 Peak Calculation"** sheet

### What Affects Peak
Peak INR value depends on BOTH:
- Stock price (USD)
- TTBR (exchange rate)

Peak could occur when stock price is high OR TTBR is high (or both).

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

### Check Peak Per-Share Info
- Look at the "PEAK PER-SHARE INFO" side panel
- Shows when AMD reached its highest per-share INR value for the year
- **This is reference only** - actual holding peaks vary by holding window

### Check Account-Level Peak
- For actual Table A2 peak calculation, see **"A2 Peak Calculation"** sheet
- Shows daily total account value and identifies the peak date
- This is what's reported in Table A2 "Peak Balance During Period"

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

