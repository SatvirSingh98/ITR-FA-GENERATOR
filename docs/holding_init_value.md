# Pre-Calendar-Year Holdings - Initial Value Calculation

## Overview
The **"Pre-{YEAR} Holdings Init Val"** sheet calculates the **Initial Value** for holdings acquired **before the calendar year started**.

**IMPORTANT:** Schedule FA uses **calendar year** (Jan 1 - Dec 31), NOT financial year (Apr 1 - Mar 31).

This is crucial for Schedule FA Table A3 compliance.

## What is Initial Value?

**Initial Value** = The INR value of shares when they were acquired (acquisition date valuation).

For shares acquired **before** the target calendar year starts (e.g., acquired in previous year), we need to calculate:
```
Initial Value (INR) = Quantity × Stock Price (USD) on Acquisition Date × TTBR on Acquisition Date
```

## Why Pre-Calendar-Year Holdings Need Special Handling

### The Problem:
When generating Schedule FA for a target calendar year (e.g., {YEAR}):
- SBI TTBR data covers **target year only** (e.g., {YEAR})
- But some shares were acquired in **previous years** (e.g., {YEAR-1} or earlier)
- We need TTBR for those historical acquisition dates to calculate their initial value

### The Solution:
The script:
1. **Detects** all acquisition dates that fall **before** the calendar year start (Jan 1 of target year)
2. **Downloads extra TTBR data** for those specific dates (with ±3 day buffer for weekends)
3. **Caches** this historical data alongside current-year data
4. **Calculates** initial value using historical stock price + historical TTBR

## Step-by-Step Process

### Step 1: Identify Pre-Year Acquisitions
From `ByStatus_expanded.xlsx` (E*TRADE Holdings):
```
Example (for target year {YEAR}):
- {YEAR-1}-07-20: 10 shares (RSU) → Pre-year ✓ (before Jan 1, {YEAR})
- {YEAR-1}-12-15: 6 shares (ESPP) → Pre-year ✓ (before Jan 1, {YEAR})
- {YEAR}-06-01: 8 shares (RSU) → Current year ✗ (in target year)
```

Acquisitions before **January 1 of target year** need special handling.

### Step 2: Download Historical TTBR
The script calls `_fetch_sbi_rates_web()` with `extra_dates`:
```python
extra_dates = ['{YEAR-1}-07-20', '{YEAR-1}-12-15']
# Plus ±3 day buffer: ['{YEAR-1}-07-17', '{YEAR-1}-07-18', ..., '{YEAR-1}-07-23']
```

This fetches TTBR for those specific dates from historical GitHub data.

### Step 3: Download Historical Stock Prices
For each pre-{YEAR} acquisition date:
```python
# Get stock price on acquisition date
stock_price_usd = yahoo_finance.get_price(symbol='AMD', date='{YEAR-1}-07-20')
ttbr = sbi_data.get_rate(date='{YEAR-1}-07-20')
```

### Step 4: Calculate Initial Value
```python
initial_value_inr = quantity × stock_price_usd × ttbr
```

**Example:**
```
RSU Tranche acquired on {YEAR-1}-07-20:
- Quantity: 10 shares
- AMD Price on {YEAR-1}-07-20: $147.50 USD
- TTBR on {YEAR-1}-07-20: 83.25
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
Acquisition Date: {YEAR-1}-12-14 (Saturday - market closed)
Buffer dates: {YEAR-1}-12-11, 12-12, 12-13, 12-14, 12-15, 12-16, 12-17

Use last available trading day before 12-14:
- {YEAR-1}-12-13 (Friday): ✓ Market open, TTBR available
```

The script:
1. Downloads TTBR for a **range** around the acquisition date
2. Forward-fills to cover weekends/holidays
3. Uses the **closest prior trading day** if exact date unavailable

## Excel Sheet Output

The **"Pre-{YEAR} Holdings Init Val"** sheet shows:

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

### Holdings for Calendar Year {YEAR} (Schedule FA: Jan 1 - Dec 31, {YEAR}):

**Pre-{YEAR} Holdings (need historical data):**
1. RSU Tranche A: 10 shares, acquired **{YEAR-1}-07-20**
2. ESPP Tranche: 6 shares, acquired **{YEAR-1}-12-15**

**Current Calendar Year Holdings (use {YEAR} data):**
3. RSU Tranche B: 8 shares, acquired **{YEAR}-06-01**

### Initial Value Calculation:

**Tranche A (Pre-{YEAR}):**
```
Date: {YEAR-1}-07-20
Quantity: 10
AMD Price: $147.50
TTBR: 83.25
Initial Value = ceil(10 × 147.50 × 83.25) = ₹1,22,794
```

