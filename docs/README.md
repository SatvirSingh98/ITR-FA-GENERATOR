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
- E*TRADE's actual lot matching (NOT forced FIFO)
- Legal basis: IT Act Circulars 704 and 768
- Gross proceeds and cost basis calculation
- Advance tax schedule (Rule 234C) in vertical format
- NEW vs OLD tax regime comparison (side-by-side)
- Why all tax amounts are rounded UP

**When to read:** When you want to understand how capital gains tax is calculated for stock sales and why we use E*TRADE's lot matching instead of forcing FIFO.

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

**Financial Year 2025-26:**
- Start: Apr 1, 2025
- End: Mar 31, 2026
- Assessment Year: 2026-27

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

The generated `schedule_fa_2025-26.xlsx` contains:

1. **Table A2 Custodial Acc** - Account summary (opening, peak, closing balance)
2. **Table A3 Equity Interest** - Individual holdings (all tranches)
3. **Capital Gains** - Simplified sheet with vertical advance tax format
   - Side-by-side NEW vs OLD regime comparison (when rates differ)
   - Single regime display (when rates are same)
   - Vertical advance tax schedule (Field | Value)
4. **Schedule OS** - Offset schedule for foreign tax credit
5. **Schedule FSI** - Foreign source income details
6. **Excluded from A3** - Audit trail (sold shares excluded from Table A3)
7. **A2 Peak Calculation** - Peak balance calculation workings
8. **A3 Peak Value Details** - Per-tranche peak value breakdown
9. **Pre-2025 Holdings Init Val** - Initial value for shares acquired before FY 2025-26
10. **2025 - Daily Rates** - Complete daily data matrix (Date | Price | TTBR | INR Value)

**Conditional Sheets (only if applicable):**
- **Dividends (Schedule FA)** - Only appears if you received dividends during the FY
- **Dividends (Schedule OS)** - Only appears if you received dividends during the FY

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
- **Solution:** Verify lot matching from E*TRADE G&L report in "Capital Gains" sheet, check acquisition dates are correct. We use E*TRADE's actual lot matching, not forced FIFO (per Circular 704).

**Problem:** "config.json has invalid JSON syntax" error before Python is installed
- **Solution:** Install Python first. The batch file will re-check JSON validity after Python setup

## Additional Resources

- [Main README.md](../README.md) - Quick start guide
- [AUTOMATION_SETUP.md](../AUTOMATION_SETUP.md) - GitHub Actions setup for daily SBI TTBR updates
- [config.json](../config.json) - Configuration settings

## Questions?

For technical questions about the calculations, refer to the specific documentation file above. For general usage questions, see the main README.md.

---

**Last Updated:** August 2026  
**Script Version:** FY 2025-26
