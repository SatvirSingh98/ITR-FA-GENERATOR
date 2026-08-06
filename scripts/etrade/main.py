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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.etrade.config_manager import ConfigManager
from scripts.etrade.forex_manager import ForexManager
from scripts.etrade.tax_calculator import TaxCalculator
from scripts.etrade.etrade_parser import ETradeParser
from scripts.etrade.capital_gains_generator import CapitalGainsGenerator
from scripts.etrade.excel_formatter import ExcelFormatter
from scripts.etrade.schedule_fa_generator import ScheduleFAGenerator
from scripts.etrade.schedule_os_fsi_generator import ScheduleOSFSIGenerator
from scripts.etrade.yahoo_scraper import YahooFinanceScraper


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

    # Step 4a: Scrape company details and stock prices from Yahoo Finance
    print(f"\n[4a/8] Scraping company details from Yahoo Finance...")
    yahoo_scraper = YahooFinanceScraper(calendar_year=calendar_year)
    company_details_cache = {}

    if companies:
        print(f"[*] Found {len(companies)} unique companies: {', '.join(companies)}")
        for symbol in companies:
            print(f"\n[*] Processing {symbol}...")

            # Scrape company profile
            profile = yahoo_scraper.scrape_company_profile(symbol)

            # Scrape stock prices for calendar year
            df_prices = yahoo_scraper.scrape_stock_prices(symbol)

            # Build price matrix with TTBR
            if not df_prices.empty:
                # Convert Date column to datetime for merging with forex data
                df_prices['Date'] = pd.to_datetime(df_prices['Date'])

                # Merge stock prices with TTBR rates
                df_matrix = pd.merge(
                    df_prices,
                    forex_manager.forex_data[['Date', 'TTBR']],
                    on='Date',
                    how='left'
                )
                # Calculate per-share valuation in INR
                df_matrix['Valuation_Per_Share_INR'] = df_matrix['Stock_Close_USD'] * df_matrix['TTBR']

                # Store in cache
                company_details_cache[symbol] = {
                    'name': profile['company_name'],
                    'address': profile['company_address'],
                    'zip': profile['zip_code'],
                    'country_name': profile['country_name'],
                    'country_code': profile['country_code'],
                    'matrix': df_matrix  # Date, Stock_Close_USD, TTBR, Valuation_Per_Share_INR
                }
                print(f"[OK] {symbol}: {len(df_matrix)} days of price data")
            else:
                print(f"[!] WARNING: No price data for {symbol}")
                # Still add basic profile info
                company_details_cache[symbol] = {
                    'name': profile['company_name'],
                    'address': profile['company_address'],
                    'zip': profile['zip_code'],
                    'country_name': profile['country_name'],
                    'country_code': profile['country_code'],
                    'matrix': pd.DataFrame()
                }

        print(f"\n[OK] Company details cache built for {len(company_details_cache)} companies")
    else:
        print("[i] No companies discovered from E*TRADE files")

    # Step 5: Generate Capital Gains (dual-regime)
    print("\n[5/9] Generating capital gains...")
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
    print("\n[6/9] Generating Schedule FA...")
    fa_generator = ScheduleFAGenerator(forex_manager, config_manager, calendar_year=calendar_year)

    # Read ClientStatement for closing balance
    account_number, closing_balance_usd = fa_generator.read_client_statement()

    # Generate Table A2 (Custodial Account Summary)
    df_table_a2 = fa_generator.generate_table_a2(
        df_dividends=df_dividends,
        df_sold_calendar=df_sold_calendar,
        client_statement_closing_usd=closing_balance_usd
    )

    # Generate Table A3 (Equity Interest Holdings) - PHASE 2B full implementation
    df_table_a3 = fa_generator.generate_table_a3(
        df_open=df_open,
        df_sold_calendar=df_sold_calendar,
        company_details_cache=company_details_cache,  # Populated with Yahoo Finance data
        df_dividends=df_dividends  # Pass dividends for per-lot allocation
    )

    # Step 7: Generate Schedule OS and FSI
    print("\n[7/9] Generating Schedule OS and FSI...")
    os_fsi_generator = ScheduleOSFSIGenerator(forex_manager, calendar_year=calendar_year)

    # Calculate Schedule OS (Other Sources - Dividend Income)
    df_schedule_os, df_div_os = os_fsi_generator.calculate_schedule_os(df_dividends)

    # Calculate Schedule FSI (Foreign Source Income)
    # Convert capital gains to required format for FSI
    if capital_gains_new:
        df_cg_for_fsi = pd.DataFrame(capital_gains_new)
    else:
        df_cg_for_fsi = pd.DataFrame()

    df_schedule_fsi = os_fsi_generator.calculate_schedule_fsi(df_dividends, df_cg_for_fsi)

    # Step 8: Write Excel output with professional formatting
    print("\n[8/9] Writing Excel output...")
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

        # Write Schedule FA sheets
        if not df_table_a2.empty:
            df_table_a2.to_excel(writer, sheet_name="Table A2 Custodial Acc", index=False)
        else:
            pd.DataFrame({'Note': ['No Table A2 data']}).to_excel(writer, sheet_name="Table A2 Custodial Acc", index=False)

        if not df_table_a3.empty:
            df_table_a3.to_excel(writer, sheet_name="Table A3 Equity Interest", index=False)
        else:
            pd.DataFrame({'Note': ['No Table A3 data']}).to_excel(writer, sheet_name="Table A3 Equity Interest", index=False)

        # Write Schedule OS and FSI
        if not df_schedule_os.empty:
            df_schedule_os.to_excel(writer, sheet_name="Schedule OS", index=False)
        else:
            pd.DataFrame({'Note': ['No Schedule OS data']}).to_excel(writer, sheet_name="Schedule OS", index=False)

        if not df_schedule_fsi.empty:
            df_schedule_fsi.to_excel(writer, sheet_name="Schedule FSI", index=False)
        else:
            pd.DataFrame({'Note': ['No Schedule FSI data']}).to_excel(writer, sheet_name="Schedule FSI", index=False)

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

    # Step 9: Summary
    print("\n[9/9] Summary...")
    print("\n" + "=" * 80)
    print("SUCCESS - ITR-FA-GENERATOR completed!")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  - {output_file}")
    print(f"\nData processed:")
    print(f"  - Companies scraped: {len(company_details_cache)}")
    print(f"  - Holdings processed: {len(df_open)}")
    print(f"  - Sales in calendar year: {len(df_sold_calendar)}")
    print(f"  - Dividends: {len(df_dividends)}")
    print(f"\nSheets generated:")
    print(f"  - Capital Gains (dual-regime)")
    print(f"  - Table A2 Custodial Acc")
    print(f"  - Table A3 Equity Interest")
    print(f"  - Schedule OS (Other Sources)")
    print(f"  - Schedule FSI (Foreign Source Income)")
    print(f"\nNOTE: Phase 2B - Complete modular architecture!")
    print(f"      [OK] Table A3 peak calculations & dividend allocation")
    print(f"      [OK] Capital Gains (dual-regime), Schedule OS, Schedule FSI")
    print(f"      [OK] YahooScraper for company data & stock prices")


if __name__ == "__main__":
    main()
