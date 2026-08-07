# Schedule FA Generator for ITR2/ITR3

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Automated generator for Schedule FA (Foreign Assets) for ITR2/ITR3 filing in India.

**Copyright (C) 2025 Satvir Singh**  
Licensed under GPL-3.0 - see [LICENSE](LICENSE) for details.

---

## 🚀 Quick Start (2 Steps)

### Step 1: Add E*TRADE Files
Place these files in `etrade_inputs/` folder:
- `ByStatus_expanded.xlsx` (REQUIRED - shows current holdings)
- `G&L_Expanded.xlsx` (REQUIRED if you sold ANY shares - contains sold shares for Table A3 + Capital Gains)
  - **Warning:** Without this file, Table A3 will be incomplete and Capital Gains will be empty
  - Only skip if you had ZERO sales during the year
- `Transaction_History.csv` (optional - only if you received dividends)

### Step 2: Run
Double-click: **`GENERATE_ITR_FA_ETRADE.bat`**

**First run:** Auto-creates venv, installs packages, generates files (~3-5 minutes)  
**Next runs:** Just generates files (~1-2 minutes)

Check `etrade_outputs/` folder for generated files.

---

## What This Tool Does

✅ **Fully automated** - Auto-discovers companies from your E*TRADE files  
✅ **Multi-company** - Handles AMD, NVDA, GOOGL, etc. automatically  
✅ **Multi-country** - Auto-detects USA, Canada, UK, etc. from company address  
✅ **No manual data entry** - Fetches company info from Yahoo Finance  
✅ **Capital gains** - Calculates LTCG/STCG with advance tax schedule (Rule 234C)  
✅ **Dividend support** - Auto-processes dividends with Schedule FA + Schedule OS  
✅ **Schedule OS & FSI** - Dividend income and foreign source income reporting  
✅ **Complete output** - JSON + Excel (9-11 sheets) + 2 CSVs + output log  
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

### ✅ Dividend Support (Schedule FA + Schedule OS + Schedule FSI)
The tool processes dividend income for COMPLETE ITR-2 filing:

**Schedule FA (Asset Disclosure):**
- **Table A2:** Creates separate rows for dividends and sales
- **Table A3:** Allocates dividend proportionally to each lot based on holdings on dividend payment date
- **Exchange Rate:** Exact credit date TTBR (per CBDT)

