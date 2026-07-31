# Table A2 - Peak Balance Calculation

## Overview
Table A2 in Schedule FA reports the **custodial account summary** with opening balance, peak balance, and closing balance for the financial year.

## What is Peak Balance?

**Peak Balance** = The highest total value (in INR) of all holdings during the entire financial year (April 1 - March 31).

For FY 2025-26, this means the maximum value between **April 1, 2025 to March 31, 2026**.

## How Peak Balance is Calculated

### Step 1: Daily Valuation Matrix
For each stock symbol (e.g., AMD), the script:
1. Gets **daily closing prices** from Yahoo Finance (all trading days in 2025)
2. Gets **SBI TTBR rates** for those same dates
3. Creates a matrix: `Date | Stock Price (USD) | TTBR | Value per Share (INR)`

### Step 2: Calculate Peak Per Share
For each symbol:
```
Peak Value per Share (INR) = MAX(Stock Price USD × TTBR) across all dates
```

**Example for AMD in 2025:**
- Peak Date: October 29, 2025
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

The **"A2 Peak Calculation"** sheet in `schedule_fa_2025-26.xlsx` shows:
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

### 4. Sold Shares
Sold shares are **excluded** from peak calculation if sold before the peak date:
- Sold on June 1, 2025
- Peak occurred on October 29, 2025
- Those shares don't count toward peak (you didn't own them on peak date)

## Formula Summary

```python
# For each trading day in FY
daily_value = sum(quantity × stock_price_usd × ttbr for all holdings)

# Peak balance
peak_balance = max(daily_value across all trading days)
```

## Verification

To verify peak balance:
1. Open **"A2 Peak Calculation"** sheet
2. Check the row marked with ⭐ PEAK
3. Verify date and calculation
4. Cross-reference with **"Reference - Daily Rates"** for stock prices and TTBR

## Example Output in Table A2

| Field | Value |
|-------|-------|
| Opening Balance (Apr 1, 2025) | ₹4,50,000 |
| **Peak Balance During Period** | **₹5,45,412** |
| Closing Balance (Mar 31, 2026) | ₹5,10,000 |

The peak balance is the key compliance field for Schedule FA!
