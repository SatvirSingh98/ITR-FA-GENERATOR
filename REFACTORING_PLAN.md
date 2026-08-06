# Refactoring Plan: Modular Architecture

## Status: IN PROGRESS

## Goal
Refactor monolithic `itr_fa_etrade.py` (3,508 lines) into modular, class-based architecture.

## Completed Modules

### ✅ 1. ConfigManager (`scripts/config_manager.py`)
**Responsibility:** Configuration management
**Methods:**
- `load()` - Load config.json
- `save()` - Save config.json
- `get_target_year()` - Get target year
- `get_account_info()` - Get account details
- `get/set_company_config()` - Company-specific settings

### ✅ 2. TaxCalculator (`scripts/tax_calculator.py`)
**Responsibility:** Tax rate calculations for both regimes
**Methods:**
- `calculate_stcg_rates_for_income(bracket)` - Get rates for both regimes
- `calculate_tax(gain, type, regime)` - Calculate tax amount
- `get_ltcg_rate()` - Get LTCG rate (12.5%)
- `get_stcg_rate(regime)` - Get STCG rate for regime

### ✅ 3. ForexManager (`scripts/forex_manager.py`)
**Responsibility:** Exchange rate management
**Methods:**
- `load_forex_data()` - Load SBI TTBR data
- `get_ttbr(date)` - Get rate for date
- `get_rule_115_1_f_ttbr(sale_date)` - Capital gains exchange rate
- `get_rule_115_1_e_ttbr(dividend_date)` - Dividend exchange rate

## Pending Modules

### 4. ETradeParser (`scripts/etrade_parser.py`)
**Responsibility:** Parse E*TRADE export files
**Methods:**
- `parse_bystatus(file)` - Parse ByStatus_expanded.xlsx
- `parse_gains_losses(file)` - Parse G&L_Expanded.xlsx
- `parse_client_statement(file)` - Parse ClientStatements PDF
- `discover_companies()` - Extract unique symbols

### 5. CapitalGainsGenerator (`scripts/capital_gains_generator.py`)
**Responsibility:** Calculate capital gains (dual-regime)
**Methods:**
- `process_sales(sales_data)` - Process all sales
- `calculate_for_regime(sales, regime)` - Calculate for one regime
- `match_lots(sale)` - Match sale to acquisition lot
- `calculate_holding_period(acq, sale)` - Calculate months held

### 6. AdvanceTaxCalculator (`scripts/advance_tax_calculator.py`)
**Responsibility:** Advance tax schedule (Rule 234C)
**Methods:**
- `calculate_schedule(capital_gains)` - Generate advance tax schedule
- `group_by_sale_period(sales)` - Group sales by deadline
- `calculate_installments(tax, sale_date)` - Calculate Jul/Sep/Dec/Mar amounts

### 7. ScheduleFAGenerator (`scripts/schedule_fa_generator.py`)
**Responsibility:** Table A2 and A3 generation
**Methods:**
- `generate_table_a2()` - Account summary
- `generate_table_a3()` - Individual holdings
- `calculate_peak_values()` - Peak calculations
- `process_partial_sales()` - Split holdings/sold rows

### 8. ScheduleOSFSIGenerator (`scripts/schedule_os_fsi_generator.py`)
**Responsibility:** Schedule OS and FSI
**Methods:**
- `generate_schedule_os()` - Dividend income
- `generate_schedule_fsi()` - Foreign source income
- `allocate_dividends_to_lots()` - Dividend allocation

### 9. ExcelFormatter (`scripts/excel_formatter.py`)
**Responsibility:** Excel output with professional formatting
**Methods:**
- `create_workbook()` - Initialize Excel file
- `write_capital_gains_dual_regime()` - Write CG sheet with 4 sections
- `apply_formatting()` - Apply colors, borders, alignment
- `format_capital_gains_sheet()` - Special CG formatting

### 10. Main Orchestrator (`scripts/main.py`)
**Responsibility:** Entry point, coordinates all modules
**Methods:**
- `main(income_bracket)` - Main execution flow
- Instantiate all managers
- Coordinate data flow
- Generate all outputs

## Benefits

1. **Maintainability:** Each module handles ONE responsibility
2. **Debuggability:** Easy to find and fix issues in specific module
3. **Testability:** Can test each class independently
4. **Reusability:** Classes can be reused in other projects
5. **Readability:** ~300 lines per file vs 3,508 lines
6. **Extensibility:** Easy to add new features

## Next Steps

1. Create remaining 7 modules
2. Create main.py orchestrator
3. Update GENERATE_ITR_FA.bat to use `scripts/main.py`
4. Test with sample data
5. Commit when all tests pass

## Rollback Plan

If refactoring fails, rollback to commit: `25c8bde` (working version)
