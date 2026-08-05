# Table A3 Structure - Multiple Rows for Partial Sales

## Overview
Table A3 (Equity Interest) in Schedule FA uses **MULTIPLE rows for the same acquisition date** when there is a partial sale.

**Source:** Email clarification from ITRFA.in (2026-08-03)

---

## The Rule: Separate Rows for Partial Sales

**When a lot is partially sold, create TWO separate rows:**

1. **Row for shares STILL HOLDING:**
   - **Initial Value**: Value of shares currently holding
   - **Peak Balance**: Peak value of shares currently holding
   - **Closing Balance**: Value of shares on Dec 31 (non-zero)
   - **Gross Proceeds**: ₹0

2. **Row for shares SOLD:**
   - **Initial Value**: Value of sold shares (at acquisition)
   - **Peak Balance**: Peak value of sold shares (before sale)
   - **Closing Balance**: ₹0 (no longer holding)
   - **Gross Proceeds**: Actual sale proceeds

**Key Insight:** The two portions have genuinely different peak and closing values through the year. Combining them into one row would misstate both values.

---

## ITRFA.in Official Guidance (2026-08-03)

### Question Asked:
"I see that in A3 you have mentioned multiple rows for the shares with acquisition date of 2024-11-08 as there was partial sale for this, is this format correct? I thought like we need to have only one row per acquisition date per entity type and if there is any sale then we need to decrease the shares, correct the peak value and then provide the gross proceeds."

### ITRFA.in Answer:
"**Multiple A3 rows for the same acquisition date — yes, correct, and intentional.** A holding acquired on one date but partly sold shows as two separate Table A3 rows: one for the shares still held (closing value = your Dec 31 balance) and one for the shares sold (closing value = 0, gross proceeds shown). **We never collapse these into a single row with a reduced share count, because the two portions have genuinely different peak and closing values through the year — combining them would misstate both.**"

---

## Example: Partial Sale

### Scenario
- **Acquisition**: Nov 8, 2024 - 11 ESPP shares @ $147.95/share
- **Sale**: Sold 5 shares on Aug 15, 2025 for $451.11 total
- **Holding**: Still holding 6 shares as of Dec 31, 2025

### CORRECT Approach (TWO rows)
```
Row 1: ESPP (6 shares)
  - Acq Date: Nov 8, 2024
  - Initial Value: ₹88,929    (6 shares × $147.95 × 83.15 TTBR)
  - Peak Balance: ₹XXX,XXX     (6 shares × peak price)
  - Closing Balance: ₹210,770  (6 shares × $147.95 × 89.47 TTBR)
  - Gross Proceeds: ₹0

Row 2: ESPP (5 shares) Sold
  - Acq Date: Nov 8, 2024
  - Initial Value: ₹74,108    (5 shares × $147.95 × 83.15 TTBR)
  - Peak Balance: ₹XXX,XXX     (5 shares × peak price before sale)
  - Closing Balance: ₹0        (no longer holding)
  - Gross Proceeds: ₹201,805   (actual sale proceeds)
```

**Why TWO rows:** The 6 holding shares and 5 sold shares have different peak values:
- Holding shares: Peak anytime in the year
- Sold shares: Peak only UP TO sale date (Aug 15)

If stock price peaked AFTER Aug 15, the two groups have genuinely different peak values!

---

## Common Cases

### Case 1: All Shares Holding (No Sale)
```
Acquisition: 17 shares on May 9, 2025
Sale: None
Holding: 17 shares

Table A3: ONE row
- Nature: ESPP (17 shares)
- Initial Value: ₹1,49,128
- Closing Balance: ₹3,25,735 (all 17 shares)
- Gross Proceeds: ₹0
```

### Case 2: All Shares Sold (Nothing Holding)
```
Acquisition: 10 shares on Mar 15, 2025
Sale: All 10 shares sold on Aug 20, 2025
Holding: 0 shares

Table A3: ONE row
- Nature: RSU (10 shares) Sold
- Initial Value: ₹1,50,000
- Closing Balance: ₹0
- Gross Proceeds: ₹3,20,000 (all 10 shares)
```

