# Dividend Handling in Schedule FA

## Overview
This document explains how dividend income from US stocks (RSU/ESPP holdings) is reported in Schedule FA (Foreign Assets disclosure).

**IMPORTANT:** Schedule FA dividend reporting is DIFFERENT from Schedule OS (income tax calculation).

---

## Critical Distinction: Schedule FA vs Schedule OS

### Schedule FA (Asset Disclosure)
- **Purpose:** Disclose the foreign account and holdings that paid dividends
- **Exchange Rate:** Use **exact credit date TTBR** (per CBDT filing instructions)
- **Where Reported:** Table A2 (account level) and Table A3 (per holding)
- **Implemented in this tool:** ✅ YES

### Schedule OS (Income Tax Calculation)
- **Purpose:** Calculate taxable dividend income and tax liability
- **Exchange Rate:** Use **Rule 115(1)(e)** - last day of month BEFORE dividend month
- **Where Reported:** Schedule OS (Other Sources income section of ITR-2)
- **Implemented in this tool:** ❌ NO (out of scope)

**Example:**
```
Dividend received: Aug 15, 2025 - $100

Schedule FA (this tool):
  - Uses Aug 15, 2025 TTBR (exact credit date)
  - Reports in Table A2 and Table A3

Schedule OS (separate ITR section):
  - Uses Jul 31, 2025 TTBR (last day of month BEFORE Aug)
  - Reports as taxable income
  - Different INR amount due to different exchange rate!
```

---

## How Schedule FA Reports Dividends

### Table A2 (Account Level)

**Rule:** If account has BOTH dividends AND sales, create **TWO separate rows**

#### Case 1: Both Dividends AND Sales
```
Row 1:
  - Nature of Amount: "D" (Dividend)
  - Amount: Total dividends in INR
  - Peak/Closing Balance: Same on both rows

Row 2:
  - Nature of Amount: "P" (Proceeds from Sale)
  - Amount: Total sale proceeds in INR
  - Peak/Closing Balance: Same on both rows
```

#### Case 2: Dividends Only (No Sales)
```
Row 1:
  - Nature of Amount: "D" (Dividend)
  - Amount: Total dividends in INR
```

#### Case 3: Sales Only (No Dividends)
```
Row 1:
  - Nature of Amount: "P" (Proceeds from Sale)
  - Amount: Total sale proceeds in INR
```

#### Case 4: Neither Dividends Nor Sales
```
Row 1:
  - Nature of Amount: "N" (No Amount)
  - Amount: 0
```

**Key Point:** The same dividend appears in BOTH Table A2 and Table A3 - this is CORRECT, not duplication!

---

### Table A3 (Per Holding)

**Rule:** Allocate dividend **PROPORTIONALLY** to each lot based on shares held on dividend payment date

**Algorithm:**
```
For each dividend payment:
  1. Find all lots acquired ON OR BEFORE dividend date
  2. Calculate shares held in each lot on dividend date
     (subtract shares sold before dividend)
  3. Calculate total shares across all lots
  4. Allocate: lot_dividend = (lot_shares / total_shares) × dividend
```

**Example:**
```
Symbol: AMD
Dividend: $120 on March 15, 2025 (TTBR 84.00 = ₹10,080)

Holdings on March 15, 2025:
  - Lot A (RSU, 10 shares): Acquired Jan 15, 2025 → 10 shares held
  - Lot B (RSU, 20 shares): Acquired Feb 10, 2025 → 20 shares held  
  - Lot C (ESPP, 30 shares): Acquired Aug 5, 2025 → 0 shares (not vested yet)
  Total: 30 shares

Allocation:
  - Lot A: (10/30) × ₹10,080 = ₹3,360
  - Lot B: (20/30) × ₹10,080 = ₹6,720
  - Lot C: (0/30) × ₹10,080 = ₹0
  
Verification: ₹3,360 + ₹6,720 + ₹0 = ₹10,080 ✓
```

**Handles Partial Sales:**
```
If Lot A sold 5 shares on Feb 20 (before March 15 dividend):
  - Lot A held on March 15: 10 - 5 = 5 shares
  - Total shares: 5 + 20 + 0 = 25 shares
  - Lot A gets: (5/25) × ₹10,080 = ₹2,016
```

**Multiple Dividends:**
- Each dividend is allocated separately based on holdings on THAT dividend date
- Lot dividends accumulate across multiple payments

---

