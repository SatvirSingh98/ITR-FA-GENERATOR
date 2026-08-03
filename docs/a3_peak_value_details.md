# A3 Peak Value Details Sheet

## Overview
The **A3 Peak Value Details** sheet provides a detailed breakdown of how peak values are calculated for each lot in Table A3. This sheet shows the exact date when each lot reached its peak value, the calculation window used, and the price/TTBR details.

**Sheet Name:** `A3 Peak Value Details`  
**Location:** Excel output, after "A2 Peak Calculation" sheet  
**Purpose:** Audit trail and verification of peak value calculations

---

## Why This Sheet Exists

Schedule FA requires reporting the **peak value** (highest value during the period) for each holding. However:
- Different lots peak on **different dates**
- Peak calculation windows **vary by lot** (acquisition date and sale date affect the window)
- Peak value = shares × price on peak date × TTBR on peak date

This sheet makes the peak calculation **transparent and verifiable**.

---

## Columns Explained

| Column | Description | Example |
|--------|-------------|---------|
| **Nature of Entity** | Lot description (type, quantity, status) | "ESPP (17 shares)" |
| **Acquisition Date** | Date shares were acquired/vested | 2025-05-09 |
| **Quantity** | Number of shares in this lot | 17 |
| **Peak Calculation Window Start** | Start date for peak search | 2025-05-09 |
| **Peak Calculation Window End** | End date for peak search | 2025-12-31 |
| **Peak Date** | Actual date when peak occurred | 2025-10-29 |
| **Peak Price (USD)** | Stock price on peak date | $264.33 |
| **Peak TTBR** | SBI TTBR on peak date | 87.80 |
| **Peak Value per Share (INR)** | Price × TTBR | ₹23,208.17 |
| **Peak Value Total (INR)** | Quantity × Peak per share | ₹3,94,539 |

---

## Peak Calculation Window Rules

The peak calculation window depends on **when the lot was acquired** and **whether it was sold**:

### For Shares Acquired BEFORE Calendar Year (e.g., 2024)

**Holding shares (NOT sold):**
- **Window Start:** Jan 1, 2025 (calendar year start)
- **Window End:** Dec 31, 2025 (calendar year end)
- **Example:** Acquired Nov 8, 2024 → Peak from **Jan 1, 2025 to Dec 31, 2025**

**Sold shares:**
- **Window Start:** Jan 1, 2025 (calendar year start)
- **Window End:** Sale date
- **Example:** Acquired Nov 8, 2024, Sold Aug 15, 2025 → Peak from **Jan 1, 2025 to Aug 15, 2025**

### For Shares Acquired DURING Calendar Year (e.g., 2025)

**Holding shares (NOT sold):**
- **Window Start:** Acquisition date
- **Window End:** Dec 31, 2025 (calendar year end)
- **Example:** Acquired May 9, 2025 → Peak from **May 9, 2025 to Dec 31, 2025**

**Sold shares:**
- **Window Start:** Acquisition date
- **Window End:** Sale date
- **Example:** Acquired May 9, 2025, Sold Sep 20, 2025 → Peak from **May 9, 2025 to Sep 20, 2025**

---

## Why Different Lots Peak on Different Dates

### Case 1: Same Peak Date for Multiple Lots

If all lots have overlapping windows that include the same peak date:

```
Example Output:
ESPP (6 shares)   | Acq: 2024-11-08 | Window: 2025-01-01 to 2025-12-31 | Peak: 2025-10-29
ESPP (17 shares)  | Acq: 2025-05-09 | Window: 2025-05-09 to 2025-12-31 | Peak: 2025-10-29
RSU (14 shares)   | Acq: 2025-08-09 | Window: 2025-08-09 to 2025-12-31 | Peak: 2025-10-29
```

**Why same peak?** All three windows include Oct 29, 2025, and that was the highest price day.

### Case 2: Different Peak Dates

If a lot was sold BEFORE the overall peak, it has a different peak:

```
Example Output:
RSU (26 shares) Sold | Acq: 2024-09-15 | Window: 2025-01-01 to 2025-08-15 | Peak: 2025-07-22
ESPP (6 shares)      | Acq: 2024-11-08 | Window: 2025-01-01 to 2025-12-31 | Peak: 2025-10-29
```

**Why different?** The sold lot's window ended Aug 15, so it couldn't reach the Oct 29 peak. Its highest price was on Jul 22.

### Case 3: Late-Acquired Lots

If a lot was acquired AFTER an early peak:

```
Example Output:
ESPP (17 shares) | Acq: 2025-05-09 | Window: 2025-05-09 to 2025-12-31 | Peak: 2025-10-29
ESPP (15 shares) | Acq: 2025-11-07 | Window: 2025-11-07 to 2025-12-31 | Peak: 2025-11-12
```

**Why different?** The second lot was acquired on Nov 7, AFTER the Oct 29 peak. Its window starts Nov 7, so its peak is Nov 12.

---

## Real-World Example

**Scenario:**
- Stock peaked at **$264.33 on Oct 29, 2025** (overall year peak)
- Stock was **$258.89 on Nov 12, 2025** (later peak, lower price)
- You have 2 ESPP lots:
  - Lot A: Acquired May 9, 2025 (17 shares)
  - Lot B: Acquired Nov 7, 2025 (15 shares)

**Peak Calculation:**

**Lot A (Acquired May 9):**
- Window: May 9, 2025 → Dec 31, 2025
- Includes Oct 29 peak → **Peak: Oct 29 at $264.33**
- Peak Value: 17 × $264.33 × 87.80 = **₹3,94,539**

