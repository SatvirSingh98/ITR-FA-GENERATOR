# ITRFA.in Official Clarifications (2026-08-03)

## Overview
This document contains official guidance from ITRFA.in received via email on 2026-08-03. These clarifications address critical implementation questions about Schedule FA Table A3 structure, FIFO handling, and dividend allocation.

**Source:** Email response from ITRFA.in support team  
**Date:** 2026-08-03

---

## Question 1: Multiple Rows for Same Acquisition Date

### Question Asked:
"I see that in A3 you have mentioned multiple rows for the shares with acquisition date of 2024-11-08 as there was partial sale for this, is this format correct? I thought like we need to have only one row per acquisition date per entity type and if there is any sale then we need to decrease the shares, correct the peak value and then provide the gross proceeds (I know this is not applicable to me yet)."

### ITRFA.in Answer:
"**Multiple A3 rows for the same acquisition date — yes, correct, and intentional.** A holding acquired on one date but partly sold shows as two separate Table A3 rows: one for the shares still held (closing value = your Dec 31 balance) and one for the shares sold (closing value = 0, gross proceeds shown). **We never collapse these into a single row with a reduced share count, because the two portions have genuinely different peak and closing values through the year — combining them would misstate both.**"

### Key Takeaways:
✅ **Partial sale = TWO separate rows** (one for holding, one for sold)  
✅ **Same acquisition date appears TWICE** (intentional and correct)  
✅ **Different peak values:** Holding portion can peak AFTER sale, sold portion peaks ONLY up to sale date  
✅ **Never consolidate** into single row with reduced share count  

### Implementation Impact:
- Reverted from consolidated one-row approach (commit aa80b01)
- Back to separate-row approach for partial sales
- Each row tracks its own peak and closing values independently

---

## Question 2: FIFO Lot Matching

### Question Asked:
"As per Indian Law FIFO is there right like if we sell any share the oldest will go first, is it the same case here also? How is this handled here because say if I sell the latest shares and old ones are still I am holding will we need to decrease the shares from the oldest holding?"

### ITRFA.in Answer:
"**FIFO — we use ETRADE's own Gains & Losses export as the source of which lot was sold.** That report already reflects whichever lot-relief method ETRADE itself applied when the sale executed. **We don't re-derive or override the lot order on top of it.**"

### Key Takeaways:
✅ **Use E*TRADE's G&L report as-is** - don't re-calculate FIFO ourselves  
✅ **E*TRADE has already applied** correct lot-relief method  
✅ **Don't override** the lot matching from E*TRADE  
✅ **Acquisition dates in G&L** are authoritative  

### Implementation Impact:
- Use "Date Acquired" column from G&L_Expanded.xlsx directly
- No FIFO re-calculation needed on our side
- Trust E*TRADE's lot matching logic

---

## Question 3: Dividend Allocation Timing

### Question Asked:
"As per Schedule FA Table A2 vs A3 — What's the Difference (with Examples) | ITRFA.in for dividend handling: In your example, you put the $120 dividend on Lot 2 (the lot still held on Dec 31), with Lot 1 getting $0 since it was sold. My question is what if the dividend was paid BEFORE the Lot 1 was sold?

Example:
- March 2025: Dividend $150 paid (only Lot 1 existed and held 100 shares)
- June 2025: Sold all Lot 1 shares
- Aug 2025: Lot 2 vested (50 shares)
- Dec 31: Only Lot 2 held (Lot 1 closing = 0)

Should the $150 dividend go on:
  a) Lot 1 (held shares when dividend was actually paid), OR
  b) Lot 2 (the only lot with closing balance > 0)?

Also, if multiple lots are held on Dec 31, is the dividend split proportionally across them or put on one 'representative row'?"

### ITRFA.in Answer:
"**Dividend timing — the dividend goes to whichever lot(s) were actually held of record on the date the dividend was declared/paid, not whichever lot is still open on Dec 31.** In your example, the March dividend goes entirely to Lot 1, even though Lot 1 later shows a $0 closing balance from the June sale — that's expected, not an error. **If more than one lot is held of record on a dividend's date, the amount is split across them in proportion to shares held, not assigned to one row.**"

### Key Takeaways:
✅ **Dividend follows payment date** - not Dec 31 closing balance  
✅ **Lot sold AFTER dividend** still gets the dividend (closing = 0 is OK)  
✅ **Multiple lots on dividend date** = split proportionally by shares held  
✅ **Not a "representative row"** assignment - each lot gets its proportional share  

### Example (from question):
```
March 2025: Dividend $150 paid (only Lot 1 with 100 shares existed)
June 2025: Sold all Lot 1 shares
Aug 2025: Lot 2 vested (50 shares)
Dec 31: Only Lot 2 held

Table A3:
Lot 1 (SOLD):
  - Closing Balance: ₹0
  - TotGrossAmtPaidCredited: ₹12,600 (entire $150 dividend)
  - TotGrossProceeds: ₹XXX,XXX
  ✓ CORRECT! Dividend stays with lot that held shares on payment date.

Lot 2 (HOLDING):
  - Closing Balance: ₹XXX,XXX
  - TotGrossAmtPaidCredited: ₹0 (didn't exist on dividend date)
  - TotGrossProceeds: ₹0
```

### Implementation Impact:
- Our current dividend allocation (lines 1436-1500) is **CORRECT**
- Allocates based on holdings on actual dividend payment date
- Handles partial sales: reduces shares if sold before dividend
- Proportional split when multiple lots held on dividend date

---

## Summary of Changes Required

### ✅ Already Correct (No changes needed):
1. **FIFO handling** - Using E*TRADE's G&L acquisition dates directly
2. **Dividend allocation** - Based on holdings on dividend payment date, proportional split

### ❌ Required Revert:
1. **Table A3 structure** - Reverted from ONE consolidated row to TWO separate rows for partial sales

---

## Implementation Status

| Area | Status | Commit/Action |
|------|--------|---------------|
| Table A3 structure | ✅ Reverted | Reverted commit aa80b01, back to separate rows |
| FIFO handling | ✅ Correct | No changes needed |
| Dividend allocation | ✅ Correct | No changes needed (already implemented in commit 5ffd0be) |
| Documentation | ✅ Updated | This file + table_a3_structure.md + README.md |

---

## Related Documentation

- **Table A3 Structure:** [table_a3_structure.md](table_a3_structure.md) - Detailed explanation with examples
- **Dividend Allocation:** [dividends.md](dividends.md) - Complete dividend handling guide
- **FIFO Lot Matching:** Covered in [capital_gains.md](capital_gains.md)

---

## Contact Information

**ITRFA.in Support:** https://itrfa.in/  
**Clarifications Source:** Email dated 2026-08-03

---

**Last Updated:** 2026-08-03  
**Applies To:** ITR_FA_GENERATOR version as of August 2026
