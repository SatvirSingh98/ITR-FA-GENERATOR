# Schedule OS (Other Sources) and Schedule FSI (Foreign Source Income)

## Overview
This document explains how Schedule OS and Schedule FSI are generated for complete ITR-2 filing, covering dividend income and foreign source income reporting.

**IMPORTANT:** These schedules are for **tax calculation and reporting**, separate from Schedule FA (asset disclosure).

---

## Critical Context: Three Different Schedules

| Schedule | Purpose | Time Period | Exchange Rate | Sheet Order |
|----------|---------|-------------|---------------|-------------|
| **Schedule FA** | Asset disclosure | Calendar Year (Jan-Dec) | Exact event date TTBR | 1st, 2nd |
| **Schedule OS** | Dividend income tax | Financial Year (Apr-Mar) | Rule 115(1)(e) month-end | 3rd |
| **Schedule FSI** | Foreign income reporting | Financial Year (Apr-Mar) | Same as Schedule OS | 4th |

**Key Point:** Same dividend transaction reported in ALL THREE schedules with DIFFERENT exchange rates!

---

## Schedule OS - Other Sources Income

### What It Does
Reports dividend income from foreign stocks (RSU/ESPP holdings) as taxable income under "Income from Other Sources."

**Tax Treatment:**
- Dividends are taxed at your slab rate (30%, 20%, 10%, etc.)
- NOT a separate tax like capital gains
- Added to your total income for tax calculation

### Financial Year Period
**CRITICAL:** Schedule OS uses **Financial Year (Apr 1 - Mar 31)**, NOT calendar year!

**Example:**
```
Calendar Year 2025: Jan 1, 2025 - Dec 31, 2025 (Schedule FA)
Financial Year 2025-26: Apr 1, 2025 - Mar 31, 2026 (Schedule OS)
Assessment Year: 2026-27
```

### Exchange Rate Rule: Rule 115(1)(e)

**Rule:** For dividend income, use TTBR on **last day of month BEFORE** the dividend was declared/distributed/paid.

**Formula:**
```python
if dividend_month == January:
    specified_date = Dec 31 of previous year
else:
    specified_date = Last day of (dividend_month - 1)
```

**Examples:**
```
Dividend paid: Aug 15, 2025
Specified date: Jul 31, 2025

Dividend paid: Jan 5, 2026
Specified date: Dec 31, 2025

Dividend paid: Nov 1, 2025
Specified date: Oct 31, 2025
```

**Why Different from Schedule FA?**
- Schedule FA: Asset disclosure (exact date)
- Schedule OS: Income tax calculation (preceding month-end)
- Income-tax Rule 115 governs income computation, not asset disclosure

### Quarterly Breakup (Section 234C)

**Purpose:** Advance tax calculation - dividend income can't be taxed before it's received!

**Quarters:**
```
Q1: Apr 1 - Jun 15
Q2: Jun 16 - Sep 15
Q3: Sep 16 - Dec 15
Q4: Dec 16 - Mar 15
Q5: Mar 16 - Mar 31
```

**Logic:** Dividend assigned to quarter based on **actual payment date** (not specified date for exchange rate).

**Example:**
```
Dividend paid: Aug 15, 2025
Exchange rate date: Jul 31, 2025 (Rule 115(1)(e))
Quarterly assignment: Q2 (Jun 16 - Sep 15) ← based on Aug 15
```

**Why It Matters:**
- Section 234C allows you to skip advance tax for earlier quarters
- Dividend received in Q3 → No penalty for not paying advance tax in Q1/Q2
- Helps calculate advance tax liability accurately

### Schedule OS Sheet Structure

