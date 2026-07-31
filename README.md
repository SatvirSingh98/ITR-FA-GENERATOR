# Schedule FA Generator for ITR2

Automated generator for Schedule FA (Foreign Assets) for ITR2 filing in India.

---

## 🚀 Quick Start (2 Steps)

### Step 1: Add E*TRADE Files
Place these files in `inputs/` folder:
- `ByStatus_expanded.xlsx` (required)
- `G&L_Expanded.xlsx` (optional - only if you sold stocks in this FY)

### Step 2: Run
Double-click: **`GENERATE_ITR_FA.bat`**

**First run:** Auto-creates venv, installs packages, generates files (~3-5 minutes)  
**Next runs:** Just generates files (~1-2 minutes)

Check `outputs/` folder for generated files.

---

## What This Tool Does

✅ **Fully automated** - Auto-discovers companies from your E*TRADE files  
✅ **Multi-company** - Handles AMD, NVDA, GOOGL, etc. automatically  
✅ **Multi-country** - Auto-detects USA, Canada, UK, etc. from company address  
✅ **No manual data entry** - Fetches company info from Yahoo Finance  
✅ **Capital gains** - Calculates LTCG/STCG with advance tax schedule (Rule 234C)  
✅ **Complete output** - JSON + Excel (7 sheets) + 2 CSVs + output log  
✅ **Beautiful formatting** - Professional Excel with currency symbols, colors, borders  

---

## Important Limitations

### ⚠️ E*TRADE Only
This script is designed specifically for E*TRADE's export file format. Won't work with Fidelity/Morgan Stanley files without modification.

### ⚠️ One Account Per Run
Processes ONE custodial account at a time. All holdings in input files belong to the same account.

**Multiple accounts?** Run the script separately for each account, then combine outputs manually.

---

## Multi-Country Support

Script auto-detects countries from Yahoo Finance addresses!

**Supported:** USA, Canada, UK, Germany, France, Japan, Australia, Switzerland, Netherlands, Singapore, Hong Kong, China, South Korea, Taiwan, India, Brazil, Mexico, Israel, Ireland, Spain, Italy

**Example:**
- AMD (USA) → USA, Code 2
- Shopify (Canada) → Canada, Code 3  
- BP (UK) → UK, Code 1

All automatic! Defaults to USA if detection fails.

---

## Configuration

Edit `config.json`:

```json
{
  "target_year": 2025,
  
  "custodial_account": {
    "country_name": "UNITED STATES OF AMERICA",
    "country_code": "2",
    "financial_institution_name": "E*TRADE Securities LLC",
    "financial_institution_address": "1271 Avenue...",
    "zip_code": "10020",
    "account_number": "ENTER_YOUR_ETRADE_ACCOUNT_NUMBER",
    "status": "BENEFICIAL_OWNER",
    "account_opening_date": ""
  },
  
  "table_a3_companies": {}
}
```

**Note:** Leave `table_a3_companies` empty - auto-filled by script!

---

## Output Files

Generated in `outputs/` folder:

1. **schedule_fa_2025-26.json** - Upload to ITR e-filing portal
2. **schedule_fa_2025-26.xlsx** - Review with CA (7 beautifully formatted sheets):
   - **Table A2 Custodial Acc** - Account summary with peak & closing balance
   - **Table A3 Equity Interest** - Individual holdings (RSU/ESPP tranches)
   - **Excluded from A3** - Audit trail of holdings removed (sold in previous years)
   - **Capital Gains** - Sale details with LTCG/STCG tax calculations + Advance tax schedule
   - **Reference - Daily Rates** - Stock prices + SBI TTBR + Peak per-share info
   - **A2 Peak Calculation** - Daily account values showing peak date
   - **Pre-FY Holdings Init Val** - Initial value details for pre-FY acquisitions
3. **schedule_fa_2025-26_table_a2.csv** - ITR format
4. **schedule_fa_2025-26_table_a3.csv** - ITR format
5. **output_summary.txt** - Generation log with all console output

---

## Capital Gains & Advance Tax

The tool automatically calculates capital gains for stock sales:

### Tax Rates
- **LTCG** (Long Term Capital Gains) - Holding > 24 months: **12.5% tax**
- **STCG** (Short Term Capital Gains) - Holding ≤ 24 months: **31.2% tax**

### Advance Tax Schedule (Income Tax Rule 234C)
For sales in the current/future FY, the tool calculates advance tax payment schedule:
- **By Jul 15:** 15% of total tax
- **By Sep 15:** 45% of total tax (cumulative)
- **By Dec 15:** 75% of total tax (cumulative)
- **By Mar 15:** 100% of total tax (cumulative)

### Date Filtering
- **Included in Capital Gains:** Sales from current FY onwards (for tax planning)
- **Excluded:** Sales from previous years (already reported)

---

## BAT Files

**`GENERATE_ITR_FA.bat`** - All-in-one runner (zero-config setup)
- **First run:** Auto-creates venv + installs packages + generates output
- **Next runs:** Just generates output
- Auto-validates Python version (requires 3.14+)
- Auto-creates config.json from example
- **Just double-click this file!**  

---

## Before Sharing

**Run:** `CLEAN_BEFORE_SHARING.bat`

Removes your personal data:
- E*TRADE files from `inputs/`
- Schedule FA from `outputs/`
- Verifies config has placeholder

---

## Technical Details

**Data Sources:**
- Stock prices: Yahoo Finance (web scraping)
- Exchange rates: SBI TTBR (independent fetcher - SBI PDF + GitHub fallback)
- Company info: Yahoo Finance profiles
- **Auto-updated daily** via GitHub Actions at 9:00 PM IST (see [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md))

**Requirements:**
- Python 3.14+ (auto-creates venv on first run)
- Chrome browser
- Internet connection

**Processing:**
- ~1-2 minutes per run
- ~249 trading days scraped
- Auto-country detection
- Peak value tracking

---

**E*TRADE Only** | **One Account Per Run** | **Auto-Discovery Enabled**  
**Version:** July 2026