### Case 3: Partial Sale (MOST IMPORTANT)
```
Acquisition: 11 shares on Nov 8, 2024
Sale: 5 shares sold on Aug 15, 2025
Holding: 6 shares

Table A3: TWO rows

Row 1 (Holding portion):
- Nature: ESPP (6 shares)
- Initial Value: ₹88,929          ← For 6 shares only
- Peak Balance: ₹XXX,XXX           ← Peak of 6 shares (anytime in year)
- Closing Balance: ₹210,770        ← 6 shares on Dec 31
- Gross Proceeds: ₹0

Row 2 (Sold portion):
- Nature: ESPP (5 shares) Sold
- Initial Value: ₹74,108          ← For 5 shares only
- Peak Balance: ₹YYY,YYY           ← Peak of 5 shares (up to Aug 15 only)
- Closing Balance: ₹0
- Gross Proceeds: ₹201,805
```

### Case 4: Future Sale (Sold After FY)
```
Acquisition: 11 shares on Nov 8, 2024
Sale: 5 shares to be sold on May 8, 2026 (FUTURE)
Holding: 11 shares as of Dec 31, 2025

Table A3 (for FY 2025-26): ONE row
- Nature: ESPP (11 shares) - Sold       ← Marked as future-sold
- Initial Value: ₹1,63,037               ← For ALL 11 shares
- Closing Balance: ₹2,10,770             ← ALL 11 shares (still holding Dec 31)
- Gross Proceeds: ₹0                     ← Nothing sold in THIS calendar year

Note: When those 5 shares actually sell in May 2026:
- They appear in Capital Gains for FY 2025-26 (advance tax planning)
- They'll create TWO rows in FY 2026-27 Table A3 (6 holding, 5 sold)
```

---

## Why Separate Rows Matter

### Problem with One Consolidated Row (WRONG)
If we combined partial sale into ONE row:
```
WRONG: ESPP (11 shares) | Initial: ₹163,037 | Closing: ₹210,770 | Proceeds: ₹201,805
```

**Issues:**
1. **Closing balance ₹210,770 for 11 shares?** No! Only 6 shares are held on Dec 31.
2. **Peak value unclear:** Did all 11 shares reach peak, or only the 6 holding shares?
3. **Misrepresents reality:** Makes it look like 11 shares are still held + sold proceeds received

### Benefits of Separate Rows (CORRECT)
1. **Accurate Peak Values:** Each row shows correct peak for that portion
2. **Clear Closing Balance:** 6 shares = ₹210,770, 5 shares = ₹0
3. **Transparent FIFO:** Can see partial sale from original lot
4. **Matches Tax Reality:** Different peak dates = different valuations

---

## Peak Value Calculation Difference

**Critical difference for partial sales:**

**Holding shares (Row 1):**
- Peak can occur ANYTIME in the calendar year (Jan 1 - Dec 31)
- Example: If stock peaked on Nov 15, these shares get that peak value

**Sold shares (Row 2):**
- Peak can occur ONLY from acquisition date to sale date
- Example: If sold on Aug 15, peak is ONLY up to Aug 15
- Any price increase AFTER Aug 15 does NOT count for sold shares

**Example:**
- Acquisition: Jan 1, 2025 - 10 shares @ $100
- Partial sale: Aug 15, 2025 - sold 5 shares when price = $150
- Dec 31 price: $200
- Peak price for YEAR: $220 on Nov 15

**Correct peak values:**
- **Holding 5 shares:** 5 × $220 × TTBR = ₹XXX (peak on Nov 15)
- **Sold 5 shares:** 5 × $150 × TTBR = ₹YYY (peak up to Aug 15 only, NOT $220!)

**If we consolidated:** Would incorrectly use $220 for all 10 shares!

---

## Peak Value Calculation Windows

The peak value calculation window depends on when the lot was acquired and whether it was sold.

### For Shares Acquired BEFORE Calendar Year

**Holding shares (NOT sold):**
- **Window:** Jan 1 (calendar year start) to Dec 31 (calendar year end)
- **Example:** Acquired Nov 8, 2024 → Peak from **Jan 1, 2025 to Dec 31, 2025**
- **Why:** Previous year prices are irrelevant for this year's Schedule FA

**Sold shares:**
- **Window:** Jan 1 (calendar year start) to Sale date
- **Example:** Acquired Nov 8, 2024, Sold Aug 15, 2025 → Peak from **Jan 1, 2025 to Aug 15, 2025**
- **Why:** Peak calculation stops at sale date (share no longer held after that)

### For Shares Acquired DURING Calendar Year

**Holding shares (NOT sold):**
- **Window:** Acquisition date to Dec 31 (calendar year end)
- **Example:** Acquired May 9, 2025 → Peak from **May 9, 2025 to Dec 31, 2025**
- **Why:** Peak starts from when shares were first held