```
Indian Financial Year                  2025-26
-----------------------------------------------
Assessment Year                        2026-27
Total Dividend Income (USD)            480.00
Total Dividend Income (INR Rs.)        40,680
                                       
Quarter (Section 234C)                 Dividend Income (INR Rs.)
                                       
Q1 (Apr 1 - Jun 15)                    10,080
Q2 (Jun 16 - Sep 15)                   20,280
Q3 (Sep 16 - Dec 15)                   10,320
Q4 (Dec 16 - Mar 15)                   0
Q5 (Mar 16 - Mar 31)                   0
                                       
WARNINGS / NOTES
• [Any warnings about missing data]
```

### What's Included
- ✅ Dividend income from US stocks
- ✅ Quarterly breakup for advance tax
- ✅ Total in USD and INR
- ❌ Interest income (not implemented - add manually if applicable)
- ❌ Other income sources (add manually)

---

## Schedule FSI - Foreign Source Income

### What It Does
Reports ALL foreign-source income for:
1. Foreign tax credit calculation (Schedule TR)
2. DTAA (Double Taxation Avoidance Agreement) claims
3. Comprehensive foreign income disclosure

**Purpose:** Ensures you get credit for taxes paid in the US (NRA withholding) and avoid double taxation.

### Components Included

**1. Dividend Income (Foreign)**
- Source: Schedule OS
- Same amounts, same exchange rates
- Appears in both OS and FSI (correct, not duplication!)

**2. Capital Gains Income (Foreign)**
- Source: Schedule CG
- Only sales within Financial Year (Apr-Mar)
- Aggregated from all sales

**3. Total Foreign Source Income**
- Sum of dividend + capital gains
- Used for tax relief calculation

**4. Tax Paid Outside India**
- NRA withholding tax from US broker
- TODO: Currently placeholder (need to extract from Transaction History)
- Converted to INR using same exchange rate as income

**5. Tax Relief Available**
- Calculated in Schedule TR (future implementation)
- Limited to lower of: US tax paid OR Indian tax on foreign income

### Schedule FSI Sheet Structure

```
Indian Financial Year                                    2025-26
----------------------------------------------------------------
Assessment Year                                          2026-27
Dividend Income (Foreign)                                40,680
Capital Gains Income (Foreign, per Schedule CG)          1,50,000
Total Foreign Source Income                              1,90,680
Total Tax Paid Outside India                             0
Total Tax Relief Available (Schedule TR)                 0

Country Details Table:
---------------------------------------------------------------------------
Country | Code | TIN/Passport | DTAA | Div(USD) | Div(INR) | CG(INR) | Tax(USD) | Tax(INR) | Relief(INR)
USA     | 2    | [TIN]        | Art. | 480.00   | 40,680   | 150,000 | 0        | 0        | 0

WARNINGS / NOTES
• US Taxpayer Identification Number (TIN) not provided - add before filing
• [Other warnings]
```

### Country Details Table

**What Goes Here:**
- **Country:** UNITED STATES OF AMERICA (auto-filled)
- **Country Code:** 2 (USA)
- **TIN/Passport:** Your US SSN or TIN (TODO: add to config.json)
- **DTAA Article:** Article number from India-US tax treaty (placeholder)
- **Dividend Income (USD):** Total dividends in USD
- **Dividend Income (INR):** Total dividends in INR (Rule 115(1)(e) rate)
- **Capital Gains (INR):** Total capital gains in INR
- **Tax Paid (USD):** NRA withholding in USD
- **Tax Paid (INR):** NRA withholding in INR
- **Tax Relief Available (INR):** Lower of US tax or Indian tax

---

## Exchange Rate Comparison: Schedule FA vs OS/FSI

### Same Dividend, Different INR Amounts!

**Example:**
```
Dividend received: Aug 15, 2025 - $100

Schedule FA (Asset Disclosure):
  Date: Aug 15, 2025
  TTBR: 84.50
  Amount: $100 × 84.50 = Rs.8,450

Schedule OS/FSI (Income Tax):
  Specified Date: Jul 31, 2025 (Rule 115(1)(e))
  TTBR: 84.00
  Amount: $100 × 84.00 = Rs.8,400

Difference: Rs.50 due to exchange rate rule!
```

