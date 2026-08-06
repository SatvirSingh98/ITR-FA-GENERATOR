# Refactoring Plan: Modular Architecture

## Status: PHASE 1 COMPLETE ✅

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

## Phase 2 Pending - Legacy Features (3/10)

### ⏳ 8. ScheduleFAGenerator (`scripts/schedule_fa_generator.py`) - TODO
**Responsibility:** Table A2 and A3 generation
**Methods:**
- `generate_table_a2()` - Account summary
- `generate_table_a3()` - Individual holdings
- `calculate_peak_values()` - Peak calculations
- `process_partial_sales()` - Split holdings/sold rows
**Status:** Still using legacy `itr_fa_etrade.py` code

### ⏳ 9. ScheduleOSFSIGenerator (`scripts/schedule_os_fsi_generator.py`) - TODO
**Responsibility:** Schedule OS and FSI
**Methods:**
- `generate_schedule_os()` - Dividend income
- `generate_schedule_fsi()` - Foreign source income
- `allocate_dividends_to_lots()` - Dividend allocation
**Status:** Still using legacy `itr_fa_etrade.py` code

### ⏳ 10. YahooFinanceScraper (`scripts/yahoo_scraper.py`) - TODO
**Responsibility:** Company details and stock price scraping
**Methods:**
- `scrape_company_info()` - Fetch company name, country
- `scrape_stock_prices()` - Get daily prices for calendar year
- `get_price_on_date()` - Get closing price for specific date
**Status:** Still using legacy `itr_fa_etrade.py` code

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

## Phase 2 TODO (Remaining 30% of features)

1. Create ScheduleFAGenerator for Table A2/A3
2. Create ScheduleOSFSIGenerator for dividend/FSI schedules
3. Create YahooFinanceScraper for company info + stock prices
4. Integrate all modules into main.py
5. Remove dependency on legacy `itr_fa_etrade.py`
6. Full end-to-end testing

## Rollback Plan

If refactoring fails, rollback to commit: `25c8bde` (working monolithic version)

## Commit History

- `dcc10e1` - Phase 1: Core modules (Config, Tax, Forex)
- **PENDING** - Phase 1 Complete: Added Parser, CG, Formatter, Main orchestrator
