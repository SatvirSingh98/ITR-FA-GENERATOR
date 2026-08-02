# Table A3 Structure - One Row Per Acquisition Date

## Overview
Table A3 (Equity Interest) in Schedule FA uses **ONE row per acquisition date (lot)**, NOT separate rows for sold vs holding portions.

**Source:** ITR e-filing portal validation, ITRFA.in guidance

---

## The Rule: One Row Per Lot

**Each acquisition date = ONE row, with:**
- **Initial Value of Investment**: Total value for ALL shares originally acquired (sold + holding)
- **Closing Balance**: Value of shares STILL HOLDING from that lot (as of Dec 31)
- **Gross Proceeds**: Proceeds from shares SOLD from that lot (in calendar year)

**Key Insight:** Both "Closing Balance" and "Gross Proceeds" can be NON-ZERO in the SAME row (partial sale)

---

## Example: Partial Sale

### Scenario
- **Acquisition**: Nov 8, 2024 - 11 ESPP shares @ $147.95/share
- **Sale**: Sold 5 shares in May 2026 for $451.11 total
- **Holding**: Still holding 6 shares as of Dec 31, 2025

### WRONG Approach (OLD CODE - 2 rows)
```
Row 1: ESPP (6 shares)  | Acq: Nov 8, 2024 | Initial: ₹88,929  | Closing: ₹210,770 | Proceeds: ₹0
Row 2: ESPP (5 shares)  | Acq: Nov 8, 2024 | Initial: ₹74,108  | Closing: ₹0       | Proceeds: ₹201,805
```
**Problem:** TWO rows for same acquisition date (split by current status)

### CORRECT Approach (NEW CODE - 1 row)
```
Row 1: ESPP (11 shares) | Acq: Nov 8, 2024 | Initial: ₹163,037 | Closing: ₹210,770 | Proceeds: ₹201,805
```
**Correct:** ONE row for the acquisition date, shows BOTH holding AND sold portions

---

## Field Calculations

### Initial Value of Investment
**Definition:** Total value of ALL shares originally acquired from this lot

**Formula:**
```python
total_original_shares = shares_holding + shares_sold
initial_value = total_original_shares × unit_cost_usd × acq_date_ttbr
```

**Example:**
- 11 shares @ $147.95 × 83.15 TTBR = ₹1,63,037

### Closing Balance
**Definition:** Value of shares STILL HOLDING from this lot as of Dec 31

**Formula:**
```python
closing_value = shares_still_holding × unit_cost_usd × dec31_ttbr
```

**Example:**
- 6 shares (still holding) @ $147.95 × 89.47 TTBR = ₹2,10,770

### Gross Proceeds
**Definition:** Proceeds from shares SOLD from this lot in the calendar year

**Formula:**
```python
proceeds_inr = sum(sale_proceeds_usd × sale_date_ttbr) for all sales from this lot
```

**Example:**
- 5 shares sold for $451.11 × 89.47 TTBR = ₹2,01,805
- Note: If sold in 2026, proceeds would be 0 for 2025 Table A3

---

## Implementation Details

### Grouping Key
Lots are grouped by:
```python
key = (symbol, acq_date, plan_type)
```

**Example:**
- (AMD, 2024-11-08, ESPP) → All ESPP shares from Nov 8, 2024
- (AMD, 2025-09-15, Rest. Stock) → All RSU shares from Sep 15, 2025

### Data Sources
1. **Sellable sheet (ByStatus_expanded.xlsx)**: Shares currently holding
2. **G&L_Expanded.xlsx (current FY)**: Shares sold in calendar year
3. **G&L_Expanded.xlsx (future)**: Shares to be sold after FY (still holding now)

### Consolidation Logic
```python
for each lot_group:
    total_qty = open_qty + sold_qty
    
    # Initial value for ALL original shares
    initial_val = calculate_value(total_qty, acq_date)
    
    # Closing balance for REMAINING shares only
    if open_qty > 0:
        close_val = calculate_value(open_qty, dec_31)
    else:
        close_val = 0
    
    # Proceeds for SOLD shares only
    proceeds = sum(sold_details.proceeds_inr)
```

---

## Common Cases

### Case 1: All Shares Holding (No Sale)
```
Acquisition: 17 shares on May 9, 2025
Sale: None
Holding: 17 shares

Table A3 Row:
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

Table A3 Row:
- Nature: RSU (10 shares)
- Initial Value: ₹1,50,000
- Closing Balance: ₹0
- Gross Proceeds: ₹3,20,000 (all 10 shares)
```

### Case 3: Partial Sale (MOST IMPORTANT)
```
Acquisition: 11 shares on Nov 8, 2024
Sale: 5 shares sold on Aug 15, 2025
Holding: 6 shares

Table A3 Row:
- Nature: ESPP (11 shares)        ← Shows TOTAL original
- Initial Value: ₹1,63,037         ← For ALL 11 shares
- Closing Balance: ₹2,10,770       ← For 6 shares holding
- Gross Proceeds: ₹2,01,805        ← For 5 shares sold
```

### Case 4: Future Sale (Sold After FY)
```
Acquisition: 11 shares on Nov 8, 2024
Sale: 5 shares to be sold on May 8, 2026 (FUTURE)
Holding: 11 shares as of Dec 31, 2025

Table A3 Row (for FY 2025-26):
- Nature: ESPP (11 shares)         ← Shows TOTAL (includes future-sold)
- Initial Value: ₹1,63,037         ← For ALL 11 shares
- Closing Balance: ₹2,10,770       ← For ALL 11 shares (still holding Dec 31)
- Gross Proceeds: ₹0               ← Nothing sold in THIS calendar year

Note: When those 5 shares actually sell in May 2026:
- They appear in Capital Gains for FY 2025-26 (advance tax planning)
- They'll reduce closing balance in FY 2026-27 Table A3
```

---

## Why This Matters

### Problem with Old Approach (2 rows)
1. **ITR Portal Rejection**: Portal may reject duplicate acquisition dates
2. **Confusing Nature**: "ESPP (6 shares)" and "ESPP (5 shares)" don't indicate same lot
3. **Initial Value Wrong**: Split across two rows instead of showing total lot value
4. **FIFO Unclear**: Can't see that 5 sold shares came from an 11-share lot

### Benefits of New Approach (1 row)
1. **Portal Compliant**: One row per acquisition date
2. **Clear Lot Tracking**: Shows total lot size in nature
3. **Correct Initial Value**: Reflects full original investment
4. **FIFO Visible**: Can see partial sale from original lot
5. **Matches E*TRADE**: E*TRADE shows lots by acquisition date

---

## Code Location
**File:** `itr_fa_engine.py`  
**Lines:** 1232-1340 (lot collection and consolidation)

**Key Functions:**
- Lines 1248-1281: Parse open lots (Sellable sheet)
- Lines 1283-1330: Parse sold lots (G&L current FY)
- Lines 1332-1363: Parse future-sold lots (G&L future)
- Lines 1365-1412: Consolidate lot_groups into equity_tranches

---

## Verification
To verify correct Table A3 structure:
1. Check Table A3 sheet in Excel output
2. For each acquisition date, should see ONLY ONE row
3. If partial sale: Both ClosingBalance > 0 AND TotGrossProceeds > 0
4. NatureOfEntity should show TOTAL original shares (not just holding)
5. Initial Value should be for ALL shares (sold + holding)

---

**Last Updated:** 2026-08-02
**Related Docs:** [closed_lots_verification.md](closed_lots_verification.md), [capital_gains.md](capital_gains.md)