**Why Different?**
- Schedule FA: Disclose asset value on actual date (CBDT instructions)
- Schedule OS/FSI: Calculate taxable income per Income-tax Rules

**Both are correct!** Each schedule has its own exchange rate rule.

### Tool Features

**Automatic Dual Calculation:**
The tool generates **TWO dividend sheets** showing the difference:

1. **Dividends (Schedule FA)** - Exact credit date TTBR
2. **Dividends (Schedule OS)** - Rule 115(1)(e) month-end TTBR

**Columns in Each Sheet:**
- Symbol
- Date (payment date)
- Amount (USD)
- Specified Date (for Schedule OS) OR Date (for Schedule FA)
- TTBR (different for each schedule!)
- Amount (INR)

**Purpose:** Verify exchange rate calculations and reconcile between schedules.

---

## Financial Year vs Calendar Year

### Critical Distinction

**Schedule FA:**
- Period: Jan 1, 2025 - Dec 31, 2025 (Calendar Year)
- Purpose: Disclose foreign assets held during calendar year
- Reports: Assets owned on any day between Jan 1 - Dec 31

**Schedule OS/FSI:**
- Period: Apr 1, 2025 - Mar 31, 2026 (Financial Year)
- Purpose: Report taxable income for FY 2025-26
- Reports: Income received between Apr 1 - Mar 31

### Example Impact

**Dividend Timeline:**
```
Dec 15, 2024: $100 dividend paid

Schedule FA for CY 2024:
  Included: NO (before Jan 1, 2025)

Schedule FA for CY 2025:
  Included: NO (before Jan 1, 2025)

Schedule OS for FY 2024-25:
  Included: YES (between Apr 1, 2024 - Mar 31, 2025)

Schedule OS for FY 2025-26:
  Included: NO (before Apr 1, 2025)
```

**Jan-Mar Dividends:**
```
Dividend paid: Jan 15, 2026 - $100

Schedule FA for CY 2025:
  Included: NO (after Dec 31, 2025)

Schedule FA for CY 2026:
  Included: YES (in calendar year 2026)

Schedule OS for FY 2025-26:
  Included: YES (between Apr 1, 2025 - Mar 31, 2026) ← SAME FY!

Schedule OS for FY 2026-27:
  Included: NO (before Apr 1, 2026)
```

**Key Takeaway:** When filing ITR for FY 2025-26, you need:
- Schedule FA data for CY 2025 (Jan-Dec 2025)
- Schedule OS/FSI data for FY 2025-26 (Apr 2025-Mar 2026)
- These are **15 months** of data, not 12!

---

## Data Sources

### Input Files
1. **Transaction_History.csv** - Dividend transactions
   - Required columns: Date, Symbol, Amount
   - Export from E*TRADE: Accounts → Transaction History → Download
   - Export Jan 1 - Mar 31 of next year (15 months for complete FY)

2. **G&L_Expanded.xlsx** - Capital gains for FSI
   - Already used for Schedule CG
   - Tool automatically filters to Financial Year

3. **SBI TTBR CSV** - Exchange rates
   - Auto-downloaded from GitHub
   - Includes historical data for Rule 115(1)(e) calculation

### Processing Logic
```python
# Filter dividends to Financial Year
fy_start = "2025-04-01"
fy_end = "2026-03-31"
dividends_fy = dividends[(date >= fy_start) & (date <= fy_end)]

# Apply Rule 115(1)(e) exchange rate
for dividend in dividends_fy:
    if dividend.month == 1:
        specified_date = Dec 31 of previous year
    else:
        specified_date = Last day of (dividend.month - 1)
    
    ttbr = get_ttbr(specified_date)
    amount_inr = ceil(amount_usd × ttbr)
    
    # Assign to quarterly bucket based on payment date
    quarter = get_quarter(dividend.date)
    quarterly_total[quarter] += amount_inr
```