**Schedule OS (Other Sources Income):**
- **Total Dividend Income:** USD and INR totals
- **Quarterly Breakup:** Section 234C advance tax periods
- **Exchange Rate:** Rule 115(1)(e) - last day of month BEFORE dividend month
- **Financial Year:** Apr-Mar (different from Schedule FA's Jan-Dec!)

**Schedule FSI (Foreign Source Income):**
- **Dividend Income:** From Schedule OS
- **Capital Gains:** From Schedule CG
- **Total Foreign Income:** Combined reporting
- **Country Details:** USA with DTAA Article info

**Key Feature:** Tool generates BOTH exchange rates automatically:
- **Dividends (Schedule FA) sheet:** Exact date TTBR for asset disclosure
- **Dividends (Schedule OS) sheet:** Rule 115(1)(e) TTBR for tax calculation
- Shows the difference side-by-side!

**AMD Note:** AMD doesn't pay dividends, so this is optional for AMD employees

**Dividend Allocation Logic:**
- Each lot receives dividend proportionally based on shares held on dividend payment date
- Handles partial sales: reduces shares if sold before dividend date
- Supports multiple dividend payments: accumulates per lot
- Example: If Lot A has 10 shares and Lot B has 20 shares on dividend date, and total dividend is $30:
  - Lot A gets: (10/30) × $30 = $10
  - Lot B gets: (20/30) × $30 = $20

**Documentation:**
- **Schedule FA dividends (with per-lot allocation):** [docs/dividends.md](docs/dividends.md)
- **Schedule OS & FSI:** [docs/schedule_os_fsi.md](docs/schedule_os_fsi.md)

### ✅ Tax Withholding: Net Share Settlement vs Sell-to-Cover

**IMPORTANT:** Tool correctly handles BOTH tax withholding methods:

**Net Share Settlement (AMD typical):**
- Employer withholds shares **BEFORE issuing** them to you
- You never receive the withheld shares
- ✅ **NO Schedule FA/CG reporting** (shares never held)
- Tool correctly **ignores** these withholding rows

**Sell-to-Cover (Different brokers):**
- Employer issues ALL shares, broker **sells portion** on your behalf
- ✅ **MUST report in Schedule FA & CG** (actual sale)
- Tool correctly **includes** these from G&L_Expanded.xlsx

**How to tell the difference:**
- Net settlement: `Shares Traded for taxes` column = NULL in E*TRADE
- Sell-to-cover: Withholding sale appears in G&L_Expanded.xlsx (same-day sale)

**Documentation:** [docs/closed_lots_verification.md](docs/closed_lots_verification.md)  
**Source:** [ITRFA.in Sell-to-Cover Guide](https://itrfa.in/blog/schedule-fa-sell-to-cover-capital-gains)

### ✅ Table A3: Multiple Rows for Partial Sales

Partial sales create **TWO separate rows** with different peak and closing values.

**Example - Partial Sale:**
- Acquired: 11 ESPP shares on Nov 8, 2024
- Sold: 5 shares on Aug 15, 2025
- Holding: 6 shares as of Dec 31, 2025

**Output: TWO rows showing:**

**Row 1 (Holding):**
- Nature: "ESPP (6 shares)"
- Initial Value: ₹88,929 (for 6 shares)
- Peak Balance: Peak value of 6 shares (anytime in year)
- Closing Balance: ₹2,10,770 (6 shares on Dec 31)
- Gross Proceeds: ₹0

**Row 2 (Sold):**
- Nature: "ESPP (5 shares) Sold"
- Initial Value: ₹74,108 (for 5 shares)
- Peak Balance: Peak value of 5 shares (up to Aug 15 only)
- Closing Balance: ₹0
- Gross Proceeds: ₹2,01,805

**Why separate rows?** The two portions have genuinely different peak and closing values. Combining them would misstate both.

**Documentation:** [docs/table_a3_structure.md](docs/table_a3_structure.md)

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

Generated in `etrade_outputs/` folder:

1. **schedule_fa_2025-26.json** - Upload to ITR e-filing portal
2. **schedule_fa_2025-26.xlsx** - Review with CA (10 beautifully formatted sheets):
   - **Table A2 Custodial Acc** - Account summary with peak & closing balance
   - **Table A3 Equity Interest** - Individual holdings (RSU/ESPP tranches)
   - **Capital Gains** - Sale details with LTCG/STCG tax calculations + Advance tax schedule
   - **Schedule OS** - Dividend income (Other Sources)
   - **Schedule FSI** - Foreign Source Income summary
   - **Excluded from A3** - Audit trail of holdings removed (sold in previous years)
   - **2025 - Daily Rates** - Stock prices + SBI TTBR for each trading day
   - **A2 Peak Calculation** - Daily account values showing peak date
   - **A3 Peak Value Details** - Peak date, window, price breakdown for each lot
   - **Pre-2025 Holdings Init Val** - Initial value details for pre-FY acquisitions
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
- **STCG** (Short Term) - Holding ≤ 24 months: **User's income tax slab rate** (Section 48)
  - Script prompts for total taxable income bracket (11 options from ₹0-4L to ₹5Cr+)
  - Automatically calculates: Base rate + Surcharge (if income > ₹50L) + 4% cess
  - Effective rates range from 0% to 39.0% depending on income level
  - Examples: ₹24L-50L → 31.2%, ₹60L → 34.32%, ₹1.5Cr → 35.88%, ₹3Cr → 39.0%

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

**`GENERATE_ITR_FA_ETRADE.bat`** - All-in-one runner (zero-config setup)
- **First run:** Auto-creates venv + installs packages + generates output
- **Next runs:** Just generates output
- Auto-validates Python version (requires 3.11+)
- Auto-creates config.json from example
- **Just double-click this file!**  

---

## Before Sharing

Removes your personal data:
- E*TRADE files from `etrade_inputs/`
- Schedule FA from `etrade_outputs/`

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

---

## Credits & Acknowledgments

This tool was built with guidance and inspiration from:

**[ITRFA.in](https://itrfa.in/)** - Comprehensive ITR Schedule FA & CG guidance
- [Schedule CG for RSU & ESPP Sales](https://itrfa.in/blog/schedule-cg-rsu-espp) - Income-tax Rule 115(1)(f), Section 49(2AA), STCG/LTCG classification
- [SBI TTBR Rule 115](https://itrfa.in/blog/sbi-ttbr-rule-115) - Exchange rate rules for Schedule FA vs Schedule CG
- Their blog posts provided critical insights into correct tax computation per Indian Tax Law

**[sbi-fx-ratekeeper](https://github.com/sahilgupta/sbi-fx-ratekeeper)** by [@sahilgupta](https://github.com/sahilgupta)
- Community-maintained archive of SBI daily TTBR rates (2020-present)
- Used as fallback data source when SBI official PDF is unavailable
- Essential for historical rate lookups needed for Schedule FA Table A3 initial values

**Community Resources:**
- [Income Tax Department](https://incometaxindia.gov.in/) - Official ITR filing instructions
- [SBI Forex Rates](https://sbi.co.in/web/interest-rates/interest-rates/forex-rates) - Daily TTBR (Telegraphic Transfer Buying Rate)
- [Yahoo Finance](https://finance.yahoo.com/) - Stock price data and company profiles

Thank you to all contributors and maintainers of these invaluable resources!
