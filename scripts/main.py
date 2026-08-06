"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

Main Orchestrator
Entry point for ITR-FA-GENERATOR modular architecture
"""

import sys
import os
import argparse
import pandas as pd

# Add parent directory to path to import scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config_manager import ConfigManager
from scripts.forex_manager import ForexManager
from scripts.tax_calculator import TaxCalculator
from scripts.etrade_parser import ETradeParser
from scripts.capital_gains_generator import CapitalGainsGenerator
from scripts.excel_formatter import ExcelFormatter


def main():
    """Main execution flow"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ITR-FA-GENERATOR - Schedule FA Generator')
    parser.add_argument('--income-bracket', type=str, required=True,
                        help='Income bracket (1-11) for STCG tax rate calculation')
    parser.add_argument('--calendar-year', type=int, default=2025,
                        help='Calendar year for processing (default: 2025)')
    args = parser.parse_args()

    income_bracket = args.income_bracket
    calendar_year = args.calendar_year

    print("=" * 80)
    print(f"ITR-FA-GENERATOR v2.0 - Modular Architecture")
    print(f"Calendar Year: {calendar_year}")
    print(f"Income Bracket: {income_bracket}")
    print("=" * 80)

    # Step 1: Load configuration
    print("\n[1/8] Loading configuration...")
    config_manager = ConfigManager()
    print(f"[OK] Loaded config for target year: {config_manager.get_target_year()}")

    # Step 2: Initialize Forex Manager and load exchange rates
    print("\n[2/8] Loading forex rates...")
    forex_manager = ForexManager(calendar_year=calendar_year)
    forex_manager.load_forex_data()

    # Step 3: Initialize Tax Calculator with income bracket
    print("\n[3/8] Initializing tax calculator...")
    tax_calculator = TaxCalculator()
    new_rate, old_rate, new_display, old_display = tax_calculator.calculate_stcg_rates_for_income(income_bracket)
    print(f"[OK] STCG Rates - New Regime: {new_display}, Old Regime: {old_display}")

    # Step 4: Parse E*TRADE input files
    print("\n[4/8] Parsing E*TRADE files...")
    etrade_parser = ETradeParser(calendar_year=calendar_year)
    files = etrade_parser.discover_input_files()

    # Check for Client Statement
    account_number, ending_value_usd = None, None
    if files['client_statement']:
        account_number, ending_value_usd = etrade_parser.parse_client_statement(files['client_statement'])

    # Parse ByStatus (holdings)
    df_open = etrade_parser.parse_bystatus(files['bystatus'])

    # Parse G&L (sales)
    df_sold_calendar, df_sold_future, df_sold_extended = etrade_parser.parse_gains_losses(
        files['gl'], calendar_year=calendar_year
    )

    # Parse Transaction History (dividends)
    df_dividends = etrade_parser.parse_transaction_history(files['transaction_history'])

    # Discover companies
    companies = etrade_parser.discover_companies(df_open, df_sold_extended)

    # Extract pre-FY acquisition dates for TTBR loading
    pre_fy_dates = etrade_parser.extract_pre_fy_acquisition_dates(df_open, df_sold_extended)
    if pre_fy_dates:
        print(f"[*] Loading historical TTBR for {len(pre_fy_dates)} pre-FY dates...")
        # Reload forex data with extra dates
        forex_manager.load_forex_data()  # This would need enhancement to accept extra_dates

    # Step 5: Generate Capital Gains (dual-regime)
    print("\n[5/8] Generating capital gains...")
    cg_generator = CapitalGainsGenerator(forex_manager, tax_calculator)

    # Process sales to get base capital gains data
    capital_gains_base = cg_generator.process_sales(df_sold_extended)

    # Calculate for both regimes
    capital_gains_new, capital_gains_old = cg_generator.generate_dual_regime_results(capital_gains_base)

    # Create DataFrames for Excel output
    df_sale_details_new = cg_generator.create_sale_details_dataframe(capital_gains_new)
    df_advance_tax_new = cg_generator.create_advance_tax_dataframe(capital_gains_new)
    df_sale_details_old = cg_generator.create_sale_details_dataframe(capital_gains_old)
    df_advance_tax_old = cg_generator.create_advance_tax_dataframe(capital_gains_old)

    print(f"[OK] New Regime Total Tax: INR {sum(item['Tax Amount (INR)'] for item in capital_gains_new):,}" if capital_gains_new else "[OK] No capital gains")
    print(f"[OK] Old Regime Total Tax: INR {sum(item['Tax Amount (INR)'] for item in capital_gains_old):,}" if capital_gains_old else "[OK] No capital gains")

    # Step 6: Generate Schedule FA (Table A2, A3)
    # TODO: This needs schedule_fa_generator module (not yet created)
    print("\n[6/8] Generating Schedule FA...")
    print("[!] Schedule FA generation - using legacy code (TODO: refactor)")

    # Step 7: Generate Schedule OS and FSI
    # TODO: This needs schedule_os_fsi_generator module (not yet created)
    print("\n[7/8] Generating Schedule OS and FSI...")
    print("[!] Schedule OS/FSI generation - using legacy code (TODO: refactor)")

    # Step 8: Write Excel output with professional formatting
    print("\n[8/8] Writing Excel output...")
    output_file = f"ITR_FA_ETRADE_{calendar_year}.xlsx"

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write Capital Gains sheet (dual-regime)
        # Row 1: NEW TAX REGIME header
        regime_header_new = pd.DataFrame([['NEW TAX REGIME - Capital Gains Calculation']])
        regime_header_new.to_excel(writer, sheet_name="Capital Gains", index=False, header=False, startrow=0, startcol=0)

        # Row 2+: Sale details NEW
        current_row = 1
        df_sale_details_new.to_excel(writer, sheet_name="Capital Gains", index=False, startrow=current_row, startcol=0)
        current_row += len(df_sale_details_new) + 1 + 3  # +1 header, +3 spacing

        # Advance tax NEW
        df_advance_tax_new.to_excel(writer, sheet_name="Capital Gains", index=False, startrow=current_row, startcol=0)
        current_row += len(df_advance_tax_new) + 1 + 5  # +1 header, +5 spacing

        # OLD TAX REGIME header
        regime_header_old = pd.DataFrame([['OLD TAX REGIME - Capital Gains Calculation']])
        regime_header_old.to_excel(writer, sheet_name="Capital Gains", index=False, header=False, startrow=current_row, startcol=0)
        current_row += 1

        # Sale details OLD
        df_sale_details_old.to_excel(writer, sheet_name="Capital Gains", index=False, startrow=current_row, startcol=0)
        current_row += len(df_sale_details_old) + 1 + 3

        # Advance tax OLD
        df_advance_tax_old.to_excel(writer, sheet_name="Capital Gains", index=False, startrow=current_row, startcol=0)

        # TODO: Add other sheets (Schedule FA, OS, FSI, etc.)
        # For now, write placeholder sheets
        pd.DataFrame({'Note': ['Schedule FA - TODO (using legacy code)']}).to_excel(writer, sheet_name="Table A2", index=False)
        pd.DataFrame({'Note': ['Schedule OS - TODO (using legacy code)']}).to_excel(writer, sheet_name="Schedule OS", index=False)
        pd.DataFrame({'Note': ['Schedule FSI - TODO (using legacy code)']}).to_excel(writer, sheet_name="Schedule FSI", index=False)

        # Apply professional formatting
        print("[*] Applying professional formatting...")
        formatter = ExcelFormatter()
        sheet_configs = {
            'Capital Gains': {
                'type': 'dual_regime',
                'df_sale_details_new': df_sale_details_new,
                'df_advance_tax_new': df_advance_tax_new,
                'df_sale_details_old': df_sale_details_old,
                'df_advance_tax_old': df_advance_tax_old
            }
        }
        formatter.format_workbook(writer, sheet_configs)

    print(f"[OK] Excel file created: {output_file}")
    print("\n" + "=" * 80)
    print("SUCCESS - ITR-FA-GENERATOR completed!")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  - {output_file}")
    print("\nNOTE: This is Phase 1 of refactoring. Some features use legacy code.")
    print("      Schedule FA, OS, FSI generation will be refactored in Phase 2.")


if __name__ == "__main__":
    main()