## Exchange Rate Rule for Schedule FA Dividends

**Use exact credit date TTBR** (NOT Rule 115(1)(e) month-end rate!)

### How It Works
1. Dividend credited: Aug 15, 2025 - $100
2. Look up SBI TTBR on **Aug 15, 2025** (exact date)
3. If Aug 15 is weekend/holiday → Use nearest **preceding** working day
4. Convert: $100 × TTBR on Aug 15 = ₹X

**Source:** CBDT Schedule FA filing instructions specify exact event date TTBR

**Common Mistake:** Using Rule 115(1)(e) (last day of month BEFORE dividend month)
- Rule 115(1)(e) is for Schedule OS (income tax), NOT Schedule FA!

---

## Data Source: Transaction History CSV

### Where to Get It
1. Log into E*TRADE
2. Go to **Accounts → Transaction History**
3. Select **Custom Time Period**: Calendar year (Jan 1 - Dec 31)
4. Click **Download** icon (top right)
5. Save as: `Transaction_History.csv` in `etrade_inputs/` folder

### What the Tool Does
1. Reads `Transaction_History.csv` (optional - no error if missing)
2. Filters for dividend transactions (TransactionType or Description contains "Dividend")
3. Filters to calendar year only (Jan 1 - Dec 31)
4. Gets TTBR for each dividend credit date (exact date)
5. Converts to INR: Amount (USD) × TTBR = Amount (INR)
6. Aggregates per symbol for Table A3
7. Sums all symbols for Table A2

### File Format Support
The tool auto-detects various E*TRADE CSV formats:
- **Date column:** TransactionDate, Date, SettlementDate, or PostedDate
- **Amount column:** Amount, NetAmount, Quantity, or Credit
- **Symbol column:** Symbol, SecuritySymbol, or Ticker

---

## Output: Dividend Reference Sheet

If dividends exist, the Excel file includes a **"Dividend Transactions"** sheet showing:

| Column | Description |
|--------|-------------|
| Symbol | Stock ticker (e.g., AMD) |
| Date | Dividend credit date (YYYY-MM-DD) |
| Amount (USD) | Dividend in US dollars |
| TTBR | SBI TTBR on credit date |
| Amount (INR) | Dividend in rupees (rounded up) |

**Purpose:** Verify dividend conversions and trace to Table A2/A3 totals

---

## AMD Stock and Dividends

**IMPORTANT:** AMD does **NOT** pay dividends on its common stock.

If you hold only AMD shares (typical for AMD employees), you will:
- ❌ NOT have any dividend transactions
- ✅ Transaction History file is optional (tool works without it)
- ✅ Table A2 will have Nature of Amount = "P" (if sales) or "N" (if no sales)

This dividend feature is for users who hold **other dividend-paying stocks** (e.g., Apple, Microsoft, Intel).

---

## Testing Dividend Support

### If You Don't Receive Dividends (AMD only)
No action needed! The tool works perfectly without Transaction History:
```
[i] Transaction History file not found - skipping dividend processing
[i] Table A2: Creating ONE row (Sale Proceeds only: ₹1,72,200)
```

### If You Hold Dividend-Paying Stocks
1. Download Transaction History CSV for calendar year
2. Place in `etrade_inputs/Transaction_History.csv`
3. Run the tool
4. Verify in Excel output:
   - **Table A2:** Check if separate dividend row exists
   - **Table A3:** Check first lot of each symbol has dividend amount
   - **Dividend Transactions sheet:** Review all dividend conversions

---

## Example: Complete Dividend Flow

### Input Data
**Transaction History CSV:**
```csv
TransactionDate,Symbol,Description,Amount
2025-03-15,AMD,Cash Dividend,120.00
2025-06-15,AMD,Cash Dividend,120.00
2025-09-15,AMD,Cash Dividend,120.00
2025-12-15,AMD,Cash Dividend,120.00
```

**TTBR Rates:**
- Mar 15, 2025: ₹84.00
- Jun 15, 2025: ₹84.50
- Sep 15, 2025: ₹85.00
- Dec 15, 2025: ₹85.50

### Calculations
```
Mar: $120 × 84.00 = ₹10,080
Jun: $120 × 84.50 = ₹10,140
Sep: $120 × 85.00 = ₹10,200
Dec: $120 × 85.50 = ₹10,260
-----------------------------------
Total: $480        = ₹40,680
```

### Output in Schedule FA

