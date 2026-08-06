"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

ScheduleFAGenerator
Handles Table A2 (Custodial Account) and Table A3 (Equity Interest) generation

PHASE 2B: Full implementation with modular peak calculations and dividend allocation.
"""

import pandas as pd
import PyPDF2
import re
import os
import glob

from scripts.etrade.matrix_builder import MatrixBuilder
from scripts.etrade.peak_calculator import PeakCalculator
from scripts.etrade.dividend_allocator import DividendAllocator
from scripts.etrade.tranche_processor import TrancheProcessor


class ScheduleFAGenerator:
    """Generate Schedule FA Tables A2 and A3"""

    def __init__(self, forex_manager, config_manager, calendar_year=2025):
        """
        Args:
            forex_manager (ForexManager): For TTBR exchange rates
            config_manager (ConfigManager): For account configuration
            calendar_year (int): Calendar year for processing
        """
        self.forex_manager = forex_manager
        self.config_manager = config_manager
        self.calendar_year = calendar_year

        # Schedule FA uses CALENDAR YEAR (Jan 1 - Dec 31)
        self.start_date = f"{calendar_year}-01-01"
        self.end_date = f"{calendar_year}-12-31"

        # Dynamic Tax Schema Years
        self.indian_fy = f"{calendar_year}-{str(calendar_year + 1)[-2:]}"
        self.assessment_year = f"{calendar_year + 1}-{str(calendar_year + 2)[-2:]}"

        self.extracted_account_number = None

        # Initialize Phase 2B modular components
        self.matrix_builder = MatrixBuilder(forex_manager)
        self.peak_calculator = PeakCalculator(self.matrix_builder, calendar_year)
        self.dividend_allocator = DividendAllocator()
        self.tranche_processor = TrancheProcessor(self.peak_calculator, self.dividend_allocator)

    @staticmethod
    def clean_text_for_itr(text):
        """Remove commas (ITR portal doesn't accept commas). Keep periods and asterisks."""
        if not text or not isinstance(text, str):
            return text
        # Remove only commas - periods and asterisks are allowed
        text = text.replace(',', '')
        # Remove other problematic characters if needed
        return text.strip()

    def read_client_statement(self, client_statement_path=None):
        """
        Reads closing balance and account number from E*TRADE ClientStatement PDF.

        Args:
            client_statement_path (str): Path to ClientStatements_*.pdf

        Returns:
            tuple: (account_number, ending_value_usd) or (None, None) if not found
        """
        # Auto-find ClientStatements_*.pdf in inputs folder
        if client_statement_path is None:
            pattern = "etrade_inputs/ClientStatements_*.pdf"
            matching_files = glob.glob(pattern)

            if matching_files:
                client_statement_path = matching_files[0]  # Use first match
                print(f"[*] Found ClientStatement: {client_statement_path}")
            else:
                print(f"[i] No ClientStatement PDF found (etrade_inputs/ClientStatements_*.pdf)")
                print(f"[i] Will use calculated closing balance from holdings")
                return None, None

        if not os.path.exists(client_statement_path):
            print(f"[i] ClientStatement not found: {client_statement_path}")
            print(f"[i] Will use calculated closing balance from holdings")
            return None, None

        try:
            print(f"[*] Reading ClientStatement: {client_statement_path}")

            with open(client_statement_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Read first page
                page = pdf_reader.pages[0]
                text = page.extract_text()

                # Extract account number (E*TRADE format: "146 - 239025 - 205 - 4 - 1" at top of statement)
                # The main account number is the first 9 digits (146239025)
                account_match = re.search(r'(\d{3})\s*-\s*(\d{6})\s*-\s*\d{3}\s*-\s*\d\s*-\s*\d', text)
                if account_match:
                    account_number = account_match.group(1) + account_match.group(2)  # Combine first two parts
                    print(f"[OK] Found Account Number: {account_number}")
                    self.extracted_account_number = account_number
                else:
                    self.extracted_account_number = None
                    print(f"[!] Could not extract account number from ClientStatement")
                    account_number = None

                # Extract "Ending Total Value (as of MM/DD/YY) $XX,XXX.XX"
                match = re.search(r'Ending Total Value.*?\$([0-9,]+\.[0-9]{2})', text)

                if match:
                    ending_value_str = match.group(1).replace(',', '')
                    ending_value_usd = float(ending_value_str)

                    print(f"[OK] Found Ending Total Value: ${ending_value_usd:,.2f}")
                    return account_number, ending_value_usd
                else:
                    print(f"[!] Could not find Ending Total Value in ClientStatement")
                    return account_number, None

        except ImportError:
            print(f"[!] PyPDF2 not installed. Run: pip install PyPDF2")
            print(f"[i] Will use calculated closing balance from holdings")
            return None, None
        except Exception as e:
            print(f"[!] Error reading ClientStatement: {e}")
            print(f"[i] Will use calculated closing balance from holdings")
            return None, None

    def generate_table_a2(self, df_dividends, df_sold_calendar, client_statement_closing_usd=None):
        """
        Generate Table A2 (Custodial Account Summary).

        NOTE: This is a SIMPLIFIED Phase 2A implementation.
              Full peak calculation will be added in Phase 2B.

        Args:
            df_dividends (DataFrame): Dividend data
            df_sold_calendar (DataFrame): Sales in calendar year
            client_statement_closing_usd (float): Ending balance from ClientStatement PDF

        Returns:
            DataFrame: Table A2 data
        """
        print("\n[*] Generating Table A2 (Custodial Account)...")

        config = self.config_manager.config
        acc_config = config.get("custodial_account", {})

        # Use extracted account number from ClientStatement if available, then config
        if self.extracted_account_number:
            final_account_no = self.extracted_account_number
            print(f"[i] Using account number from ClientStatement: {final_account_no}")
        elif acc_config.get("account_number"):
            final_account_no = acc_config.get("account_number")
            print(f"[i] Using account number from config.json: {final_account_no}")
        else:
            final_account_no = ""
            print(f"[!] Account number not found - Table A2 account number will be empty")

        # Calculate total dividends (all symbols combined)
        total_dividends_inr = int(df_dividends['Amount (INR)'].sum()) if not df_dividends.empty else 0

        # Calculate total sale proceeds (all symbols combined)
        total_sale_proceeds_inr = 0
        if not df_sold_calendar.empty and 'Total Proceeds' in df_sold_calendar.columns:
            # Convert sale proceeds to INR using exact sale date TTBR
            for _, row in df_sold_calendar.iterrows():
                sale_date = pd.to_datetime(row['Date Sold']).strftime('%Y-%m-%d')
                proceeds_usd = float(row['Total Proceeds'])

                # Get TTBR for sale date
                ttbr = self.forex_manager.get_ttbr(sale_date)
                total_sale_proceeds_inr += int(proceeds_usd * ttbr)

        # TODO Phase 2B: Calculate actual peak from daily matrix
        # For now, use closing as approximation
        total_peak_account_inr = 0

        # Get closing balance from ClientStatement or set to 0
        if client_statement_closing_usd:
            # Get TTBR for Dec 31
            closing_ttbr = self.forex_manager.get_ttbr(self.end_date)
            total_closing_account_inr = int(client_statement_closing_usd * closing_ttbr)
            # Use closing as peak approximation (will be fixed in Phase 2B)
            total_peak_account_inr = total_closing_account_inr
            print(f"[OK] Using ClientStatement closing: ${client_statement_closing_usd:.2f} x {closing_ttbr:.2f} = Rs.{total_closing_account_inr:,}")
        else:
            total_closing_account_inr = 0
            print(f"[!] ClientStatement PDF not found - Table A2 closing balance will be 0")

        # Build Table A2 - Create separate rows for dividends and sale proceeds if both exist
        # Per ITRFA.in guidance: "If both dividend AND sales, create TWO A2 rows"
        custodial_accounts = []

        # Base account info (same for all rows)
        base_account_info = {
            "CountryName": acc_config.get("country_name", "UNITED STATES OF AMERICA"),
            "CountryCodeExcludingIndia": int(acc_config.get("country_code", 2)),
            "FinancialInstName": self.clean_text_for_itr(acc_config.get("financial_institution_name", "E*TRADE Securities LLC")),
            "FinancialInstAddress": self.clean_text_for_itr(acc_config.get("financial_institution_address", "1271 Avenue of the Americas New York NY 10020 United States")),
            "ZipCode": str(acc_config.get("zip_code", "10020")),
            "AccountNumber": str(final_account_no),
            "Status": acc_config.get("status", "BENEFICIAL_OWNER"),
            "AccOpenDate": acc_config.get("account_opening_date", ""),
            "PeakBalanceDuringPeriod": total_peak_account_inr,
            "ClosingBalance": total_closing_account_inr
        }

        # Case 1: Both dividends AND sales exist → Create TWO rows
        if total_dividends_inr > 0 and total_sale_proceeds_inr > 0:
            # Row 1: Dividend
            custodial_accounts.append({
                **base_account_info,
                "GrossAmtPaidCredited": total_dividends_inr,
                "NatureOfAmount": "D"  # D = Dividend
            })
            # Row 2: Sale proceeds
            custodial_accounts.append({
                **base_account_info,
                "GrossAmtPaidCredited": total_sale_proceeds_inr,
                "NatureOfAmount": "P"  # P = Proceeds from Sale or Redemption of Financial Assets
            })
            print(f"[i] Table A2: Creating TWO rows (Dividend: Rs.{total_dividends_inr:,}, Sale Proceeds: Rs.{total_sale_proceeds_inr:,})")

        # Case 2: Only dividends (no sales) → Create ONE row
        elif total_dividends_inr > 0:
            custodial_accounts.append({
                **base_account_info,
                "GrossAmtPaidCredited": total_dividends_inr,
                "NatureOfAmount": "D"  # D = Dividend
            })
            print(f"[i] Table A2: Creating ONE row (Dividend only: Rs.{total_dividends_inr:,})")

        # Case 3: Only sales (no dividends) → Create ONE row
        elif total_sale_proceeds_inr > 0:
            custodial_accounts.append({
                **base_account_info,
                "GrossAmtPaidCredited": total_sale_proceeds_inr,
                "NatureOfAmount": "P"  # P = Proceeds from Sale
            })
            print(f"[i] Table A2: Creating ONE row (Sale Proceeds only: Rs.{total_sale_proceeds_inr:,})")

        # Case 4: No dividends AND no sales → Create ONE row with N (No Amount)
        else:
            custodial_accounts.append({
                **base_account_info,
                "GrossAmtPaidCredited": 0,
                "NatureOfAmount": "N"  # N = No Amount
            })
            print(f"[i] Table A2: Creating ONE row (No dividends or sales)")

        df_a2 = pd.DataFrame(custodial_accounts)
        print(f"[OK] Table A2 generated with {len(df_a2)} row(s)")

        return df_a2

    def generate_table_a3(self, df_open, df_sold_calendar, company_details_cache, df_dividends=None):
        """
        Generate Table A3 (Equity Interest Holdings).

        PHASE 2B: Full implementation with peak calculations and dividend allocation.

        Args:
            df_open (DataFrame): Open holdings from ByStatus
            df_sold_calendar (DataFrame): Sales in calendar year from G&L
            company_details_cache (dict): {symbol: {name, address, zip, country_name, country_code, matrix}}
            df_dividends (DataFrame, optional): Dividend data for allocation

        Returns:
            DataFrame: Table A3 data
        """
        print("\n[*] Generating Table A3 (Equity Interest)...")
        print("[*] Using PHASE 2B full implementation with peak calculations")

        if df_open.empty and (df_sold_calendar is None or df_sold_calendar.empty):
            print("[!] No holdings or sales data - Table A3 will be empty")
            return pd.DataFrame()

        # Step 1: Process open holdings into tranches
        print(f"[*] Processing {len(df_open)} open holdings...")
        tranches_open = self.tranche_processor.process_holdings(df_open, company_details_cache)

        # Step 2: Process sales into tranches
        tranches_sold = []
        if df_sold_calendar is not None and not df_sold_calendar.empty:
            print(f"[*] Processing {len(df_sold_calendar)} sales...")
            tranches_sold = self.tranche_processor.process_sales(df_sold_calendar, company_details_cache)

        # Combine all tranches
        all_tranches = tranches_open + tranches_sold
        print(f"[*] Total tranches to process: {len(all_tranches)}")

        # Step 3: Allocate dividends to tranches
        dividend_allocations = {}
        if df_dividends is not None and not df_dividends.empty:
            print(f"[*] Allocating {len(df_dividends)} dividend payments to tranches...")
            dividend_allocations = self.dividend_allocator.allocate_dividends(all_tranches, df_dividends)
            print(f"[OK] Dividends allocated to {len(dividend_allocations)} tranches")

        # Step 4: Generate Table A3 rows with peak calculations
        print("[*] Calculating peak values and generating Table A3 rows...")
        table_a3_rows = self.tranche_processor.generate_table_a3_rows(
            all_tranches,
            company_details_cache,
            dividend_allocations
        )

        df_a3 = pd.DataFrame(table_a3_rows)

        if not df_a3.empty:
            # Sort by acquisition date
            df_a3 = df_a3.sort_values('InterestAcquiringDate')
            print(f"[OK] Table A3 generated with {len(df_a3)} row(s)")
        else:
            print("[!] Table A3 is empty (no valid tranches)")

        return df_a3
