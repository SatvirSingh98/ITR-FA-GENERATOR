# Refactoring Plan: Modular Architecture

## Status: PHASE 2A IN PROGRESS ⏳

## Goal
Refactor monolithic `itr_fa_etrade.py` (3,508 lines) into modular, class-based architecture.

## Phase 1 Complete - Core Modules (7/10) ✅

### ✅ 1. ConfigManager (`scripts/config_manager.py`) - 70 lines
**Responsibility:** Configuration management
**Methods:**
- `load()` - Load config.json
- `save()` - Save config.json
- `get_target_year()` - Get target year
- `get_account_info()` - Get account details
- `get/set_company_config()` - Company-specific settings

### ✅ 2. TaxCalculator (`scripts/tax_calculator.py`) - 260 lines
**Responsibility:** Tax rate calculations + advance tax scheduling
**Methods:**
- `calculate_stcg_rates_for_income(bracket)` - Get rates for both regimes
- `calculate_tax(gain, type, regime)` - Calculate tax amount
- `calculate_advance_tax_installment(tax, date)` - Jul/Sep/Dec/Mar schedule
- `group_sales_by_period(sales)` - Group by advance tax deadline period
- `get_ltcg_rate()` - Get LTCG rate (12.5%)
- `get_stcg_rate(regime)` - Get STCG rate for regime

### ✅ 3. ForexManager (`scripts/forex_manager.py`) - 138 lines
**Responsibility:** Exchange rate management
**Methods:**
- `load_forex_data()` - Load SBI TTBR data
- `get_ttbr(date)` - Get rate for date
- `get_rule_115_1_f_ttbr(sale_date)` - Capital gains exchange rate
- `get_rule_115_1_e_ttbr(dividend_date)` - Dividend exchange rate

### ✅ 4. ETradeParser (`scripts/etrade_parser.py`) - 270 lines
**Responsibility:** Parse E*TRADE export files
**Methods:**
- `discover_input_files()` - Find ByStatus, G&L, Transaction History, ClientStatement
- `parse_bystatus(file)` - Parse ByStatus_expanded.xlsx
- `parse_gains_losses(file)` - Parse G&L_Expanded.xlsx (calendar + extended)
- `parse_transaction_history(file)` - Parse Transaction_History.csv
- `parse_client_statement(file)` - Extract account number and ending value
- `discover_companies()` - Extract unique symbols
- `extract_pre_fy_acquisition_dates()` - Pre-FY dates for TTBR loading

### ✅ 5. CapitalGainsGenerator (`scripts/capital_gains_generator.py`) - 220 lines
**Responsibility:** Calculate capital gains (dual-regime)
**Methods:**
- `process_sales(sales_data)` - Process all sales
- `calculate_holding_period(acq, sale)` - Calculate months held
- `calculate_tax_for_regime(sales, regime)` - Calculate for one regime
- `generate_dual_regime_results()` - Calculate for BOTH regimes
- `create_sale_details_dataframe()` - Format for Excel
- `create_advance_tax_dataframe()` - Grouped advance tax schedule

### ✅ 6. ExcelFormatter (`scripts/excel_formatter.py`) - 240 lines
**Responsibility:** Excel output with professional formatting
**Methods:**
- `format_capital_gains_sheet()` - Dual-regime CG formatting
- `format_standard_sheet()` - Standard sheet formatting
- `auto_size_columns()` - Auto-size based on content
- `format_workbook()` - Format entire workbook

### ✅ 7. Main Orchestrator (`scripts/main.py`) - 180 lines
**Responsibility:** Entry point, coordinates all modules
**Methods:**
- `main(income_bracket)` - Main execution flow
- Instantiate all managers
- Coordinate data flow
- Generate all outputs
**Status:** Working with capital gains only (Schedule FA/OS/FSI pending)

## Phase 2A Complete - Additional Modules (3/10) ✅

### ✅ 8. YahooFinanceScraper (`scripts/yahoo_scraper.py`) - 420 lines
**Responsibility:** Company details and stock price scraping
**Methods:**
- `scrape_company_profile(symbol)` - Fetch company name, address, country code
- `scrape_stock_prices(symbol)` - Get daily prices for calendar year
- `detect_country(address)` - Map address to ITR country codes  
- `get_price_on_date(df, date)` - Get closing price with backward search
**Status:** Complete and ready for integration

