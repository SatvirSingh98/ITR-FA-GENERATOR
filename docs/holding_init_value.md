# Pre-FY Holdings - Initial Value Calculation

## Overview
The **"Pre-FY Holdings Init Val"** sheet calculates the **Initial Value** for holdings acquired **before the financial year started**.

This is crucial for Schedule FA Table A3 compliance.

## What is Initial Value?

**Initial Value** = The INR value of shares when they were acquired (acquisition date valuation).

For shares acquired **before** the FY starts (e.g., acquired in 2024 for FY 2025-26), we need to calculate:
```
Initial Value (INR) = Quantity × Stock Price (USD) on Acquisition Date × TTBR on Acquisition Date
```

## Why Pre-FY Holdings Need Special Handling

### The Problem:
When generating Schedule FA for **FY 2025-26** (Apr 1, 2025 - Mar 31, 2026):
- SBI TTBR data covers **2025 only** (the target year)
- But some shares were acquired in **2024** (or earlier)
- We need TTBR for acquisition dates in **2024** to calculate their initial value

### The Solution:
The script:
1. **Detects** all acquisition dates that fall **before** the FY start date
2. **Downloads extra TTBR data** for those specific dates (with ±3 day buffer for weekends)
3. **Caches** this pre-FY data alongside current-year data
4. **Calculates** initial value using historical stock price + historical TTBR

## Step-by-Step Process

### Step 1: Identify Pre-FY Acquisitions
From `ByStatus_expanded.xlsx` (E*TRADE Holdings):
```
Example acquisitions:
- 2024-07-20: 10 shares (RSU) → Pre-FY ✓
- 2024-12-15: 6 shares (ESPP) → Pre-FY ✓
- 2025-06-01: 8 shares (RSU) → Current FY ✗
```

For FY 2025-26, acquisitions before **April 1, 2025** need special handling.

### Step 2: Download Historical TTBR
The script calls `_fetch_sbi_rates_web()` with `extra_dates`:
```python
extra_dates = ['2024-07-20', '2024-12-15']
# Plus ±3 day buffer: ['2024-07-17', '2024-07-18', ..., '2024-07-23']
```

This fetches TTBR for those specific dates from historical GitHub data.

### Step 3: Download Historical Stock Prices
For each pre-FY acquisition date:
```python
# Get stock price on acquisition date
stock_price_usd = yahoo_finance.get_price(symbol='AMD', date='2024-07-20')
ttbr = sbi_data.get_rate(date='2024-07-20')
```

### Step 4: Calculate Initial Value
```python
initial_value_inr = quantity × stock_price_usd × ttbr
```

**Example:**
```
RSU Tranche acquired on 2024-07-20:
- Quantity: 10 shares
- AMD Price on 2024-07-20: $147.50 USD
- TTBR on 2024-07-20: 83.25
- Initial Value = 10 × 147.50 × 83.25 = ₹1,22,794
```

### Step 5: Round Up
```python
initial_value_inr = math.ceil(initial_value_inr)
```

All values rounded UP for tax compliance.

## Why ±3 Day Buffer?

### The Weekend Problem:
If acquisition date falls on a weekend or holiday:
- **Stock market:** Closed (no price)
- **Indian banks:** Closed (no TTBR)

### Solution: Forward-Fill Logic
```
Acquisition Date: 2024-12-14 (Saturday - market closed)
Buffer dates: 2024-12-11, 12-12, 12-13, 12-14, 12-15, 12-16, 12-17

Use last available trading day before 12-14:
- 2024-12-13 (Friday): ✓ Market open, TTBR available
```

The script:
1. Downloads TTBR for a **range** around the acquisition date
2. Forward-fills to cover weekends/holidays
3. Uses the **closest prior trading day** if exact date unavailable

## Excel Sheet Output

The **"Pre-FY Holdings Init Val"** sheet shows:

| Column | Description |
|--------|-------------|
| Symbol | Stock ticker (e.g., AMD) |
| Quantity | Number of shares |
| Acquisition Date | When shares were acquired |
| Stock Price (USD) | Price on acquisition date |
| TTBR | Exchange rate on acquisition date |
| Initial Value (INR) | Calculated value (rounded up) |

This is a **reference sheet** - the values are also used in **Table A3**.

## Example Scenario

### Holdings for FY 2025-26:

**Pre-FY Holdings (need historical data):**
1. RSU Tranche A: 10 shares, acquired **2024-07-20**
2. ESPP Tranche: 6 shares, acquired **2024-12-15**

**Current-FY Holdings (use current-year data):**
3. RSU Tranche B: 8 shares, acquired **2025-06-01**

### Initial Value Calculation:

**Tranche A (Pre-FY):**
```
Date: 2024-07-20
Quantity: 10
AMD Price: $147.50
TTBR: 83.25
Initial Value = ceil(10 × 147.50 × 83.25) = ₹1,22,794
```

