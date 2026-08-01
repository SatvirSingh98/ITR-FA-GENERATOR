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

## Important Features

### ✅ ESPP Cost Basis Fix (Section 49(2AA))
The tool correctly uses **FMV on purchase date** for ESPP shares (NOT the discounted purchase price):
- **E*TRADE reports:** Adjusted Cost Basis = discounted price (e.g., $118.59 with 15% discount)
- **Indian Tax Law:** Must use FMV on purchase date (e.g., $152.39)
- **Tool uses:** "Purchase Date Fair Mkt. Value" column from E*TRADE
- **Impact:** Significantly higher initial value and cost basis for ESPP shares
- **Per ITRFA.in:** "If employer taxed the discount, Indian cost = FMV on purchase date"

### ✅ Future Sales for Advance Tax Planning
The tool includes future sales (after current FY) in Capital Gains sheet:
- Shows estimated tax amount for sales that haven't happened yet
- Calculates when to pay advance tax (Jul/Sep/Dec/Mar of next FY)
- Helps you plan: "If shares sell in Jun 2026, pay by Sep 15, 2026"
- Marked with "- FUTURE" in nature column

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
  
  "disclose_unvested_rsu": false,
  
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

**Configuration Notes:**
- **`disclose_unvested_rsu`**: Set to `true` for conservative approach (disclose unvested RSUs as beneficial interest). Default: `false` (practical approach - defer until vesting). Per ITRFA.in: "some CAs defer until vesting". Consult your CA if unsure.
- **`table_a3_companies`**: Leave empty - auto-filled by script!

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

The tool automatically calculates capital gains for stock sales AND future sales for advance tax planning:

### Tax Classification (Per ITRFA.in)
Foreign company shares (RSU/ESPP) = **UNLISTED securities** (no STT on Indian exchange)

**Holding Period Threshold:** 24 months (NOT 12 months for STT-paid Indian listed equity)
- **CRITICAL:** Use **calendar months**, NOT day count (730 days fails in leap years!)
- **CRITICAL:** Sale on 24-month anniversary = STILL short-term (per Section 2(42A))

**Tax Rates & Sections:**
- **LTCG** (Long Term) - Holding > 24 months: **12.5% tax** (Section 112, no indexation)
- **STCG** (Short Term) - Holding ≤ 24 months: **31.2% tax** (Section 48, slab rate)

### Advance Tax Schedule (Income Tax Rule 234C)
The Capital Gains sheet shows advance tax installments for:
1. **Current FY Sales** (Jan 2025 - Mar 2026): Tax to be paid with this year's ITR
2. **Future Sales** (Apr 2026 onwards): Advance tax planning for next FY

Advance tax payment schedule (based on sale date):
- **By Jul 15:** 15% of total tax
- **By Sep 15:** 45% of total tax (cumulative)
- **By Dec 15:** 75% of total tax (cumulative)
- **By Mar 15:** 100% of total tax (cumulative)

### Exchange Rate Rules (CRITICAL - Different for FA vs CG!)
**Schedule FA (Table A2/A3):**
- **Rule:** CBDT filing instructions
- **Rate:** **Exact date** SBI TTBR
- **Example:** Vest on Jul 15, 2025 → Use Jul 15, 2025 TTBR

**Schedule CG (Capital Gains):**
- **Rule:** Income-tax Rule 115(1)(f)
- **Rate:** **Last day of month BEFORE sale month** SBI TTBR
- **CRITICAL:** SAME rate for BOTH proceeds AND cost basis
- **Example:** Sale on Aug 15, 2025 → Use **Jul 31, 2025** TTBR for everything
- **Example:** Sale on Jan 1, 2026 → Use **Dec 31, 2025** TTBR for everything

**Common mistake:** Using exact sale/acquisition dates for Capital Gains (wrong! Use Rule 115(1)(f))

### Date Ranges (Per ITRFA.in Guidance)
- **Table A3 (Schedule FA):** Calendar year only (Jan 1 - Dec 31)
- **Capital Gains (Schedule CG):** Extended period (Jan 1 - Mar 31 next year) + Future sales
- **Why different?** Schedule FA uses calendar year, but Indian FY for capital gains is Apr-Mar
- Sales in Jan-Mar next year: Appear in Capital Gains THIS year, but Table A3 NEXT year

---

## BAT Files

**`GENERATE_ITR_FA.bat`** - All-in-one runner (zero-config setup)
- **First run:** Auto-creates venv + installs packages + generates output
- **Next runs:** Just generates output
- Auto-validates Python version (requires 3.11+)
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
- Python 3.11+ (auto-creates venv on first run)
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
