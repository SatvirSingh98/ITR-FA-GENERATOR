# Capital Gains Calculation

## Overview
The **Capital Gains** sheet calculates tax liability on stock sales, categorized as Long-Term Capital Gains (LTCG) or Short-Term Capital Gains (STCG) based on holding period.

**Sources:** [ITRFA.in Schedule CG Blog](https://itrfa.in/blog/schedule-cg-rsu-espp) | [ITRFA.in SBI TTBR Rule 115](https://itrfa.in/blog/sbi-ttbr-rule-115)

---

## CRITICAL: Exchange Rate Rule - Income-tax Rule 115(1)(f)

**Schedule CG uses a DIFFERENT exchange rate rule than Schedule FA!**

### Rule 115(1)(f) for Capital Gains
**"For income chargeable under the head 'Capital gains', the specified date is the last day of the month immediately preceding the month in which the capital asset is transferred (sold)"**

**CRITICAL POINTS:**
1. Use **last day of month BEFORE sale month** (NOT exact sale date!)
2. Use the **SAME rate** for BOTH proceeds AND cost of acquisition
3. This is DIFFERENT from Schedule FA which uses exact dates

**Examples:**
- Sale on Aug 15 → Use **Jul 31** TTBR for BOTH proceeds and cost basis
- Sale on Nov 1 → Use **Oct 31** TTBR for BOTH proceeds and cost basis
- Sale on Jan 1 → Use **Dec 31 (previous year)** TTBR for BOTH proceeds and cost basis

**Why it matters:**
- Form 16 uses Rule 115(1)(a): Last day of month BEFORE vest month
- Schedule FA uses exact date (per CBDT filing instructions)
- Schedule CG uses last day of month BEFORE sale month (per Rule 115(1)(f))
- **All three are different dates with different rates!**

**Common mistake:** Using exact sale/acquisition dates (WRONG!)

**Implementation:** Lines 1552-1602 in `itr_fa_etrade.py`

---

## Tax Classification (Unlisted Securities)

### Foreign Company Shares = UNLISTED Securities
RSU/ESPP shares of foreign companies (e.g., AMD) are **unlisted securities** for Indian tax purposes (no STT paid on Indian exchange).

**Threshold:** 24 months (NOT 12 months which applies to STT-paid Indian listed equity)

### Holding Period Calculation
**CRITICAL: Use calendar months, NOT day count!**
- 24 months can be 730 OR 731 days depending on leap year
- Sale on 24-month anniversary = STILL short-term (per Section 2(42A): "not more than 24 months")
- Day count approximation (730 days) FAILS in leap years

**Example:**
```
Acquired: Jan 10, Year 1
Sold: Jan 10, Year 3  (exactly 24 months later)
Classification: STCG (not "more than" 24 months)
```

### Tax Rates & Sections

#### Long-Term Capital Gains (LTCG)
- **Holding Period:** > 24 months
- **Section:** 112
- **Tax Rate:** 12.5%
- **Indexation:** NONE (per Finance Act {YEAR-1} for transfers on/after July 23, {YEAR-1}; check with CA for earlier sales)
- **NOT applicable:** Section 112A (that's for STT-paid Indian listed equity)

#### Short-Term Capital Gains (STCG)
- **Holding Period:** ≤ 24 months
- **Section:** 48
- **Tax Rate:** 31.2% (slab rate: 30% + 4% cess)
- **NOT applicable:** Section 111A (that's for STT-paid Indian listed equity)

**Calculation:** Always rounded UP using `math.ceil()`

**Implementation:** Lines 1525-1541 in `itr_fa_etrade.py`

---

## ESPP Cost Basis - Section 49(2AA)

### The Rule
**Section 49(2AA):** For ESPP shares, cost of acquisition = **FMV on purchase date** (already taxed as perquisite), NOT the discounted price you paid.

### Why It Matters
**E*TRADE reports:**
- "Adjusted Cost Basis" = discounted purchase price (e.g., $118.59 with 15% discount)

**Indian Tax Law requires:**
- Cost basis = FMV on purchase date (e.g., $152.39)
- The discount was already taxed as perquisite in Form 16

**Impact:**
- Using discounted price = **DOUBLE TAXATION** of the discount amount!
- For 15% ESPP discount on large sale: thousands of rupees in overpaid tax

**Example:**
```
ESPP Purchase: 100 shares at 15% discount
FMV: $152.39/share → Total FMV = $15,239
Discounted Price: $118.59/share → Paid = $11,859
Discount: $3,380 (already taxed as salary perquisite)

WRONG cost basis: $11,859 → Capital gain overstated by $3,380
CORRECT cost basis: $15,239 → No double taxation
```

**RSU vs ESPP:**
- **RSU:** "Adjusted Cost Basis Per Share" is correct (equals FMV at vest)
- **ESPP:** Must use "Purchase Date Fair Mkt. Value" column

**Prerequisite:** Employer must have taxed the discount as perquisite (normal case for qualified ESPP)

**Implementation:** Lines 1545-1551 in `itr_fa_etrade.py`

---

## Step-by-Step Calculation

### Step 1: Identify Sales
From `G&L_Expanded.xlsx` (E*TRADE Gain & Loss report):
- Extract all SELL transactions
- Get: Symbol, Quantity Sold, Sale Date, Sale Price (USD)

### Step 2: Lot Matching - E*TRADE's Actual Matching (NOT Forced FIFO)

**CRITICAL:** We use **E*TRADE's actual lot matching** from the Gains & Losses report, NOT re-derived FIFO!

> **"FIFO — we use ETRADE's own Gains & Losses export as the source of which lot was sold. That report already reflects whichever lot-relief method ETRADE itself applied when the sale executed. **We don't re-derive or override the lot order on top of it.**"**
>
> — ITRFA.in Official Guidance (2026-08-03)

**Why This Matters:**

From the article [Lot matching vs. FIFO: why it changes your capital gains (July 2026)](https://ethro.com):

> **"Section 45(2A) of the Income-tax Act mandates FIFO — but only for securities held in dematerialised form through an Indian depository (NSDL/CDSL). A foreign brokerage account is not that."**

**Key Points:**
- ✅ **FIFO is NOT mandatory** for foreign brokerage accounts (E*TRADE)
- ✅ **E*TRADE's matching is authoritative** - we report what actually happened
- ✅ **Handles RSU sell-to-cover correctly** - avoids phantom gains from forced FIFO

**Example: RSU Sell-to-Cover (Why Lot Matching Matters)**

**Scenario:**
- Nov 8, 2024: You already own 10 AMD shares (old lot, cost basis $147.95)
- May 9, 2025: 17 RSU vest (new lot, cost basis = $264.33 vest price)
- May 9, 2025: Immediately sell 5 shares to cover taxes

**FIFO (Wrong for sell-to-cover):**
```
Sale matched to Nov 8, 2024 lot (oldest)
Cost basis: $147.95 × 5 = $739.75
Sale proceeds: $264.50 × 5 = $1,322.50
Capital gain: $582.75 (LARGE phantom gain!)
```

**E*TRADE's Actual Matching (Correct):**
```
Sale matched to May 9, 2025 lot (the vested shares)
Cost basis: $264.33 × 5 = $1,321.65
Sale proceeds: $264.50 × 5 = $1,322.50
Capital gain: $0.85 (near-zero, correct!)
```

**Our Implementation:**
```python
# Read E*TRADE's "Date Acquired" column AS-IS from G&L_Expanded.xlsx
acq_date = pd.to_datetime(row['Date Acquired']).strftime('%Y-%m-%d')

# We NEVER re-calculate FIFO - we trust E*TRADE's matching
```

**Legal Position:**
- Foreign accounts: Specific lot identification is **legitimate and defensible**
- E*TRADE's G&L report: **Already reflects their lot-relief method**
- Our approach: **Report what actually happened**, not impose FIFO retroactively

**Example:**
```
Acquisitions (from ByStatus_expanded.xlsx):
- Nov 8, 2024: 10 shares (Lot A)
- May 9, 2025: 17 shares (Lot B)

Sale (from G&L_Expanded.xlsx):
- Date Sold: May 9, 2025
- Quantity: 5 shares
- Date Acquired: May 9, 2025  ← E*TRADE says this sale closed Lot B!

We report: Sold 5 shares from Lot B (May 9, 2025 acquisition)
We DON'T say: Sold 5 shares from Lot A (forced FIFO)
```

### Step 3: Calculate Holding Period
```
Holding Period (months) = (Sale Date - Acquisition Date) / 30 days
```

**Classification:**
- > 24 months → LTCG
- ≤ 24 months → STCG

### Step 4: Determine Rule 115(1)(f) Specified Date
```python
# Calculate last day of month BEFORE sale month
if sale_month == 1:
    specified_date = Dec 31 of previous year
else:
    specified_date = Last day of (sale_month - 1)
```

**Example:**
- Sale Date: Aug 15, {YEAR}
- Sale Month: August (8)
- **Specified Date = Jul 31, {YEAR}** (last day of July)

### Step 5: Calculate Gross Proceeds (INR)
```python
# CRITICAL: Use Rule 115(1)(f) specified date TTBR, NOT sale date TTBR!
Gross Proceeds (INR) = math.ceil(Quantity × Sale Price (USD) × TTBR on Specified Date)
```

**Example:**
- Sold: 10 shares on Aug 15, {YEAR}
- Sale Price: $200 USD
- Specified Date: Jul 31, {YEAR}
- TTBR on Jul 31, {YEAR}: 84.50
- **Gross Proceeds = ceil(10 × 200 × 84.50) = ₹1,69,000**

### Step 6: Calculate Cost Basis (INR)
```python
# CRITICAL: Use SAME Rule 115(1)(f) specified date TTBR (NOT acquisition date TTBR!)
Cost Basis (INR) = math.ceil(Quantity × Acquisition Price (USD) × TTBR on Specified Date)
```

**Example:**
- Acquired: 10 shares on {DATE}
- Acquisition Price: $150 USD
- **Specified Date: Jul 31, {YEAR}** (SAME as proceeds!)
- TTBR on Jul 31, {YEAR}: 84.50 (SAME as proceeds!)
- **Cost Basis = ceil(10 × 150 × 84.50) = ₹1,26,750**

**CRITICAL:** Both proceeds and cost basis use the SAME specified date TTBR!

### Step 7: Calculate Capital Gain
```python
Capital Gain = Gross Proceeds - Cost Basis
```

**Example:**
- Gross Proceeds: ₹1,69,000
- Cost Basis: ₹1,26,750
- **Capital Gain = ₹42,250**

### Step 8: Calculate Tax
```python
# For LTCG (>24 months)
Tax = math.ceil(Capital Gain × 0.125)

# For STCG (≤24 months)
Tax = math.ceil(Capital Gain × 0.312)
```

**Example (LTCG):**
- Capital Gain: ₹46,000
- Tax Rate: 12.5%
- **Tax = ceil(46,000 × 0.125) = ₹5,750**

## Advance Tax Schedule (Income Tax Rule 234C)

### Overview

For capital gains realized during the Financial Year, advance tax must be paid in installments:

| Due Date | Cumulative % | Amount (if total tax = ₹10,000) |
|----------|--------------|--------------------------------|
| **Jul 15** | 15% | ₹1,500 |
| **Sep 15** | 45% | ₹4,500 |
| **Dec 15** | 75% | ₹7,500 |
| **Mar 15** | 100% | ₹10,000 |

**Sources:**
- [ClearTax - Advance Tax FY 2026-27](https://cleartax.in/s/advance-tax)
- [Tax2Win - Advance Tax Payment](https://tax2win.in/guide/advance-tax)
- [TaxGuru - Advance Tax under Income Tax Act](https://taxguru.in/income-tax/advance-tax-income-tax-act-1961.html)
- [TaxBuddy - Advance Tax Rules for Capital Gains](https://www.taxbuddy.com/blog/advance-tax-for-capital-gains-investors)

---

### Special Rule for Capital Gains: No Penalty for Missing Earlier Installments!

**CRITICAL:** Capital gains have a **special exemption** from interest penalties under Section 234C!

> **"If a taxpayer earns capital gains after one or more installment dates have passed, they are not liable to pay interest for the earlier installments. Instead, they must pay the full advance tax on such gains in the next immediate installment following the realization of income."**
>
> — [ClearTax on Advance Tax](https://cleartax.in/s/advance-tax)

**What this means:**
- ✅ Sale in **January** → Pay 100% by **Mar 15** → **No interest penalty** (Jul/Sep/Dec deadlines already passed)
- ✅ Sale in **August** → Pay 100% by **Sep 15** → **No interest penalty** (Jul deadline already passed)
- ✅ Sale in **October** → Pay 100% by **Dec 15** → **No interest penalty** (Jul/Sep deadlines already passed)

**Key Point:** Pay by the **next deadline after the sale date** to avoid interest!

---

### Section 234C - Interest on Late/Short Payment

**Rule:** 1% per month interest on short payment of advance tax installments

**EXCEPTION for Capital Gains:**
> "Interest under section 234C of the Act is not applicable on the shortfall in advance tax instalments provided such shortfall is on account of under-estimate or failure to estimate the amount of capital gains and **the whole of tax payable on such capital gains is paid by the advance tax payment deadline immediately due after the date when such capital gains arise.**"
>
> — [TaxGuru on Advance Tax](https://taxguru.in/income-tax/advance-tax-income-tax-act-1961.html)

**Examples:**

| Sale Date | Next Deadline | Interest if Paid by Deadline | Interest if Paid After |
|-----------|---------------|------------------------------|------------------------|
| Jan 15, 2026 | Mar 15, 2026 | ✅ **No interest** | ❌ 1% per month from Apr 1 |
| Jul 20, 2025 | Sep 15, 2025 | ✅ **No interest** | ❌ 1% per month from Sep 16 |
| Oct 5, 2025 | Dec 15, 2025 | ✅ **No interest** | ❌ 1% per month from Dec 16 |

---

### If No Installment Remains (Sale After Mar 15)

From [India Filings](https://www.indiafilings.com/learn/advance-tax-payment):

> **"When no installment is due, pay by 31st March of the relevant financial year to avoid interest."**

**Example:**
- Sale on **Mar 20, 2026** (after Mar 15 deadline)
- Pay by **Mar 31, 2026** (self-assessment tax, not advance tax)
- ✅ **No interest penalty**

---

### Section 234B - Interest on Non-Payment/Short Payment of Total Tax

**Rule:** If total advance tax paid < 90% of assessed tax → 1% per month interest from Apr 1

**EXCEPTION:** Capital gains special rule applies here too!

From [Tax2Win](https://tax2win.in/guide/advance-tax):

| Advance Tax Paid | Interest Under 234B |
|------------------|---------------------|
| **< 90% of total tax** | 1% per month from Apr 1 |
| **≥ 90% of total tax** | No interest |

**Example:**
- Total tax liability: ₹1,00,000 (all from capital gains)
- Sale on Jan 15, 2026
- Paid ₹1,00,000 by Mar 15, 2026
- **Result:** ✅ No interest under 234B or 234C

---

### Grouped Advance Tax Schedule (New in v2.0)

Our tool now **groups sales by applicable deadlines** instead of showing one aggregated row!

**Benefits:**
1. ✅ Shows which sales go to which Financial Year
2. ✅ Indicates which deadlines have already passed
3. ✅ Clear payment planning by sale period

**Example Output:**

| Sale Period | Financial Year | Total Tax (INR) | By Jul 15 | By Sep 15 | By Dec 15 | By Mar 15 | Note |
|-------------|----------------|-----------------|-----------|-----------|-----------|-----------|------|
| **Jan-Jun 2026** | FY 2026-27 | ₹1,40,654 | ₹21,100 | ₹63,296 | ₹1,05,492 | ₹1,40,654 | All 4 deadlines apply |
| **Jul-Aug 2025** | FY 2025-26 | ₹50,000 | ₹0 | ₹22,500 | ₹37,500 | ₹50,000 | Jul 15 deadline passed |
| **Sep-Nov 2025** | FY 2025-26 | ₹30,000 | ₹0 | ₹0 | ₹22,500 | ₹30,000 | Jul/Sep deadlines passed |
| **Dec 2025-Mar 2026** | FY 2025-26 | ₹20,000 | ₹0 | ₹0 | ₹0 | ₹20,000 | Only Mar 15 deadline applies |
| **TOTAL** | | **₹2,40,654** | **₹21,100** | **₹85,796** | **₹1,65,492** | **₹2,40,654** | Sum across all groups |

**How to Use This:**

**Group 1 (Jan-Jun Sales):** All 4 deadlines apply
```
Jul 15: Pay ₹21,100 (15% of ₹1,40,654)
Sep 15: Pay ₹42,196 more (cumulative 45%)
Dec 15: Pay ₹42,196 more (cumulative 75%)
Mar 15: Pay ₹35,162 more (total 100%)
```

**Group 2 (Jul-Aug Sales):** Only 3 deadlines apply (Jul passed)
```
Sep 15: Pay ₹22,500 (45% of ₹50,000)
Dec 15: Pay ₹15,000 more (cumulative 75%)
Mar 15: Pay ₹12,500 more (total 100%)
```

**Group 3 (Sep-Nov Sales):** Only 2 deadlines apply (Jul/Sep passed)
```
Dec 15: Pay ₹22,500 (75% of ₹30,000)
Mar 15: Pay ₹7,500 more (total 100%)
```

**Group 4 (Dec-Mar Sales):** Only 1 deadline applies (only Mar left)
```
Mar 15: Pay ₹20,000 (100%)
```

---

### Calculation Logic

```python
# Group sales by sale month to determine applicable deadlines
if sale_month <= 6:  # Jan-Jun: All 4 deadlines apply
    jul_payment = tax × 15%
    sep_payment = tax × 45%
    dec_payment = tax × 75%
    mar_payment = tax × 100%

elif sale_month <= 8:  # Jul-Aug: 3 deadlines (Jul passed)
    jul_payment = 0
    sep_payment = tax × 45%
    dec_payment = tax × 75%
    mar_payment = tax × 100%

elif sale_month <= 11:  # Sep-Nov: 2 deadlines (Jul/Sep passed)
    jul_payment = 0
    sep_payment = 0
    dec_payment = tax × 75%
    mar_payment = tax × 100%

else:  # Dec-Mar: Only Mar deadline applies
    jul_payment = 0
    sep_payment = 0
    dec_payment = 0
    mar_payment = tax × 100%
```

**IMPORTANT:** All values rounded UP using `math.ceil()`

## Example: Complete Calculation

### Scenario
**Sale Transaction:**
- Symbol: AMD
- Date: {DATE}
- Quantity: 12 shares
- Sale Price: $200 USD
- TTBR on {DATE}: 84.50

**Matched Acquisitions (FIFO):**
1. **Tranche A:** 10 shares (acquired 30 months earlier)
   - Acquisition Price: $150 USD
   - Holding: 30 months → **LTCG**

2. **Tranche B:** 2 shares (acquired 15 months earlier)
   - Acquisition Price: $160 USD
   - Holding: 15 months → **STCG**

### Calculations

#### Tranche A (LTCG)
```
Gross Proceeds = ceil(10 × 200 × 84.50) = ₹1,69,000
Cost Basis = ceil(10 × 150 × 82.00) = ₹1,23,000
Capital Gain = ₹1,69,000 - ₹1,23,000 = ₹46,000
Tax (12.5%) = ceil(46,000 × 0.125) = ₹5,750
```

#### Tranche B (STCG)
```
Gross Proceeds = ceil(2 × 200 × 84.50) = ₹33,800
Cost Basis = ceil(2 × 160 × 83.20) = ₹26,624
Capital Gain = ₹33,800 - ₹26,624 = ₹7,176
Tax (31.2%) = ceil(7,176 × 0.312) = ₹2,239
```

#### Total Tax
```
Total Tax = ₹5,750 (LTCG) + ₹2,239 (STCG) = ₹7,989
```

#### Advance Tax Schedule
```
Jul 15: ceil(7,989 × 0.15) = ₹1,199
Sep 15: ceil(7,989 × 0.45) = ₹3,595
Dec 15: ceil(7,989 × 0.75) = ₹5,992
Mar 15: ₹7,989
```

## Excel Sheet Output

The **"Capital Gains"** sheet contains:

| Column | Description |
|--------|-------------|
| Nature | Type and quantity (e.g., "RSU (10 shares)", "ESPP (5 shares) - FUTURE") |
| Quantity | Number of shares sold |
| Acquisition Date | When those shares were acquired |
| Sale Date | When shares were sold |
| **Rule 115(1)(f) Specified Date** | Last day of month BEFORE sale month (exchange rate date) |
| **TTBR (INR/USD)** | Exchange rate used (SAME for proceeds and cost basis) |
| Holding Period (months) | Calendar months held |
| Tax Type | LTCG or STCG |
| **Section** | Section 112 (LTCG) or Section 48 (STCG) |
| Cost Basis (INR) | Purchase cost in rupees (using specified date TTBR) |
| Sale Proceeds (INR) | Sale value in rupees (using specified date TTBR) |
| Capital Gain (INR) | Profit |
| Tax Rate | 12.5% or 31.2% |
| Tax Amount (INR) | Tax liability |

Plus a summary section with:
- Total Advance Tax Schedule (Rule 234C)
- By Jul 15 (15%)
- By Sep 15 (45%)
- By Dec 15 (75%)
- By Mar 15 (100%)

## Extended Period: Calendar Year PLUS Next Q1

### Why Extended Period?

**Schedule FA (Table A3):** Calendar year only (Jan 1 - Dec 31, 2025)

**Capital Gains:** **Extended period** (Jan 1, 2025 - Mar 31, 2026)

**Reason:** Sales in Jan-Mar 2026 belong to the **same Indian Financial Year (FY 2025-26)**, so they need:
- Tax calculation for the same FY
- Advance tax planning during FY 2025-26

**Example:**
```
FY 2025-26: Apr 1, 2025 to Mar 31, 2026

Capital Gains includes:
- Jan 2025 - Dec 2025 (calendar year 2025)
- Jan 2026 - Mar 2026 (Q1 of next calendar year)

Why? All these sales fall in FY 2025-26!
```

### Date Filtering Logic

**Sales Included in Capital Gains:**
- From: Jan 1, 2025 (calendar year start)
- To: Mar 31, 2026 (end of FY 2025-26)
- Total: **15 months** of sales

**Sales Excluded:**
- Before Jan 1, 2025 (previous calendar years, already reported)
- After Mar 31, 2026 (next FY, will be reported next year)

**Comparison:**

| Sheet | Period | Duration | Example for FY 2025-26 |
|-------|--------|----------|------------------------|
| **Schedule FA (A3)** | Calendar year | 12 months | Jan 1, 2025 - Dec 31, 2025 |
| **Capital Gains** | Extended | 15 months | Jan 1, 2025 - Mar 31, 2026 |

### Example: Jan 2026 Sale

**Sale Date:** Jan 15, 2026

**Appears in:**
- ❌ **Schedule FA (Table A3):** NO (calendar year 2025 ended Dec 31)
- ✅ **Capital Gains:** YES (FY 2025-26 ends Mar 31, 2026)

**Why?**
- Table A3 reports holdings as of Dec 31, 2025 → Share was still held
- Capital Gains reports sales in FY 2025-26 → Sale happened in same FY

**Advance Tax:**
- Sale in Jan 2026 → Belongs to FY 2025-26
- Pay by Mar 15, 2026 (last deadline of FY 2025-26)
- No interest penalty (special rule for capital gains)

## Important Notes

### 1. Always Round UP
All tax amounts use `math.ceil()` to round up:
```python
# Never underpay
math.ceil(5750.001) = 5751  ✓
round(5750.001) = 5750      ✗ (risky - underpayment)
```

### 2. TTBR Date Matching - Rule 115(1)(f)
**CRITICAL:** Schedule CG uses Income-tax Rule 115(1)(f), NOT exact dates!
- **Both proceeds and cost basis:** Use TTBR on **last day of month BEFORE sale month**
- **Same rate for both:** ONE specified date per sale, not separate dates
- **Different from Schedule FA:** Schedule FA uses exact acquisition/sale dates
- If TTBR missing for specified date, the script will fail (needs manual intervention)

### 3. FIFO is Mandatory
- Cannot choose which shares to sell (tax rule)
- Oldest shares must be sold first

### 4. Multiple Sales
If you sold multiple times:
- Each sale is processed separately
- FIFO queue is maintained across all sales
- Running total of unsold shares tracked

### 5. Exchange Rate Impact
Capital gains can vary significantly based on:
- TTBR on acquisition date
- TTBR on sale date

**Example:**
- Bought at TTBR 82, Sold at TTBR 86 → Higher INR gain
- Bought at TTBR 86, Sold at TTBR 82 → Lower INR gain (or even loss!)

## Verification Steps

1. Open **"Capital Gains"** sheet in Excel
2. Verify FIFO matching (oldest shares sold first)
3. Check holding period calculation (months)
4. Confirm LTCG vs STCG classification
5. Verify tax rate applied (12.5% or 31.2%)
6. Check all values rounded UP
7. Verify advance tax schedule adds up to total tax

## Common Questions

**Q: What if I have losses?**
A: Losses are calculated the same way (negative capital gain). Can be set off against other capital gains.

**Q: What if holding period is exactly 24 months?**
A: 24 months = STCG (must be **more than** 24 for LTCG)

**Q: What if I sold in {YEAR-1} but generating for FY {YEAR}-{YEAR+1}?**
A: Those sales are excluded (already reported in previous ITR)

**Q: Can I choose which shares to sell?**
A: No, FIFO is mandatory per Indian tax law

**Q: What if TTBR is missing for sale date?**
A: Script will error out - you need to manually add that date's TTBR to the CSV
