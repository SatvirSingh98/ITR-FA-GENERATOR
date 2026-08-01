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
- Sale on Aug 15, 2025 → Use **Jul 31, 2025** TTBR for BOTH proceeds and cost basis
- Sale on Nov 1, 2025 → Use **Oct 31, 2025** TTBR for BOTH proceeds and cost basis
- Sale on Jan 1, 2026 → Use **Dec 31, 2025** TTBR for BOTH proceeds and cost basis

**Why it matters:**
- Form 16 uses Rule 115(1)(a): Last day of month BEFORE vest month
- Schedule FA uses exact date (per CBDT filing instructions)
- Schedule CG uses last day of month BEFORE sale month (per Rule 115(1)(f))
- **All three are different dates with different rates!**

**Common mistake:** Using exact sale/acquisition dates (WRONG!)

**Implementation:** Lines 1552-1602 in `itr_fa_engine.py`

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
Acquired: Jan 10, 2024
Sold: Jan 10, 2026  (exactly 24 months)
Classification: STCG (not "more than" 24 months)
```

### Tax Rates & Sections

#### Long-Term Capital Gains (LTCG)
- **Holding Period:** > 24 months
- **Section:** 112
- **Tax Rate:** 12.5%
- **Indexation:** NONE (per Finance Act 2024 for transfers on/after July 23, 2024)
- **NOT applicable:** Section 112A (that's for STT-paid Indian listed equity)

#### Short-Term Capital Gains (STCG)
- **Holding Period:** ≤ 24 months
- **Section:** 48
- **Tax Rate:** 31.2% (slab rate: 30% + 4% cess)
- **NOT applicable:** Section 111A (that's for STT-paid Indian listed equity)

**Calculation:** Always rounded UP using `math.ceil()`

**Implementation:** Lines 1525-1541 in `itr_fa_engine.py`

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

**Implementation:** Lines 1545-1551 in `itr_fa_engine.py`

---

## Step-by-Step Calculation

### Step 1: Identify Sales
From `G&L_Expanded.xlsx` (E*TRADE Gain & Loss report):
- Extract all SELL transactions
- Get: Symbol, Quantity Sold, Sale Date, Sale Price (USD)

### Step 2: Match with Acquisitions (FIFO)
For each sale, match against acquisitions using **FIFO (First-In, First-Out)**:
- Oldest unsold shares are sold first
- Track remaining quantity per tranche

**Example:**
```
Acquisitions:
- 2023-06-10: 10 shares (Tranche A)
- 2024-09-15: 8 shares (Tranche B)
- 2025-02-20: 6 shares (Tranche C)

Sale: 2025-12-15: 12 shares
FIFO Matching:
- 10 shares from Tranche A (2023-06-10)
- 2 shares from Tranche B (2024-09-15)
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
- Sale Date: Aug 15, 2025
- Sale Month: August (8)
- **Specified Date = Jul 31, 2025** (last day of July)

### Step 5: Calculate Gross Proceeds (INR)
```python
# CRITICAL: Use Rule 115(1)(f) specified date TTBR, NOT sale date TTBR!
Gross Proceeds (INR) = math.ceil(Quantity × Sale Price (USD) × TTBR on Specified Date)
```

**Example:**
- Sold: 10 shares on Aug 15, 2025
- Sale Price: $200 USD
- Specified Date: Jul 31, 2025
- TTBR on Jul 31, 2025: 84.50
- **Gross Proceeds = ceil(10 × 200 × 84.50) = ₹1,69,000**

### Step 6: Calculate Cost Basis (INR)
```python
# CRITICAL: Use SAME Rule 115(1)(f) specified date TTBR (NOT acquisition date TTBR!)
Cost Basis (INR) = math.ceil(Quantity × Acquisition Price (USD) × TTBR on Specified Date)
```

**Example:**
- Acquired: 10 shares on 2023-06-10
- Acquisition Price: $150 USD
- **Specified Date: Jul 31, 2025** (SAME as proceeds!)
- TTBR on Jul 31, 2025: 84.50 (SAME as proceeds!)
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

For sales in the **current or future FY**, advance tax must be paid in installments:

| Due Date | Cumulative % | Amount (if total tax = ₹10,000) |
|----------|--------------|--------------------------------|
| **Jul 15** | 15% | ₹1,500 |
| **Sep 15** | 45% | ₹4,500 |
| **Dec 15** | 75% | ₹7,500 |
| **Mar 15** | 100% | ₹10,000 |

### Calculation
```python
total_tax = sum(all LTCG + STCG tax)

advance_jul = math.ceil(total_tax × 0.15)
advance_sep = math.ceil(total_tax × 0.45)
advance_dec = math.ceil(total_tax × 0.75)
advance_mar = total_tax  # 100%
```

## Example: Complete Calculation

### Scenario
**Sale Transaction:**
- Symbol: AMD
- Date: 2025-12-01
- Quantity: 12 shares
- Sale Price: $200 USD
- TTBR on 2025-12-01: 84.50

**Matched Acquisitions (FIFO):**
1. **Tranche A:** 10 shares from 2023-06-10
   - Acquisition Price: $150 USD
   - TTBR on 2023-06-10: 82.00
   - Holding: 30 months → **LTCG**

2. **Tranche B:** 2 shares from 2024-09-15
   - Acquisition Price: $160 USD
   - TTBR on 2024-09-15: 83.20
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

## Date Filtering

**Sales Included:**
- Only sales from **current FY onwards** are included
- Example: Generating for FY 2025-26, only sales from Apr 1, 2025 onwards

**Sales Excluded:**
- Sales from previous years (already reported in past ITRs)

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

**Q: What if I sold in 2024 but generating for FY 2025-26?**
A: Those sales are excluded (already reported in previous ITR)

**Q: Can I choose which shares to sell?**
A: No, FIFO is mandatory per Indian tax law

**Q: What if TTBR is missing for sale date?**
A: Script will error out - you need to manually add that date's TTBR to the CSV
