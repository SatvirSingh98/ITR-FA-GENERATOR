# Table A2 - Peak Balance Calculation

## Overview
Table A2 in Schedule FA reports the **custodial account summary** with opening balance, peak balance, and closing balance for the **calendar year**.

**IMPORTANT:** Schedule FA uses **calendar year (Jan 1 - Dec 31)**, NOT financial year (Apr 1 - Mar 31).

## What is Peak Balance?

**Peak Balance** = The highest total value (in INR) of all holdings during the entire **calendar year (January 1 - December 31)**.

For calendar year {YEAR}, this means the maximum value between **Jan 1, {YEAR} to Dec 31, {YEAR}**.

## How Peak Balance is Calculated

### Step 1: Daily Valuation Matrix
For each stock symbol (e.g., AMD), the script:
1. Gets **daily closing prices** from Yahoo Finance (all trading days in {YEAR})
2. Gets **SBI TTBR rates** for those same dates
3. Creates a matrix: `Date | Stock Price (USD) | TTBR | Value per Share (INR)`

### Step 2: Calculate Peak Per Share
For each symbol:
```
Peak Value per Share (INR) = MAX(Stock Price USD × TTBR) across all dates
```

**Example for AMD in {YEAR}:**
- Peak Date: {PEAK_DATE}
- AMD Price: $264.33 USD
- TTBR: ₹85.97
- **Peak per Share: ₹22,725.50**

### Step 3: Calculate Peak Balance for All Holdings
For each tranche (RSU/ESPP lot):
```
Peak Balance = Quantity × Peak Value per Share (INR)
```

**Example:**
- RSU Tranche 1: 10 shares × ₹22,725.50 = ₹2,27,255
- RSU Tranche 2: 8 shares × ₹22,725.50 = ₹1,81,804
- ESPP Tranche: 6 shares × ₹22,725.50 = ₹1,36,353
- **Total Peak Balance: ₹5,45,412**

### Step 4: Round and Report
- All values rounded UP using `math.ceil()` (tax compliance)
- Reported in Table A2 under **"Peak Balance During the Period"**

## Why Peak Balance Matters

**ITR Requirement:** Schedule FA requires you to report the highest value your foreign assets reached during the year, not just the closing value.

This helps tax authorities understand:
- Maximum exposure to foreign assets
- Wealth growth tracking
- Compliance verification

## Sheet in Excel Output

The **"A2 Peak Calculation"** sheet in `schedule_fa_{YEAR}-{YEAR+1}.xlsx` shows:
- Date-by-date total portfolio value
- Which date had the peak
- Breakdown by tranche

## Important Notes

### 1. Peak Date vs Peak USD Price
Peak INR value might NOT be on the same date as peak USD price because:
- USD price peaks on Date A at $250 (TTBR: 83.50) = ₹20,875
- USD price at $240 on Date B (TTBR: 86.00) = ₹20,640
- Peak INR: Date A wins

TTBR fluctuations affect the final INR value!

### 2. Only Trading Days
- Peak is calculated only for dates with **both** stock price AND TTBR
- Weekends/holidays excluded (no trading = no value change)

### 3. Multiple Symbols
If you have AMD + NVDA holdings:
```
Total Peak = Peak of (AMD Portfolio + NVDA Portfolio combined)
```

Each symbol has its own peak date, but we find the single day when the **total portfolio** was highest.

### 4. Sold Shares Within Calendar Year
The code includes **all shares owned on each date** when calculating daily total:
- If acquired before or on a date: included in that date's total
- Peak is the maximum across all dates in the calendar year
- Shares sold mid-year contribute to peak if they were owned on the peak date

**Note:** The current implementation includes sold shares in the daily calculation. The actual peak reflects whichever day had the maximum total value.

## Formula Summary

```python
# For each trading day in calendar year (Jan 1 - Dec 31)
daily_value = sum(quantity × stock_price_usd × ttbr for all holdings)

# Peak balance
peak_balance = max(daily_value across all calendar year trading days)
```

## Verification

To verify peak balance:
1. Open **"A2 Peak Calculation"** sheet
2. Check the **"PEAK SUMMARY"** side panel which shows:
   - Peak Date
   - Stock Price (USD) on that date
   - TTBR on that date
   - Account Value (USD) on that date
   - Account Value (INR) on that date
3. Scan the daily data to find the peak date row
4. Verify: Account Value (INR) = Account Value (USD) × TTBR
5. Cross-reference with **"Reference - Daily Rates"** for stock prices

## Example Output in Table A2

| Field | Value |
|-------|-------|
| Opening Balance (Jan 1, {YEAR}) | ₹4,50,000 |
| **Peak Balance During Period** | **₹5,45,412** |
| Closing Balance (Dec 31, {YEAR}) | ₹5,10,000 |

**Note:** Opening balance is typically 0 or calculated from previous year's closing. The script uses Dec 31 closing balance.

The peak balance is the key compliance field for Schedule FA!