**ESPP (Pre-FY):**
```
Date: 2024-12-15
Quantity: 6
AMD Price: $152.30
TTBR: 83.65
Initial Value = ceil(6 × 152.30 × 83.65) = ₹76,465
```

**Tranche B (Current-FY):**
```
Date: 2025-06-01
Quantity: 8
AMD Price: $180.00
TTBR: 84.20
Initial Value = ceil(8 × 180.00 × 84.20) = ₹1,21,248
```

## Console Output During Generation

When the script detects pre-FY holdings:
```
[*] Found acquisition dates before FY 2025, downloading TTBR with ±3 day buffer for weekends
[OK] Downloaded 278 SBI TTBR records for 2025
[OK] Plus 8 specific dates before FY: 2024-07-17, 2024-07-18, ..., 2024-12-18
[OK] TTBR range: 82.50 to 86.49
```

This confirms:
- Current-year TTBR downloaded (278 records for 2025)
- Pre-FY TTBR downloaded (8 records around 2024-05-15 and 2024-11-08)

## Important Notes

### 1. TTBR Source: GitHub Historical Data
Pre-FY TTBR comes from:
```
https://github.com/sahilgupta/sbi-fx-ratekeeper
```

This has historical data going back to 2020, so acquisitions from 2020-2024 are covered.

### 2. What if Acquisition Date has No TTBR?
If the exact date is missing:
- The ±3 day buffer usually covers it (finds nearest trading day)
- If still missing, script will error out
- **Manual fix:** Add that date's TTBR to `data/SBI_FOREX_CARD_RATES_USD.csv`

### 3. Stock Price Source: Yahoo Finance
Yahoo Finance has historical data going back years, so this is usually not a problem.

### 4. Multiple Pre-FY Tranches
If you have 10 tranches acquired in different years:
- Script collects all unique acquisition dates
- Downloads TTBR for all of them in one batch
- Efficient: no duplicate downloads

### 5. No Pre-FY Holdings?
If all acquisitions are within the current FY:
- This sheet will be **empty** (or show "No pre-FY holdings")
- No historical TTBR download needed

## Verification Steps

1. Open **"Pre-FY Holdings Init Val"** sheet
2. Check each pre-FY tranche listed
3. Verify acquisition date is before FY start date
4. Cross-check stock price with Yahoo Finance historical data
5. Cross-check TTBR with `data/SBI_FOREX_CARD_RATES_USD.csv`
6. Verify calculation: Qty × Price × TTBR
7. Confirm all values rounded UP

## Relationship to Table A3

The initial values calculated here appear in **Table A3 - Equity Interest**:

**Table A3 Columns:**
- Date of Acquisition → From ByStatus
- Initial Value of Investment → **From this calculation**
- Peak Value → From peak calculation (current-year data)
- Closing Value → From closing calculation (current-year data)

## Common Questions

**Q: Why not just use current-year TTBR for all holdings?**
A: That would be incorrect. Initial value must reflect the **actual** exchange rate when shares were acquired.

**Q: What if I acquired shares in 2020?**
A: As long as the GitHub historical data has 2020 TTBR, it will work. The current dataset goes back to 2020-01-04.

**Q: What if TTBR is missing for my acquisition date?**
A: 
1. Check if it's a weekend/holiday (±3 buffer should handle it)
2. If still missing, manually add that date's TTBR to the CSV
3. Re-run the script

**Q: Why ±3 days instead of ±1?**
A: Handles long weekends and holiday clusters (e.g., Diwali + weekend = 4-5 days off)

**Q: Does this affect capital gains calculation?**
A: Yes! Initial value (cost basis) for pre-FY holdings uses this same historical TTBR + stock price.

## Example: Full Pre-FY Flow

**Scenario:** Generating Schedule FA for FY 2025-26

**Holdings:**
- RSU: 10 shares, acquired 2024-07-20
- ESPP: 6 shares, acquired 2024-12-15

**Script Execution:**
```
1. [*] Reading E*TRADE files...
2. [OK] Discovered 2 tranches, 2 are pre-FY
3. [*] Downloading SBI TTBR for 2025...
4. [OK] Downloaded 278 records
5. [*] Found pre-FY dates, downloading historical TTBR...
6. [OK] Plus 8 specific dates: 2024-07-17 to 2024-07-23, 2024-12-12 to 2024-12-18
7. [*] Scraping Yahoo Finance for AMD...
8. [OK] Got prices for all dates including historical
9. [*] Calculating initial values...
10. [OK] Pre-FY Holdings:
    - 2024-07-20: 10 shares, $147.50, TTBR 83.25 → ₹1,22,794
    - 2024-12-15: 6 shares, $152.30, TTBR 83.65 → ₹76,465
11. [OK] Saved to "Pre-FY Holdings Init Val" sheet
```

**Output in Excel:**
All pre-FY holdings listed with proper historical valuation! ✓