**ESPP (Pre-{YEAR}):**
```
Date: {YEAR-1}-12-15
Quantity: 6
AMD Price: $152.30
TTBR: 83.65
Initial Value = ceil(6 × 152.30 × 83.65) = ₹76,465
```

**Tranche B (Current Calendar Year):**
```
Date: {YEAR}-06-01
Quantity: 8
AMD Price: $180.00
TTBR: 84.20
Initial Value = ceil(8 × 180.00 × 84.20) = ₹1,21,248
```

## Console Output During Generation

When the script detects pre-{YEAR} holdings:
```
[*] Found acquisition dates before calendar year {YEAR}, downloading TTBR with ±3 day buffer for weekends
[OK] Downloaded 278 SBI TTBR records for {YEAR}
[OK] Plus 8 specific dates before {YEAR}: {YEAR-1}-07-17, {YEAR-1}-07-18, ..., {YEAR-1}-12-18
[OK] TTBR range: 82.50 to 86.49
```

This confirms:
- Current-year TTBR downloaded (278 records for {YEAR})
- Pre-{YEAR} TTBR downloaded (8 records around {YEAR-1}-05-15 and {YEAR-1}-11-08)

## Important Notes

### 1. TTBR Source: GitHub Historical Data
Pre-{YEAR} TTBR comes from:
```
https://github.com/sahilgupta/sbi-fx-ratekeeper
```

This has historical data going back to 2020, so acquisitions from 2020-{YEAR-1} are covered.

### 2. What if Acquisition Date has No TTBR?
If the exact date is missing:
- The ±3 day buffer usually covers it (finds nearest trading day)
- If still missing, script will error out
- **Manual fix:** Add that date's TTBR to `data/SBI_FOREX_CARD_RATES_USD.csv`

### 3. Stock Price Source: Yahoo Finance
Yahoo Finance has historical data going back years, so this is usually not a problem.

### 4. Multiple Pre-{YEAR} Tranches
If you have 10 tranches acquired in different years:
- Script collects all unique acquisition dates
- Downloads TTBR for all of them in one batch
- Efficient: no duplicate downloads

### 5. No Pre-{YEAR} Holdings?
If all acquisitions are within calendar year {YEAR} (on or after Jan 1, {YEAR}):
- This sheet will be **empty** (or show "No acquisitions before calendar year start")
- No historical TTBR download needed

## Verification Steps

1. Open **"Pre-{YEAR} Holdings Init Val"** sheet
2. Check each pre-{YEAR} tranche listed
3. Verify acquisition date is before Jan 1, {YEAR} (calendar year start)
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
A: As long as the GitHub historical data has 2020 TTBR, it will work. The current dataset goes back to 2020-01-04. These will show in the pre-{YEAR} holdings sheet.

**Q: What if TTBR is missing for my acquisition date?**
A: 
1. Check if it's a weekend/holiday (±3 buffer should handle it)
2. If still missing, manually add that date's TTBR to the CSV
3. Re-run the script

**Q: Why ±3 days instead of ±1?**
A: Handles long weekends and holiday clusters (e.g., Diwali + weekend = 4-5 days off)

**Q: Does this affect capital gains calculation?**
A: No! Capital Gains uses Rule 115(1)(f) - a different exchange rate rule (last day of month before sale). This sheet is only for Schedule FA Table A3 initial value.

## Example: Full Pre-{YEAR} Flow

**Scenario:** Generating Schedule FA for Calendar Year {YEAR}

**Holdings:**
- RSU: 10 shares, acquired {YEAR-1}-07-20 (before Jan 1, {YEAR})
- ESPP: 6 shares, acquired {YEAR-1}-12-15 (before Jan 1, {YEAR})

**Script Execution:**
```
1. [*] Reading E*TRADE files...
2. [OK] Discovered 2 tranches, 2 are pre-{YEAR}
3. [*] Downloading SBI TTBR for {YEAR}...
4. [OK] Downloaded 278 records
5. [*] Found acquisition dates before calendar year {YEAR}, downloading historical TTBR...
6. [OK] Plus 8 specific dates: {YEAR-1}-07-17 to {YEAR-1}-07-23, {YEAR-1}-12-12 to {YEAR-1}-12-18
7. [*] Scraping Yahoo Finance for AMD...
8. [OK] Got prices for all dates including historical
9. [*] Calculating initial values...
10. [OK] Pre-{YEAR} Holdings:
    - {YEAR-1}-07-20: 10 shares, $147.50, TTBR 83.25 → ₹1,22,794
    - {YEAR-1}-12-15: 6 shares, $152.30, TTBR 83.65 → ₹76,465
11. [OK] Saved to "Pre-{YEAR} Holdings Init Val" sheet
```

**Output in Excel:**
All pre-{YEAR} holdings listed with proper historical valuation! ✓