---

## AMD Stock and Dividends

**IMPORTANT:** AMD does **NOT** pay dividends on its common stock.

**For AMD Employees:**
- Schedule OS will show: Total Dividend Income = 0
- Schedule FSI will show: Dividend Income (Foreign) = 0
- Only Capital Gains Income will appear in FSI
- No quarterly breakup needed
- Sheets still generated with zeros (for compliance)

**If You Hold Other Stocks:**
- Apple (AAPL): Pays quarterly dividends
- Microsoft (MSFT): Pays quarterly dividends
- Intel (INTC): Pays quarterly dividends
- These will appear in Schedule OS/FSI

---

## Future Enhancements (TODO)

### 1. NRA Withholding Tax Extraction
**Current:** Placeholder (shows 0)
**Needed:** Extract from Transaction History CSV
- Filter transactions for "NRA Withholding" or "Tax Withheld"
- Match to dividend transactions
- Convert to INR using Rule 115(1)(e) rate
- Populate "Tax Paid Outside India" field

### 2. US TIN/SSN Configuration
**Current:** Not collected
**Needed:** Add to config.json
```json
{
  "us_taxpayer_info": {
    "tin_or_ssn": "XXX-XX-XXXX",
    "passport_number": ""  // If no TIN/SSN
  }
}
```

### 3. Schedule TR (Tax Relief)
**Current:** Placeholder only
**Needed:** Calculate foreign tax credit
- Lower of: US tax paid OR Indian tax on foreign income
- Relief claimed under Section 90/91
- DTAA article reference

### 4. DTAA Article Mapping
**Current:** Placeholder
**Needed:** India-US tax treaty article numbers
- Dividend income: Article X
- Capital gains: Article XIII
- User configuration or auto-mapping

---

## Troubleshooting

### "No dividend activity found"
**Cause:** No dividends in Financial Year (Apr-Mar)
**Action:** Normal if you only hold AMD (no dividends)

### "Total foreign income is only capital gains"
**Status:** Expected for AMD employees
**Reason:** AMD doesn't pay dividends, only capital gains from sales

### Schedule OS shows different amount than Schedule FA
**Status:** CORRECT behavior!
**Reason:** Different exchange rate rules (exact date vs Rule 115(1)(e))
**Action:** Both amounts are correct for their respective purposes

### Missing Jan-Mar dividends in Schedule OS
**Cause:** Transaction History exported for calendar year only
**Solution:** Export 15 months (Jan 1, 2025 - Mar 31, 2026) instead of 12

### Quarterly breakup doesn't match total
**Cause:** Possible rounding differences
**Check:** Sum of Q1+Q2+Q3+Q4+Q5 should equal total
**Action:** Report as GitHub issue if difference > Rs.5

### US TIN/Passport field empty
**Status:** Expected (not yet implemented)
**Action:** Manually add your SSN/TIN before filing ITR
**Future:** Will be added to config.json

---

## Compliance Notes

### What You Must Add Manually

**Before filing ITR-2:**
1. ✅ US TIN/SSN in Schedule FSI country details
2. ✅ Verify quarterly breakup totals
3. ✅ Add any other dividend/interest income (non-US sources)
4. ✅ Verify NRA withholding amounts (when implemented)
5. ✅ Complete Schedule TR if claiming foreign tax credit

### What the Tool Does Automatically

**Schedule OS:**
- ✅ Total dividend income (USD & INR)
- ✅ Quarterly breakup (Section 234C)
- ✅ Rule 115(1)(e) exchange rate
- ✅ Financial Year filtering

**Schedule FSI:**
- ✅ Dividend income aggregation
- ✅ Capital gains aggregation
- ✅ Total foreign source income
- ✅ Country code (USA = 2)
- ✅ Financial Year filtering

### What Needs Your Input