**Table A2 (if sales also occurred):**
```
Row 1:
  Peak Balance: ₹3,47,760
  Closing Balance: ₹1,54,560
  Nature of Amount: D (Dividend)
  Amount: ₹40,680

Row 2:
  Peak Balance: ₹3,47,760
  Closing Balance: ₹1,54,560
  Nature of Amount: P (Proceeds from Sale)
  Amount: ₹1,72,200
```

**Table A3 (AMD holdings):**
```
Assume all 3 lots held for all 4 quarterly dividends:
  Total shares: 10 + 8 + 6 = 24 shares

Lot 1 (RSU, 10 shares):
  TotGrossAmtPaidCredited: (10/24) × ₹40,680 = ₹16,950
  TotGrossProceeds: ₹0

Lot 2 (RSU, 8 shares):
  TotGrossAmtPaidCredited: (8/24) × ₹40,680 = ₹13,560
  TotGrossProceeds: ₹0

Lot 3 (ESPP, 6 shares):
  TotGrossAmtPaidCredited: (6/24) × ₹40,680 = ₹10,170
  TotGrossProceeds: ₹1,72,200      ← This lot was sold

Verification: ₹16,950 + ₹13,560 + ₹10,170 = ₹40,680 ✓
```

**Dividend Transactions Sheet:**
```
Symbol | Date       | Amount (USD) | TTBR  | Amount (INR)
-------|------------|--------------|-------|-------------
AMD    | 2025-03-15 | 120.00       | 84.00 | 10,080
AMD    | 2025-06-15 | 120.00       | 84.50 | 10,140
AMD    | 2025-09-15 | 120.00       | 85.00 | 10,200
AMD    | 2025-12-15 | 120.00       | 85.50 | 10,260
```

---

## Troubleshooting

### "Transaction History file not found"
**Status:** Normal if you don't receive dividends (AMD stock)
**Action:** None needed

### "No dividend transactions found in Transaction History"
**Possible causes:**
1. Stock doesn't pay dividends (AMD)
2. Wrong date range exported (should be Jan 1 - Dec 31)
3. CSV format not recognized

**Solution:** Check Transaction History CSV has "Dividend" in Description/Type column

### "Could not find date column in Transaction History"
**Cause:** E*TRADE changed CSV format
**Solution:** Open GitHub issue with sample CSV (remove sensitive data)

### Weekend/Holiday Dividend Dates
```
[i] Dividend 2025-07-04 is weekend/holiday, using previous trading day 2025-07-03 TTBR: 84.75
```
**Status:** Normal - tool automatically finds preceding working day

### Dividend Allocation Per Lot
**Expected behavior:** 
- Each lot gets dividend proportional to shares held on dividend date
- Output shows allocation per lot during execution
```
[*] Calculating dividends per lot...
  Dividend: AMD on 2025-03-15 - INR 10,080.00
    Total shares held on 2025-03-15: 24
      RSU (10 shares)  | 10 shares | INR 4,200.00
      RSU (8 shares)   |  8 shares | INR 3,360.00
      ESPP (6 shares)  |  6 shares | INR 2,520.00
```

---

## Related Documentation

- **Schedule OS (Income Tax):** See ITRFA.in blog on Schedule OS dividend income
- **Exchange Rate Rules:** See [docs/exchange_rates.md](exchange_rates.md)
- **Table A2 vs A3:** See [docs/table_a2_vs_a3.md](table_a2_vs_a3.md)

---

## Sources and Credits

- **ITRFA.in:** Schedule FA Table A2 vs A3 guidance
  - https://itrfa.in/blog/schedule-fa-table-a2-vs-a3
- **CBDT Filing Instructions:** Schedule FA uses exact event date TTBR
- **Income-tax Rule 115(1)(e):** Last day of month before dividend month (for Schedule OS, not FA)

---

## Summary

✅ **Schedule FA dividend handling:**
- Use exact credit date TTBR
- Create separate A2 row if both dividends and sales exist
- Allocate dividend proportionally to each lot based on holdings on dividend date
- Handles partial sales and multiple dividend payments
- Same dividend total appears in both A2 and A3 (correct!)

❌ **Out of scope:**
- Schedule OS (income tax calculation)
- Rule 115(1)(e) month-end rate (that's for Schedule OS)
- Quarterly breakup for advance tax
- Form 67 foreign tax credit

This tool handles **Schedule FA disclosure only** - consult ITRFA.in or your CA for Schedule OS/FSI/Form 67.