**Sold shares:**
- **Window:** Acquisition date to Sale date
- **Example:** Acquired May 9, 2025, Sold Sep 20, 2025 → Peak from **May 9, 2025 to Sep 20, 2025**
- **Why:** Peak is only for the period shares were actually held


```python
hold_start = max(self.start_date, acq_date_str)  # Later of: Jan 1 OR acquisition
hold_end = sell_date_str if (sell_date_str and sell_date_str <= self.end_date) else self.end_date
```

### Verification

The **A3 Peak Value Details** sheet shows the exact peak calculation window and peak date for each lot. See [a3_peak_value_details.md](a3_peak_value_details.md) for details.

---

## FIFO Handling

### Question to ITRFA.in:
"As per Indian Law FIFO is there right like if we sell any share the oldest will go first, is it the same case here also?"

### ITRFA.in Answer:
"**FIFO — we use ETRADE's own Gains & Losses export as the source of which lot was sold.** That report already reflects whichever lot-relief method ETRADE itself applied when the sale executed. **We don't re-derive or override the lot order on top of it.**"

- Use E*TRADE's G&L_Expanded.xlsx acquisition dates AS-IS
- Don't re-calculate FIFO ourselves
- E*TRADE has already applied the correct lot-relief method

---

## Dividend Allocation for Partial Sales

### Question to ITRFA.in:
"For dividend handling: In your example, you put the $120 dividend on Lot 2 (the lot still held on Dec 31), with Lot 1 getting $0 since it was sold. My question is what if the dividend was paid BEFORE the Lot 1 was sold?"

### ITRFA.in Answer:
"**Dividend timing — the dividend goes to whichever lot(s) were actually held of record on the date the dividend was declared/paid, not whichever lot is still open on Dec 31.** In your example, the March dividend goes entirely to Lot 1, even though Lot 1 later shows a $0 closing balance from the June sale — that's expected, not an error. **If more than one lot is held of record on a dividend's date, the amount is split across them in proportion to shares held, not assigned to one row.**"

**Example:**
```
March 2025: Dividend $150 paid (only Lot 1 existed with 100 shares)
June 2025: Sold all Lot 1 shares (closing balance = 0)
Aug 2025: Lot 2 vested (50 shares)
Dec 31: Only Lot 2 held

Dividend allocation:
- Lot 1 (SOLD): TotGrossAmtPaidCredited = ₹12,600 (entire dividend)
                Closing Balance = ₹0
- Lot 2 (HOLDING): TotGrossAmtPaidCredited = ₹0 (didn't exist on dividend date)
                   Closing Balance = ₹XXX

This is CORRECT! Dividend stays with the lot that held shares on payment date.
```


---

## Code Location
**Lines:** 1244-1400 (separate row creation for open/sold/future-sold lots)

**Key Sections:**

---

## Verification Checklist

To verify correct Table A3 structure in Excel output:

1. ✅ **Partial sale creates TWO rows** (same acquisition date)
   - Row 1: "ESPP (X shares)" with closing balance > 0
   - Row 2: "ESPP (Y shares) Sold" with closing balance = 0

2. ✅ **Different peak values** for holding vs sold portions
   - Holding: Peak can be AFTER sale date
   - Sold: Peak is ONLY up to sale date

3. ✅ **Correct initial values** (separate for each row)
   - Holding row: Initial value for X shares
   - Sold row: Initial value for Y shares
   - Total: X + Y = original lot size

4. ✅ **Dividend allocation** matches dividend payment date
   - If dividend paid BEFORE sale: Goes to sold lot (even if closing = 0)
   - If dividend paid AFTER sale: Goes to holding lot
   - Multiple lots on dividend date: Split proportionally

---

## Summary

**CORRECT:**
- ✅ Partial sale = **TWO separate rows** (one holding, one sold)
- ✅ Each row has **different peak and closing values**
- ✅ **Never** consolidate into single row
- ✅ Dividend goes to lot **held on dividend date** (not based on Dec 31 closing)
- ✅ Use E*TRADE's lot matching from G&L export (don't re-derive FIFO)

**WRONG:**
- ❌ One row per acquisition date with reduced share count
- ❌ Combining peak values from holding and sold portions
- ❌ Assigning dividend based on closing balance instead of dividend payment date

---

**Last Updated:** 2026-08-03 (ITRFA.in email clarification)  
**Related Docs:** [closed_lots_verification.md](closed_lots_verification.md), [dividends.md](dividends.md), [capital_gains.md](capital_gains.md)