**Not Yet Automated:**
- ❌ US TIN/SSN (add to config.json - future)
- ❌ NRA withholding tax (extract from Transaction History - future)
- ❌ DTAA article numbers (add to config - future)
- ❌ Schedule TR calculation (foreign tax credit - future)
- ❌ Interest income from foreign sources (add manually)

---

## Example: Complete Flow

### Input Data
**Transaction History (FY 2025-26):**
```csv
Date,Symbol,Description,Amount
2025-06-15,AAPL,Cash Dividend,25.00
2025-09-15,AAPL,Cash Dividend,25.00
2025-12-15,AAPL,Cash Dividend,25.00
2026-03-15,AAPL,Cash Dividend,25.00
```

**Capital Gains (FY 2025-26):**
- Sale on 2025-08-15: Rs.1,50,000 gain

### Exchange Rate Calculation (Rule 115(1)(e))

```
Jun 15 dividend → May 31 TTBR = 84.00
Sep 15 dividend → Aug 31 TTBR = 85.00
Dec 15 dividend → Nov 30 TTBR = 85.50
Mar 15 dividend → Feb 28 TTBR = 86.00
```

### Schedule OS Output

```
Total Dividend Income (USD): 100.00
Total Dividend Income (INR): 34,050

Quarterly Breakup:
Q1 (Apr 1 - Jun 15):     Rs.2,100  ($25 × 84.00)
Q2 (Jun 16 - Sep 15):    Rs.2,125  ($25 × 85.00)
Q3 (Sep 16 - Dec 15):    Rs.2,138  ($25 × 85.50)
Q4 (Dec 16 - Mar 15):    Rs.2,150  ($25 × 86.00)
Q5 (Mar 16 - Mar 31):    Rs.0
```

### Schedule FSI Output

```
Dividend Income (Foreign):                Rs.34,050
Capital Gains Income (Foreign):           Rs.1,50,000
Total Foreign Source Income:              Rs.1,84,050
Tax Paid Outside India:                   Rs.0 (TODO)
Tax Relief Available:                     Rs.0
```

---

## Related Documentation

- **Schedule FA:** See [docs/table_a2_vs_a3.md](table_a2_vs_a3.md)
- **Dividends:** See [docs/dividends.md](dividends.md)
- **Capital Gains:** See [docs/capital_gains.md](capital_gains.md)
- **Exchange Rates:** See [docs/exchange_rates.md](exchange_rates.md) (if exists)

---

## Sources and Credits

- **Income-tax Rule 115(1)(e):** Last day of month before dividend month
  - Source: Income Tax Rules, 1962
- **Section 234C:** Advance tax quarterly periods
  - Source: Income Tax Act, 1961
- **DTAA:** India-US Double Taxation Avoidance Agreement
  - Source: https://www.incometaxindia.gov.in/pages/international-taxation/dtaa.aspx
- **ITRFA.in:** Schedule OS and FSI guidance
  - https://itrfa.in/blog/schedule-os-dividend-income
  - https://itrfa.in/blog/schedule-fa-table-a2-vs-a3

---

## Summary

✅ **Schedule OS (Other Sources):**
- Dividend income taxed at slab rate
- Rule 115(1)(e) exchange rate (month-end before)
- Quarterly breakup for advance tax
- Financial Year period (Apr-Mar)

✅ **Schedule FSI (Foreign Source Income):**
- Dividend + Capital Gains aggregation
- Tax paid outside India tracking
- DTAA compliance reporting
- Financial Year period (Apr-Mar)

✅ **Key Features:**
- Automatic dual exchange rate calculation
- Financial Year filtering (different from Schedule FA)
- Quarterly breakup per Section 234C
- Professional Excel formatting
- Side-by-side comparison sheets

❌ **Future Enhancements:**
- NRA withholding extraction
- US TIN/SSN configuration
- Schedule TR calculation
- DTAA article mapping

**This tool handles Schedule FA + OS + FSI for complete ITR-2 filing!**