**Lot B (Acquired Nov 7):**
- Window: Nov 7, 2025 → Dec 31, 2025
- Does NOT include Oct 29 (acquired after) → **Peak: Nov 12 at $258.89**
- Peak Value: 15 × $258.89 × 88.20 = **₹3,42,511**

**Result in Sheet:**
```
ESPP (17 shares) | 2025-05-09 | 2025-05-09 to 2025-12-31 | 2025-10-29 | $264.33 | 87.80 | ₹3,94,539
ESPP (15 shares) | 2025-11-07 | 2025-11-07 to 2025-12-31 | 2025-11-12 | $258.89 | 88.20 | ₹3,42,511
```

---

## How to Use This Sheet

### Verification

1. **Check Peak Dates Make Sense:**
   - Are peak dates within the calculation window? ✓
   - Do sold lots have earlier peaks than holding lots? (expected)
   - Do late-acquired lots have different peaks? (expected)

2. **Verify Peak Values:**
   - Peak Value Total (INR) = Quantity × Peak per Share (INR)
   - Peak per Share (INR) = Peak Price (USD) × Peak TTBR
   - Cross-check against Table A3 "Peak Balance During Period" column

3. **Cross-Reference with Daily Rates:**
   - Open the "[Calendar Year] - Daily Rates" sheet
   - Find the peak date row
   - Verify the stock price and TTBR match

### Example Verification

**From A3 Peak Value Details:**
```
ESPP (17 shares) | Peak Date: 2025-10-29 | Peak Price: $264.33 | TTBR: 87.80
```

**Check in "2025 - Daily Rates" sheet:**
```
Date       | AMD Stock Price (USD) | SBI TTBR Rate | AMD Value per Share (INR)
2025-10-29 | 264.33                | 87.80         | 23,208.17
```

**✓ Match!** The peak calculation is correct.

### Audit Trail

This sheet serves as proof for:
- **Tax audits:** "How did you calculate peak value?"
- **CA review:** "Which date did each lot peak?"
- **ITR filing:** "Why are two lots' peak values different?"

---

## Special Cases

### Unvested RSUs (Beneficial Interest)

Unvested RSUs are **excluded** from this sheet because:
- They are reported in Table A3 as "Beneficial Interest"
- Peak value is calculated differently (uses full calendar year window)
- Initial value = ₹0 (not acquired yet)

### Multiple Sales from Same Lot (Partial Sales)

If a lot has partial sales, it appears as **TWO rows** in Table A3 and this sheet:

**Example:**
- Acquired 11 shares on Nov 8, 2024
- Sold 5 shares on Aug 15, 2025
- Holding 6 shares on Dec 31, 2025

**A3 Peak Value Details shows:**
```
ESPP (6 shares)      | 2024-11-08 | 2025-01-01 to 2025-12-31 | Peak: 2025-10-29
ESPP (5 shares) Sold | 2024-11-08 | 2025-01-01 to 2025-08-15 | Peak: 2025-07-22
```

**Why different peaks?** The sold portion's window ended Aug 15 (before Oct 29 peak).

---

## Calculation Formula

The tool calculates peak value using this algorithm:

```python
# For each lot:
1. Determine window:
   - Start: max(Jan 1, acquisition_date)
   - End: sale_date if sold, else Dec 31

2. For each trading day in window:
   - Calculate: shares × price_on_day × ttbr_on_day

3. Find maximum value across all days
   - That day = Peak Date
   - That value = Peak Value Total (INR)

4. Extract peak details:
   - Peak Price (USD) = stock price on peak date
   - Peak TTBR = SBI TTBR on peak date
   - Peak per Share = price × TTBR
```

---

## Code Reference

**File:** `itr_fa_engine.py`

**Peak Calculation:** Lines 1059-1086
```python
# Calculate peak value and details
peak_idx = window['Valuation_Per_Share_INR'].idxmax()
peak_val = round(qty * window['Valuation_Per_Share_INR'].max(), 2)

peak_row = window.loc[peak_idx]
peak_date = peak_row['Date']
peak_price_usd = peak_row['Stock_Close_USD']
peak_ttbr = peak_row['TTBR']
peak_per_share_inr = peak_row['Valuation_Per_Share_INR']
```

**Sheet Generation:** Lines 1821-1839
```python
# Create Peak Value Details sheet
peak_details_data = []
for tranche in equity_tranches:
    peak_info = tranche.get('_peak_details', {})
    peak_details_data.append({
        'Peak Date': peak_info.get('peak_date', ''),
        'Peak Price (USD)': round(peak_info.get('peak_price_usd', 0), 2),
        # ... other fields
    })
df_peak_details = pd.DataFrame(peak_details_data)
```

---

## Common Questions

### Q: Why do some lots have the same peak date?
**A:** Their calculation windows overlap and include the same highest-price day.

### Q: Why does a sold lot have a lower peak than a holding lot?
**A:** The sold lot's window ended at the sale date, before the overall year peak occurred.

### Q: Can I use this to verify my Table A3 peak values?
**A:** Yes! Peak Value Total (INR) in this sheet = "Peak Balance During Period" in Table A3.

### Q: What if I sold shares in a previous year?
**A:** Those don't appear in this year's Schedule FA. Only holdings during the current calendar year are included.

### Q: Does this sheet go to the ITR portal?
**A:** No. This is a **reference sheet** for your records and CA review. Only Table A2/A3 CSVs/JSON go to the portal.

---

## Related Documentation

- **Table A3 Structure:** [table_a3_structure.md](table_a3_structure.md)
- **Peak Calculation Logic:** This file
- **Daily Rates Sheet:** Shows stock prices and TTBR for all trading days

---

**Last Updated:** 2026-08-03  
**Applies To:** ITR_FA_GENERATOR version as of August 2026
