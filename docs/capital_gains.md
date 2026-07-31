# Capital Gains Calculation

## Overview
The **Capital Gains** sheet calculates tax liability on stock sales, categorized as Long-Term Capital Gains (LTCG) or Short-Term Capital Gains (STCG) based on holding period.

## Holding Period Rules

### Long-Term Capital Gains (LTCG)
- **Holding Period:** > 24 months
- **Tax Rate:** 12.5%
- **Calculation:** Always rounded UP using `math.ceil()`

### Short-Term Capital Gains (STCG)
- **Holding Period:** ≤ 24 months
- **Tax Rate:** 31.2%
- **Calculation:** Always rounded UP using `math.ceil()`

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

### Step 4: Calculate Gross Proceeds (INR)
```python
Gross Proceeds (INR) = math.ceil(Quantity × Sale Price (USD) × TTBR on Sale Date)
```

**Example:**
- Sold: 10 shares
- Sale Price: $200 USD
- TTBR on sale date: 84.50
- **Gross Proceeds = ceil(10 × 200 × 84.50) = ₹1,69,000**

### Step 5: Calculate Cost Basis (INR)
```python
Cost Basis (INR) = math.ceil(Quantity × Acquisition Price (USD) × TTBR on Acquisition Date)
```

**Example:**
- Acquired: 10 shares on 2023-06-10
- Acquisition Price: $150 USD
- TTBR on 2023-06-10: 82.00
- **Cost Basis = ceil(10 × 150 × 82.00) = ₹1,23,000**

### Step 6: Calculate Capital Gain
```python
Capital Gain = Gross Proceeds - Cost Basis
```

**Example:**
- Gross Proceeds: ₹1,69,000
- Cost Basis: ₹1,23,000
- **Capital Gain = ₹46,000**

### Step 7: Calculate Tax
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
| Symbol | Stock ticker (e.g., AMD) |
| Sale Date | When shares were sold |
| Quantity | Number of shares sold |
| Acquisition Date | When those shares were acquired |
| Holding Period | Months held |
| Type | LTCG or STCG |
| Gross Proceeds (INR) | Sale value in rupees |
| Cost Basis (INR) | Purchase cost in rupees |
| Capital Gain (INR) | Profit |
| Tax Rate | 12.5% or 31.2% |
| Tax (INR) | Tax liability |

Plus a summary section with:
- Total LTCG
- Total STCG
- Combined Tax
- Advance Tax Schedule

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

### 2. TTBR Date Matching
- Sale: Use TTBR on **sale date**
- Acquisition: Use TTBR on **acquisition date**
- If TTBR missing for a date, the script will fail (needs manual intervention)

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
