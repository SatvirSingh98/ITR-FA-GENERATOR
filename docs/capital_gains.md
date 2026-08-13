# Capital Gains Calculation

## Overview
The **Capital Gains** sheet calculates tax liability on stock sales, categorized as Long-Term Capital Gains (LTCG) or Short-Term Capital Gains (STCG) based on holding period.

**Sources:** [ITRFA.in Schedule CG Blog](https://itrfa.in/blog/schedule-cg-rsu-espp) | [ITRFA.in SBI TTBR Rule 115](https://itrfa.in/blog/sbi-ttbr-rule-115)

---

## Capital Gains Excel Sheet

### Sheet Structure

The Capital Gains sheet displays sale details and advance tax schedule in a **compact vertical format**.

#### Single Regime (Same Tax Rate for NEW and OLD)
```
Row 1:  [TEAL HEADERS] Nature | Quantity | Acquisition Date | Sale Date | Tax Rate | Tax Amount (INR) | ...
Rows 2-N: Sale details (alternating white/light blue rows)
(Blank separator rows)
Row N+4: [TEAL HEADER - MERGED A:B] Advance Tax Schedule
Row N+5: Sale Period          | Apr 1 - Jul 15, 2026
Row N+6: Tax Type             | Advance Tax
Row N+7: Total Tax (INR)      | Rs.XX,XXX
Row N+8: By Jul 15            | Rs.XX,XXX
Row N+9: By Sep 15            | Rs.XX,XXX
Row N+10: By Dec 15           | Rs.XX,XXX
Row N+11: By Mar 15           | Rs.XX,XXX
Row N+12: Note                | All 4 deadlines apply
```

#### Dual Regime (Different Tax Rates for NEW and OLD)
```
Row 1:  [TEAL HEADERS] Nature | Quantity | ... | Tax Rate (New) | Tax Amount (New) INR | Tax Rate (Old) | Tax Amount (Old) INR
Rows 2-N: Sale details (alternating white/light blue rows)
(Blank separator rows)
Row N+4: [BLUE MERGED A:B] NEW TAX REGIME | [RED MERGED E:F] OLD TAX REGIME
Columns A-B (NEW):              Columns E-F (OLD):
Row N+5: Sale Period            | Sale Period
Row N+6: Tax Type               | Tax Type
Row N+7: Total Tax (INR)        | Total Tax (INR)
Row N+8: By Jul 15              | By Jul 15
Row N+9: By Sep 15              | By Sep 15
Row N+10: By Dec 15             | By Dec 15
Row N+11: By Mar 15             | By Mar 15
Row N+12: Note                  | Note
```

### Professional Color Scheme

**Headers:**
- **Teal (#00695C):** Sale details headers and single regime advance tax header
- **Dark Blue (#01579B):** NEW TAX REGIME label (dual regime)
- **Dark Red (#BF360C):** OLD TAX REGIME label (dual regime)

**Data Rows:**
- **Sale Details:** Alternating white (#FFFFFF) and light blue (#E3F2FD)
- **Advance Tax:** White background (#FFFFFF) with black text (#000000)
- **Separators:** Clean white space with NO borders

**Layout Features:**
- Regime headers: Merged cells (A:B for single/NEW, E:F for OLD), centered, NO borders
- Advance tax: Vertical format (Field | Value) for easy reading
- Side-by-side comparison: NEW regime in columns A-B, OLD regime in columns E-F
- Columns C-D: Empty separator (no borders, no data)

### Example Tax Comparison

**Income Bracket: ₹16-20 lakhs (illustrative example)**

| Sale | Quantity | Capital Gain | New Regime Tax (20.8%) | Old Regime Tax (31.2%) | Savings |
|------|----------|--------------|------------------------|------------------------|---------|
| Stock | 30 shares | ₹2,50,000 | ₹52,000 | ₹78,000 | ₹26,000 |
| Stock | 10 shares | ₹80,000 | ₹16,640 | ₹24,960 | ₹8,320 |
| ESPP | 5 shares | ₹40,000 | ₹8,320 | ₹12,480 | ₹4,160 |
| ESPP | 8 shares | ₹1,20,000 | ₹24,960 | ₹37,440 | ₹12,480 |
| **TOTAL** | - | **₹4,90,000** | **₹1,01,920** | **₹1,52,880** | **₹50,960** |

**Tax Savings with New Regime:** ₹50,960 (33% less tax)

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
- **Tax Rate:** User's income tax slab rate (including surcharge and cess)
- **Dual-Regime Calculation:** Tool automatically calculates tax under BOTH New and Old regimes for comparison

##### Tax Rate Calculation - Dual Regime Approach

**User Input:** Select expected TOTAL TAXABLE INCOME bracket (1-11 options)
- **Tip:** Check Form-16 for "Total Taxable Income" (includes salary + other income sources)

**Output:** Capital Gains sheet displays TWO separate tables side-by-side:
1. **NEW TAX REGIME** - Sale details + Advance tax schedule
2. **OLD TAX REGIME** - Sale details + Advance tax schedule

This allows users to compare and decide which regime minimizes their tax liability.

##### New Tax Regime Rates (FY 2025-26)

**Base Slab Rates:**
- Up to ₹4L: 0%
- ₹4L-8L: 5%
- ₹8L-12L: 10%
- ₹12L-16L: 15%
- ₹16L-20L: 20%
- ₹20L-24L: 25%
- Above ₹24L: 30%

**Surcharge (on income tax):**
- Up to ₹50L: Nil
- ₹50L-1Cr: 10%
- ₹1Cr-2Cr: 15%
- ₹2Cr-5Cr: 25%
- Above ₹5Cr: **25%** (max surcharge in New Regime)

**Cess:** 4% on (base tax + surcharge)

**Effective STCG Rates (New Regime):**
| Income Bracket | Base + Surcharge + Cess | Effective Rate |
|----------------|-------------------------|----------------|
| Up to ₹4L | 0% + 0% + 0% | 0.0% |
| ₹4L-8L | 5% + 0% + 4% cess | 5.2% |
| ₹8L-12L | 10% + 0% + 4% cess | 10.4% |
| ₹12L-16L | 15% + 0% + 4% cess | 15.6% |
| ₹16L-20L | 20% + 0% + 4% cess | 20.8% |
| ₹20L-24L | 25% + 0% + 4% cess | 26.0% |
| ₹24L-50L | 30% + 0% + 4% cess | 31.2% |
| ₹50L-1Cr | 30% + 10% + 4% cess | 34.32% |
| ₹1Cr-2Cr | 30% + 15% + 4% cess | 35.88% |
| ₹2Cr-5Cr | 30% + 25% + 4% cess | 39.0% |
| Above ₹5Cr | 30% + 25% + 4% cess | 39.0% |

##### Old Tax Regime Rates

**Base Slab Rates (Different from New):**
- Up to ₹2.5L: 0%
- ₹2.5L-5L: 5%
- ₹5L-10L: 20%
- Above ₹10L: 30%

**Surcharge (on income tax):**
- Up to ₹50L: Nil
- ₹50L-1Cr: 10%
- ₹1Cr-2Cr: 15%
- ₹2Cr-5Cr: 25%
- Above ₹5Cr: **37%** (higher than New Regime!)

**Cess:** 4% on (base tax + surcharge)

**Effective STCG Rates (Old Regime):**
| Income Bracket | Base + Surcharge + Cess | Effective Rate |
|----------------|-------------------------|----------------|
| Up to ₹4L | 0% (nil) | 0.0% |
| ₹4L-8L | 5% + 0% + 4% cess | 5.2% |
| ₹8L-12L | 20% + 0% + 4% cess | 20.8% (higher) |
| ₹12L-16L | 30% + 0% + 4% cess | 31.2% (higher) |
| ₹16L-20L | 30% + 0% + 4% cess | 31.2% (higher) |
| ₹20L-24L | 30% + 0% + 4% cess | 31.2% (higher) |
| ₹24L-50L | 30% + 0% + 4% cess | 31.2% (same) |
| ₹50L-1Cr | 30% + 10% + 4% cess | 34.32% (same) |
| ₹1Cr-2Cr | 30% + 15% + 4% cess | 35.88% (same) |
| ₹2Cr-5Cr | 30% + 25% + 4% cess | 39.0% (same) |
| Above ₹5Cr | 30% + 37% + 4% cess | **42.744%** (higher) |

**Key Differences:**
- Old Regime has 20% slab at ₹5L-10L → Higher tax for ₹8L-24L income
- Old Regime has 37% surcharge above ₹5Cr → Higher tax for ultra-high earners
- New Regime generally more favorable for ₹8L-5Cr income range

**Example Comparison (Income: ₹16L-20L):**
- New Regime: 20.8% → Save ₹10.4% on every rupee of STCG
- Old Regime: 31.2%

- **NOT applicable:** Section 111A (that's for STT-paid Indian listed equity)

**Calculation:** Always rounded UP using `math.ceil()`

- Rate calculation: `calculate_stcg_rates_for_income()` function (lines 49-98)
- Dual-regime tax computation: `calculate_tax_for_regime()` function (lines 2445-2491)

---

## ESPP Cost Basis - Section 49(2AA)

### The Rule
**"If employer taxed the discount as perquisite → Cost basis = FMV on purchase date (NOT discounted purchase price)"**

**Per ITRFA.in:** "Section 49(2AA) says that if the employer has taxed the discount under section 17(2), the cost of acquisition for capital gains is the fair market value on the purchase date"

### Example
```
Purchase Date: May 9, 2025
FMV on purchase date: $152.39 per share
Discounted price (15% off): $129.53 per share

E*TRADE shows:
  - Adjusted Cost Basis: $129.53 (WRONG for Indian tax)
  - Purchase Date Fair Mkt. Value: $152.39 (CORRECT for Indian tax)

Use: $152.39 per share
```

**Why:**
1. You already paid income tax on the $22.86 discount ($152.39 - $129.53)
2. Using $129.53 would tax you again on the same amount
3. Section 49(2AA) prevents double taxation

**RSU vs ESPP:**
- **RSU:** "Adjusted Cost Basis Per Share" is correct (equals FMV at vest)
- **ESPP:** Must use "Purchase Date Fair Mkt. Value" column

**Prerequisite:** Employer must have taxed the discount as perquisite (normal case for qualified ESPP)


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

**E*TRADE's Actual Lot Matching (Correct):**
```
E*TRADE matched to May 9, 2025 lot (same-day)
Cost basis: $264.33 × 5 = $1,321.65
Sale proceeds: $264.50 × 5 = $1,322.50
Capital gain: $0.85 (minimal gain - reflects reality)
```

**Impact:** FIFO would create a ₹58,000 phantom gain on a ₹100 actual gain!

**What We Do:**
- Read `OpenDate`, `Quantity`, `OpenPrice USD` from G&L report
- Use E*TRADE's lot assignment as-is
- No FIFO enforcement or re-derivation


### Step 3: Get Rule 115(1)(f) Exchange Rate

**For each sale:**
1. Get sale date (e.g., Aug 15, 2025)
2. Calculate specified date = **last day of month BEFORE sale month** (Jul 31, 2025)
3. Look up SBI TTBR for that date
4. Use SAME rate for both sale proceeds AND cost basis

**Example:**
```
Sale Date: Aug 15, 2025
Specified Date: Jul 31, 2025 (last day of previous month)
TTBR: 84.50 INR/USD (from SBI data)

Sale Proceeds: $1,500.00 × 84.50 = ₹1,26,750
Cost Basis: $1,485.00 × 84.50 = ₹1,25,483
```


### Step 4: Calculate Capital Gain

```python
capital_gain_inr = sale_proceeds_inr - cost_basis_inr
```

**Example:**
```
Sale Proceeds: ₹1,26,750
Cost Basis: ₹1,25,483
Capital Gain: ₹1,267
```

### Step 5: Classify as LTCG or STCG

Calculate holding period in calendar months:
```python
holding_months = (sale_year - acq_year) * 12 + (sale_month - acq_month)
```

**Classification:**
- `holding_months > 24` → LTCG (Section 112, 12.5% tax)
- `holding_months ≤ 24` → STCG (Section 48, slab rate)

**Example:**
```
Acquisition: May 9, 2025
Sale: May 9, 2025 (same day)
Holding: 0 months → STCG
```

### Step 6: Calculate Tax (Dual Regime)

**For STCG sales:**

1. **Determine tax rates based on income bracket** (from user selection)
2. **Calculate tax for BOTH regimes:**

**New Regime:**
```python
tax_new = math.ceil(capital_gain * stcg_rate_new)
```

**Old Regime:**
```python
tax_old = math.ceil(capital_gain * stcg_rate_old)
```

3. **Create TWO separate sale detail tables** - one per regime
4. **Calculate TWO separate advance tax schedules** - one per regime

**For LTCG sales:**
```python
tax = math.ceil(capital_gain * 0.125)  # 12.5% for both regimes
```

**Example (STCG, Income ₹16L-20L):**
```
Capital Gain: ₹1,267

New Regime Tax: ceil(₹1,267 × 20.8%) = ceil(₹263.536) = ₹264
Old Regime Tax: ceil(₹1,267 × 31.2%) = ceil(₹395.304) = ₹396

Savings with New Regime: ₹132
```


---

## Advance Tax Schedule and Penalty Rules

### Overview
This section covers advance tax payment deadlines (Rule 234C) and related penalty provisions to help you avoid interest charges and fees.

### Advance Tax Schedule (Rule 234C) - Vertical Format

**Purpose:** Show when to pay advance tax for capital gains based on sale date.

The Excel sheet displays advance tax in **vertical format** for easy reading:

**Example Output (Vertical Layout):**
```
Field                | Value
---------------------|----------------------
Sale Period          | Apr 1 - Jul 15, 2026
Tax Type             | Advance Tax
Total Tax (INR)      | Rs.1,40,654
By Jul 15            | Rs.21,100
By Sep 15            | Rs.63,296
By Dec 15            | Rs.1,05,492
By Mar 15            | Rs.1,40,654
Note                 | All 4 deadlines apply
```

**Dual Regime Comparison:**
When tax rates differ between NEW and OLD regimes, both schedules appear **side-by-side**:
- Columns A-B: NEW TAX REGIME schedule
- Columns E-F: OLD TAX REGIME schedule
- Columns C-D: Empty separator for readability

### Payment Deadlines (within the Financial Year)

| Deadline | Cumulative % | Incremental % |
|----------|--------------|---------------|
| Jul 15 | 15% | 15% |
| Sep 15 | 45% | 30% |
| Dec 15 | 75% | 30% |
| Mar 15 | 100% | 25% |

### Rules Based on Sale Date

**Group 1: Sales Apr 1 - Jul 15**
- All 4 deadlines apply
- Example: Sale on Jun 10 → Pay 15% by Jul 15, 45% by Sep 15, 75% by Dec 15, 100% by Mar 15

**Group 2: Sales Jul 16 - Sep 15**
- Jul 15 deadline passed → Pay 0% by Jul 15
- Remaining 3 deadlines apply
- Example: Sale on Aug 20 → Pay 0% by Jul 15, 45% by Sep 15, 75% by Dec 15, 100% by Mar 15

**Group 3: Sales Sep 16 - Dec 15**
- Jul 15 and Sep 15 deadlines passed
- Remaining 2 deadlines apply
- Example: Sale on Oct 30 → Pay 0% by Jul 15, 0% by Sep 15, 75% by Dec 15, 100% by Mar 15

**Group 4: Sales Dec 16 - Mar 15**
- Only Mar 15 deadline applies
- Example: Sale on Jan 20 → Pay 0% by Jul 15, 0% by Sep 15, 0% by Dec 15, 100% by Mar 15

**Group 5: Sales Mar 16 - Mar 31**
- All deadlines passed
- Pay as self-assessment tax by Mar 31 (ITR filing deadline)
- Example: Sale on Mar 25 → Pay 0% advance tax, 100% by Mar 31 (self-assessment)

### Future Sales (After Current FY)

The tool also includes **future sales** (sales after Mar 31 of current FY) to help plan advance tax for next year.

**Example:**
```
Current FY: 2025-26 (Apr 1, 2025 - Mar 31, 2026)
Sale Date: Jun 15, 2026 (next FY 2026-27)

Marked as: "FUTURE" in Nature column
Tax payable in: FY 2026-27
Advance tax by: Jul 15, 2026 (15%), Sep 15, 2026 (45%), etc.
```

**Why helpful:**
- Plan liquidity for tax payments
- Know when to pay if shares sell in next FY
- Estimate tax impact before exercising options

### Dual-Regime Advance Tax Schedules

Both New and Old regime calculations include separate advance tax schedules:

**New Regime Advance Tax:**
- Calculated from New Regime tax amounts
- Shows payment schedule based on sale period
- Includes FY designation (e.g., "FY 2026-27" for future sales)

**Old Regime Advance Tax:**
- Calculated from Old Regime tax amounts (higher for ₹8L-5Cr income)
- Same payment schedule structure
- Allows comparison of payment obligations

**Example (Sale Apr 1 - Jul 15, 2026):**

| Regime | Total Tax | By Jul 15 (15%) | By Sep 15 (45%) | By Dec 15 (75%) | By Mar 15 (100%) |
|--------|-----------|-----------------|-----------------|-----------------|------------------|
| **New** | ₹1,00,000 | ₹15,000 | ₹45,000 | ₹75,000 | ₹1,00,000 |
| **Old** | ₹1,50,000 | ₹22,500 | ₹67,500 | ₹1,12,500 | ₹1,50,000 |

### Interest and Penalty Provisions

**IMPORTANT:** Missing advance tax deadlines or filing ITR late results in **automatic interest/penalties**. The Income Tax Department calculates these automatically.

#### Section 234C - Interest on Deferment of Advance Tax

**What:** 1% per month (or part thereof) simple interest on advance tax shortfall at each installment.

**When Applied:**
- Interest charged if advance tax paid by a deadline is less than required cumulative %
- Calculated separately for each missed/short installment
- Applied even if total tax is paid by Mar 31

**Calculation Example:**
```
Total tax liability: ₹1,20,000
Required by Sep 15: ₹54,000 (45%)
Actually paid by Sep 15: ₹35,000
Shortfall: ₹19,000

Interest (Sep 15 to Mar 31 = 6 months): ₹19,000 × 1% × 6 = ₹1,140
```

**How to Avoid:**
- Pay advance tax by each deadline (Jul 15, Sep 15, Dec 15, Mar 15)
- Ensure cumulative % paid matches or exceeds required %
- Plan liquidity for tax payments in advance

**Note:** This is what the **Advance Tax Schedule** in the Capital Gains sheet helps you avoid!

#### Section 234B - Interest on Shortfall in Total Advance Tax

**What:** 1% per month (or part thereof) simple interest if total advance tax paid by Mar 31 is less than 90% of assessed tax.

**When Applied:**
- Calculated from Apr 1 of assessment year to date of assessment/self-assessment
- Applied on the shortfall amount (assessed tax minus advance tax paid)
- Common scenario: Underestimated capital gains or other income

**Calculation Example:**
```
Total assessed tax: ₹1,50,000
Required minimum (90%): ₹1,35,000
Total advance tax paid by Mar 31: ₹1,00,000
Shortfall: ₹35,000

Interest (Apr 1 to Jul 31 = 4 months): ₹35,000 × 1% × 4 = ₹1,400
```

**How to Avoid:**
- Ensure total advance tax ≥ 90% of estimated tax liability
- Account for ALL income sources (salary + capital gains + other)
- Use the Capital Gains sheet to accurately estimate tax
- Pay self-assessment tax before filing ITR if advance tax was short

**Difference from 234C:**
- 234C: Interest on deferring individual installments
- 234B: Interest on overall shortfall in advance tax

#### Section 234A - Interest on Delay in Filing ITR

**What:** 1% per month (or part thereof) simple interest on unpaid tax from ITR due date to actual filing date.

**When Applied:**
- ITR filed after due date (usually July 31 for individuals)
- Interest calculated on tax due (after adjusting TDS/advance tax)
- Continues until ITR is filed AND tax is paid

**Calculation Example:**
```
Tax due after TDS/advance tax: ₹60,000
ITR due date: Jul 31, 2026
Actual filing date: Oct 15, 2026
Delay: 2.5 months

Interest: ₹60,000 × 1% × 3 = ₹1,800 (3 months, rounded up)
```

**How to Avoid:**
- File ITR before July 31 (for individuals without audit)
- Pay all self-assessment tax before filing
- Use pre-filled ITR data to speed up filing
- Keep all documents ready (Form 16, Capital Gains statement, etc.)

**Due Dates:**
- Individuals (no audit): **July 31**
- Partnership firms/Companies (with audit): **October 31**
- Revised ITR: **December 31**

#### Section 234F - Fee for Delay in Filing ITR

**What:** Late filing fee (NOT interest, it's a flat penalty).

**Fee Structure:**
| Total Income | Filing Delay | Fee |
|--------------|--------------|-----|
| Up to ₹5 lakhs | After Jul 31 | ₹1,000 |
| Above ₹5 lakhs | After Jul 31 | ₹5,000 |
| Any amount | After Dec 31 | ₹10,000* |

*₹10,000 is the maximum fee (₹5,000 for delay beyond Jul 31 + ₹5,000 for delay beyond Dec 31)

**When Applied:**
- Automatically added when filing delayed ITR
- Separate from Section 234A interest
- Both 234A interest AND 234F fee apply together

**Calculation Example:**
```
Income: ₹20,00,000 (above ₹5 lakhs)
ITR due: Jul 31, 2026
Filed on: Sep 20, 2026

Fee: ₹5,000 (under 234F)
Plus: Interest under 234A on any unpaid tax
```

**How to Avoid:**
- File ITR by July 31, even if you need to revise later
- If you filed on time, you can revise by December 31 with NO penalty
- Delayed filing cannot claim refunds easily

### Summary: How to Avoid All Penalties

| Section | What | How to Avoid |
|---------|------|--------------|
| **234C** | Interest on deferred advance tax installments | Pay advance tax by each deadline (use Capital Gains sheet schedule) |
| **234B** | Interest if total advance tax < 90% | Ensure total advance tax paid ≥ 90% of estimated tax |
| **234A** | Interest on delayed ITR filing | File ITR by July 31 |
| **234F** | Penalty fee for delayed ITR filing | File ITR by July 31 |

**Best Practice:**
1. Use the **Capital Gains sheet Advance Tax Schedule** to plan payments
2. Pay advance tax on time (by each deadline shown in the sheet)
3. Ensure total advance tax ≥ 90% of estimated tax liability
4. File ITR by **July 31** to avoid both 234A interest and 234F penalty
5. Keep buffer for self-assessment tax when filing

**Pro Tip:** Even if you miss advance tax deadlines, **file ITR on time** (by July 31) to at least avoid 234F penalty and limit 234A interest.


---

## Excel Sheet Output - Detailed Structure

### Table 1: NEW TAX REGIME - Sale Details

**Columns:**
- Nature (e.g., "Stock (26 shares)", "ESPP (5 shares) - FUTURE")
- Quantity
- Acquisition Date
- Sale Date
- Rule 115(1)(f) Specified Date (last day of month before sale)
- TTBR (INR/USD) (Rule 115(1)(f) rate)
- Holding Period (months)
- Tax Type (STCG/LTCG)
- Section (48/112)
- Cost Basis (INR)
- Sale Proceeds (INR)
- Capital Gain (INR)
- Tax Rate (percentage)
- Tax Amount (INR)

**Formatting:**
- Header: Teal background (#00695C), white bold text
- Data rows: Alternating white and light blue (#E3F2FD)
- All columns: Borders, center-aligned
- Currency columns: ₹ symbol, no decimals (ITR requirement)

### Table 2: NEW TAX REGIME - Advance Tax Schedule

**Columns:**
- Sale Period (e.g., "Apr 1 - Jul 15, 2026")
- Financial Year (e.g., "FY 2026-27")
- Tax Type ("Advance Tax" or "Self-Assessment Tax")
- Total Tax (INR)
- By Jul 15
- By Sep 15
- By Dec 15
- By Mar 15
- Note (e.g., "All 4 deadlines apply")

**Formatting:**
- Header: Dark gray background (#455A64), white bold text
- Empty columns (J-N): No color, no borders
- Data rows: White background, borders only in columns A-I
- TOTAL row: Shows sum across all sale periods

### Table 3: OLD TAX REGIME - Sale Details

Same structure as Table 1, but with Old Regime tax rates and amounts.

**Key Differences:**
- Tax Rate column shows higher rates (e.g., 31.2% instead of 20.8%)
- Tax Amount column shows higher amounts
- Same sale data, different tax calculation

### Table 4: OLD TAX REGIME - Advance Tax Schedule

Same structure as Table 2, but with Old Regime tax amounts.

**Key Differences:**
- Total Tax (INR) is higher
- All deadline amounts proportionally higher
- TOTAL row shows higher cumulative tax

### Separator Rows

Between the two regime sections:
- 5-6 blank rows
- No borders, no colors
- Clean visual separation

### Visual Hierarchy

**Level 1 - Regime Headers (Rows 1, 18):**
- Color: Blue (#0277BD)
- Font: Bold, 12pt, white
- Borders: None (clean banner)
- Alignment: Center

**Level 2 - Sale Details Headers (Rows 2, 19):**
- Color: Teal (#00695C)
- Font: Bold, 11pt, white
- Borders: All sides
- Alignment: Center

**Level 3 - Advance Tax Headers (Rows 10, 27):**
- Color: Dark Gray (#455A64)
- Font: Bold, 11pt, white
- Borders: Only columns A-I (where headers exist)
- Alignment: Center

**Data Rows:**
- Sale details: Alternating colors for readability
- Advance tax: White background, selective borders
- All data: Center-aligned

---

## Date Ranges

### Schedule FA (Table A3)
**Period:** Calendar year ONLY (Jan 1 - Dec 31)
- **Purpose:** Asset disclosure
- **Includes:** Holdings as of Dec 31 (end of calendar year)
- **Excludes:** Sales/acquisitions after Dec 31

### Capital Gains
**Period:** Extended (Jan 1 - Mar 31 next year) + Future
- **Current FY Sales:** Jan 1 - Mar 31 next year
- **Future Sales:** Apr 1 onwards (marked as "FUTURE")

**Why different?**
- Schedule FA uses calendar year (CBDT filing instructions)
- Capital Gains uses Indian Financial Year (Apr-Mar)
- Jan-Mar sales of next year:
  - Capital Gains: THIS year's ITR
  - Schedule FA Table A3: NEXT year's ITR (asset was held on Dec 31)

**Example:**
```
Sale: Feb 15, 2026

Capital Gains sheet:
  - Appears in FY 2025-26 output
  - Tax payable with Apr 2026 ITR filing
  - Advance tax by Mar 15, 2026

Schedule FA Table A3:
  - Does NOT appear in FY 2025-26 (asset was sold)
  - Would have appeared in FY 2024-25 if held on Dec 31, 2024
```

---

## Verification Checklist

1. Check Rule 115(1)(f) dates are correct (last day of month BEFORE sale)
2. Verify lot matching matches E*TRADE G&L report (no forced FIFO)
3. Confirm ESPP uses "Purchase Date Fair Mkt. Value" (not Adjusted Cost Basis)
4. Check holding period classification (LTCG vs STCG)
5. Verify tax rates applied correctly for BOTH regimes
6. Check all values rounded UP
7. Verify advance tax schedule adds up to total tax for BOTH regimes
8. Compare New vs Old regime tax amounts
9. Verify future sales are marked "- FUTURE" in Nature column
10. Check Excel formatting (colors, borders, alignment)

## Common Questions

**Q: What if I have losses?**
A: Losses are calculated the same way (negative capital gain). Can be set off against other capital gains. Both regime tables will show the loss.

**Q: What if holding period is exactly 24 months?**
A: 24 months = STCG (must be **more than** 24 for LTCG)

**Q: What if I sold in {YEAR-1} but generating for FY {YEAR}-{YEAR+1}?**
A: Those sales are excluded (already reported in previous ITR)

**Q: Can I choose which shares to sell?**
A: For foreign brokerage accounts like E*TRADE, **YES** - you can use specific lot selection. FIFO is only mandatory for Indian demat accounts (Section 45(2A)). We report whatever lot E*TRADE actually sold per the Gains & Losses report.

**Q: What if TTBR is missing for sale date?**
A: Script will error out - you need to manually add that date's TTBR to the CSV

**Q: Which regime should I choose?**
A: The tool shows BOTH regime calculations side-by-side. Compare total tax amounts and choose the regime with lower tax. Generally:
- New Regime is better for ₹8L-50L income
- Old Regime MAY be better if you have large deductions (80C, 80D, etc.)
- Consult your CA for final decision

**Q: Do I have to pay tax under both regimes?**
A: NO! You choose ONE regime when filing ITR. The tool shows both to help you decide. Once you pick a regime for the year, you pay tax according to that regime's rates.

**Q: Can I change regimes mid-year?**
A: NO. You choose one regime for the entire Financial Year when filing ITR. The regime choice applies to ALL your income for that year.

**Q: How accurate is the advance tax schedule?**
A: The schedule is calculated per Rule 234C and is accurate for tax planning. However, consult your CA before making actual payments, as your total tax liability may include other income sources.

**Q: What if my income changes after I selected the bracket?**
A: Re-run the tool with the correct income bracket. The Capital Gains sheet will regenerate with updated tax rates for both regimes.