### ✅ 9. ScheduleOSFSIGenerator (`scripts/schedule_os_fsi_generator.py`) - 230 lines
**Responsibility:** Schedule OS and FSI
**Methods:**
- `calculate_schedule_os(df_dividends)` - Apply Rule 115(1)(e) for dividends
- `calculate_schedule_fsi(df_dividends, df_cg)` - Aggregate foreign source income
- Quarterly breakup per Section 234C
**Status:** Complete and ready for integration

### ✅ 10. ScheduleFAGenerator (`scripts/schedule_fa_generator.py`) - 340 lines
**Responsibility:** Table A2 and A3 generation (SIMPLIFIED Phase 2A)
**Methods:**
- `read_client_statement()` - Extract account number and closing balance from PDF
- `generate_table_a2()` - Account summary (simplified peak calculation)
- `generate_table_a3()` - Placeholder for holdings (full implementation in Phase 2B)
**Status:** Simplified wrapper created - DELEGATES complex peak/dividend logic to legacy code
**Note:** Full peak calculations and dividend allocation deferred to Phase 2B (800+ lines of complex logic)

## Phase 2B Pending - Full Table A2/A3 Refactoring

### ⏳ Table A2/A3 Full Implementation
**Why deferred:** The legacy Table A2/A3 logic is 800+ lines of highly complex code:
- Daily matrix calculations (stock price × TTBR for every day)
- Peak value detection across different holding windows
- Partial sale handling (split into separate rows)
- Per-lot dividend allocation based on holdings on dividend dates
- Pre-FY TTBR loading with backward search

**Phase 2B Plan:**
- Extract PeakCalculator class for daily matrix and peak detection
- Extract DividendAllocator class for per-lot dividend distribution
- Extract TrancheProcessor class for holdings/sales processing
- Break 800-line monolith into 4-5 focused classes
- Full test coverage
- Remove dependency on legacy code

## Benefits Achieved

1. **Maintainability:** Each module handles ONE responsibility (~70-270 lines each)
2. **Debuggability:** Easy to find and fix issues in specific module
3. **Testability:** Can test each class independently
4. **Reusability:** Classes can be reused in other projects
5. **Readability:** ~200 lines per file vs 3,508 lines monolith
6. **Extensibility:** Easy to add new features

## Phase 1 Test Results ✅

- [x] Config loading working
- [x] Forex rates loading (CSV parsing fixed for uppercase columns)
- [x] Tax calculation (dual-regime) working
- [x] E*TRADE parsing working (ByStatus, G&L, Transaction History)
- [x] Capital gains calculation working (base + dual-regime)
- [x] Excel output working with professional formatting
- [x] GENERATE_ITR_FA.bat updated to use `scripts/main.py`

## Phase 2A Status ⏳

**Completed:**
- [x] YahooFinanceScraper module (420 lines)
- [x] ScheduleOSFSIGenerator module (230 lines)
- [x] ScheduleFAGenerator simplified wrapper (340 lines)
- [x] Documentation of Phase 2A vs 2B split rationale

**Pending:**
- [ ] Integrate Phase 2A modules into main.py
- [ ] Test with legacy fallback for Table A2/A3
- [ ] Update __init__.py version to 2.1.0
- [ ] Commit Phase 2A to GitHub

## Phase 2B TODO (Future - Full Table A2/A3 Refactoring)

1. Extract PeakCalculator class (~200 lines)
2. Extract DividendAllocator class (~150 lines)
3. Extract TrancheProcessor class (~250 lines)
4. Extract MatrixBuilder class (~200 lines)
5. Integrate into ScheduleFAGenerator
6. Remove dependency on legacy `itr_fa_etrade.py`
7. Full end-to-end testing with complex scenarios

## Rollback Plan

If refactoring fails, rollback to commit: `25c8bde` (working monolithic version)

## Commit History

- `dcc10e1` - Phase 1: Core modules (Config, Tax, Forex)
- `dc1770e` - Phase 1 Complete: Added Parser, CG, Formatter, Main orchestrator
- **PENDING** - Phase 2A: YahooScraper, OS/FSI, simplified FA wrapper
