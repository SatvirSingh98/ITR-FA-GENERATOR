# ITR Schedule FA Generator - Documentation

This folder contains detailed technical documentation for understanding how the ITR Schedule FA Generator calculates various values.

## Documentation Index

### 1. [Reference Sheet - Daily Rates](reference_sheet.md)
**What it covers:**
- Complete daily data matrix (Date, Stock Price, TTBR, INR Value)
- How peak value is identified
- Data sources (Yahoo Finance + SBI TTBR)
- How to verify calculations

**When to read:** When you want to understand the raw daily data and how peak dates are determined.

---

### 2. [Table A2 - Peak Balance Calculation](table_a2_peak_calculation.md)
**What it covers:**
- How peak balance is calculated for custodial accounts
- Daily valuation matrix methodology
- Peak per share calculation
- Why peak date might differ from peak USD price date
- Multiple symbol handling

**When to read:** When you want to understand how the "Peak Balance During Period" is calculated for Table A2.

---

### 3. [Capital Gains Calculation](capital_gains.md)
**What it covers:**
- LTCG vs STCG classification (24-month rule)
- Tax rates (12.5% vs 31.2%)
- FIFO (First-In, First-Out) matching logic
- Gross proceeds and cost basis calculation
- Advance tax schedule (Rule 234C)
- Why all tax amounts are rounded UP

**When to read:** When you want to understand how capital gains tax is calculated for stock sales.

---

### 4. [Pre-FY Holdings - Initial Value](holding_init_value.md)
**What it covers:**
- How initial value is calculated for shares acquired before the FY
- Why historical TTBR is needed
- ±3 day buffer for weekends/holidays
- How pre-FY data is downloaded and cached
- Relationship to Table A3

**When to read:** When you have holdings acquired before the current financial year and want to understand how their initial values are determined.

---

## Quick Reference

### Common Calculations

**Initial Value (for any tranche):**
```
Initial Value (INR) = Quantity × Stock Price (USD) on Acquisition Date × TTBR on Acquisition Date
```

**Peak Value (for any tranche):**
```
Peak Value (INR) = Quantity × MAX(Stock Price USD × TTBR) across all FY dates
```

**Closing Value (for any tranche):**
```
Closing Value (INR) = Quantity × Stock Price (USD) on Mar 31 × TTBR on Mar 31
```

**Capital Gain (per sale):**
```
Capital Gain = Gross Proceeds - Cost Basis
Tax = Capital Gain × (12.5% for LTCG or 31.2% for STCG)
```

### Key Dates

**Financial Year {YEAR}-26:**
- Start: Apr 1, {FY_START_YEAR}
- End: Mar 31, {FY_END_YEAR}
- Assessment Year: {YEAR+1}-27

**Advance Tax Due Dates:**
- Jul 15: 15% of total tax
- Sep 15: 45% of total tax
- Dec 15: 75% of total tax
- Mar 15: 100% of total tax

### Data Sources

**Stock Prices:**
- Source: Yahoo Finance (web scraping)
- Coverage: All trading days in the calendar year
- Format: Daily closing prices in USD

**SBI TTBR (Exchange Rates):**
- Source: SBI official PDF + GitHub historical data
- Coverage: 2020-present
- Format: USD/INR TT Buying Rate
- Location: `data/SBI_FOREX_CARD_RATES_USD.csv`

**E*TRADE Data:**
- Holdings: `etrade_inputs/ByStatus_expanded.xlsx` (REQUIRED)
- Sales: `etrade_inputs/G&L_Expanded.xlsx` (REQUIRED if you sold any shares during the year)
  - **Important:** G&L file contains sold shares which are removed from ByStatus
  - Without it, Table A3 will be incomplete and Capital Gains will be empty
  - Only skip this file if you had ZERO sales during the year

### Excel Output Sheets

The generated `schedule_fa_{YEAR}-{YEAR+1}.xlsx` contains:

1. **Table A2 Custodial Acc** - Account summary (opening, peak, closing)
2. **Table A3 Equity Interest** - Individual holdings (all tranches)
3. **Excluded from A3** - Audit trail (sold shares excluded)
4. **Capital Gains** - Tax calculations for sales
5. **Reference - Daily Rates** - Complete daily data matrix
6. **A2 Peak Calculation** - Peak balance workings
7. **Pre-FY Holdings Init Val** - Historical initial value calculations

### Rounding Rules

**All monetary values:**
- Always rounded **UP** using `math.ceil()`
- Reason: Tax compliance (never underpay)
- Example: ₹5,750.01 → ₹5,751

**Exception:** Display values in reference sheets may use 2 decimal places for readability, but calculations use ceiling.

## Understanding the Flow

```
1. Load E*TRADE Files
   ↓
2. Discover Companies (AMD, NVDA, etc.)
   ↓
3. Download SBI TTBR (current year + pre-FY dates)
   ↓
4. Scrape Stock Prices (Yahoo Finance)
   ↓
5. Build Daily Valuation Matrix (Date | Price | TTBR | INR Value)
   ↓
6. Calculate Values:
   - Initial Value (acquisition date)
   - Peak Value (max across all dates)
   - Closing Value (Mar 31)
   ↓
7. Process Sales (if any):
   - FIFO matching
   - Capital gains
   - Tax calculation
   ↓
8. Generate Output:
   - JSON (for ITR portal upload)
   - Excel (7 sheets for CA review)
   - CSVs (Table A2 + A3)
```

## Troubleshooting

**Problem:** "Python not found" error when running GENERATE_ITR_FA_ETRADE.bat
- **Solution:** Install Python 3.11+ from [python.org](https://python.org/downloads/) and check "Add Python to PATH" during installation

**Problem:** Warning about G&L_Expanded.xlsx missing
- **Solution:** 
  - If you sold shares: Export G&L report from E*TRADE and place in `etrade_inputs/` folder
  - If you had ZERO sales: Press any key to continue (script will skip capital gains)

**Problem:** Table A3 missing sold shares
- **Solution:** Sold shares only appear in G&L_Expanded.xlsx, not ByStatus. Make sure G&L file is present in etrade_inputs/

**Problem:** Missing TTBR for a date
- **Solution:** Check `data/SBI_FOREX_CARD_RATES_USD.csv` and manually add the missing date

**Problem:** Stock price not found for acquisition date
- **Solution:** Verify date format in E*TRADE file (YYYY-MM-DD), check if market was closed that day

**Problem:** Peak value seems wrong
- **Solution:** Check "A2 Peak Calculation" sheet to see which date was identified as peak and why

**Problem:** Capital gains calculation looks off
- **Solution:** Verify FIFO matching in "Capital Gains" sheet, check acquisition dates are correct

**Problem:** "config.json has invalid JSON syntax" error before Python is installed
- **Solution:** Install Python first. The batch file will re-check JSON validity after Python setup

## Additional Resources

- [Main README.md](../README.md) - Quick start guide
- [AUTOMATION_SETUP.md](../AUTOMATION_SETUP.md) - GitHub Actions setup for daily SBI TTBR updates
- [config.json](../config.json) - Configuration settings

## Questions?

For technical questions about the calculations, refer to the specific documentation file above. For general usage questions, see the main README.md.

---

**Last Updated:** July {YEAR+1}  
**Script Version:** FY {YEAR}-{YEAR+1}
