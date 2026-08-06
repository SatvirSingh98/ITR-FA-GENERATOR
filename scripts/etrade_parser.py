"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

ETradeParser
Handles parsing of E*TRADE export files
"""

import os
import pandas as pd
import re


class ETradeParser:
    """Parse E*TRADE export files (ByStatus, G&L, Transaction History, Client Statement)"""

    def __init__(self, calendar_year=2025):
        self.calendar_year = calendar_year
        self.start_date = f"{calendar_year}-01-01"
        self.end_date = f"{calendar_year}-12-31"

    def discover_input_files(self):
        """
        Discover E*TRADE input files in inputs folder or root

        Returns:
            dict: Paths to discovered files
        """
        files = {
            'bystatus': None,
            'gl': None,
            'transaction_history': None,
            'client_statement': None
        }

        # Check for ByStatus
        if os.path.exists("etrade_inputs/ByStatus_expanded.xlsx"):
            files['bystatus'] = "etrade_inputs/ByStatus_expanded.xlsx"
        elif os.path.exists("ByStatus_expanded.xlsx"):
            files['bystatus'] = "ByStatus_expanded.xlsx"

        # Check for G&L
        if os.path.exists("etrade_inputs/G&L_Expanded.xlsx"):
            files['gl'] = "etrade_inputs/G&L_Expanded.xlsx"
        elif os.path.exists("G&L_Expanded.xlsx"):
            files['gl'] = "G&L_Expanded.xlsx"

        # Check for Transaction History
        if os.path.exists("etrade_inputs/Transaction_History.csv"):
            files['transaction_history'] = "etrade_inputs/Transaction_History.csv"
        elif os.path.exists("Transaction_History.csv"):
            files['transaction_history'] = "Transaction_History.csv"

        # Check for Client Statement
        if os.path.exists("etrade_inputs/ClientStatement.pdf"):
            files['client_statement'] = "etrade_inputs/ClientStatement.pdf"
        elif os.path.exists("ClientStatement.pdf"):
            files['client_statement'] = "ClientStatement.pdf"

        return files

    def parse_bystatus(self, file_path):
        """
        Parse ByStatus_expanded.xlsx file

        Args:
            file_path (str): Path to ByStatus file

        Returns:
            DataFrame: Sellable holdings
        """
        if not file_path or not os.path.exists(file_path):
            print("[!] WARNING: ByStatus_expanded.xlsx not found")
            return pd.DataFrame()

        try:
            print(f"[*] Reading {file_path}...")
            df_bystatus = pd.read_excel(file_path, sheet_name='Sellable')
            df_open = df_bystatus[df_bystatus['Record Type'].isin(['Purchase', 'Grant'])].copy()
            print(f"[OK] Loaded {len(df_open)} open positions from ByStatus")
            return df_open
        except Exception as e:
            print(f"[!] ERROR reading ByStatus: {e}")
            return pd.DataFrame()

    def parse_gains_losses(self, file_path, calendar_year=None):
        """
        Parse G&L_Expanded.xlsx file

        Args:
            file_path (str): Path to G&L file
            calendar_year (int): Calendar year for filtering

        Returns:
            tuple: (df_sold_calendar, df_sold_future, df_sold_extended)
                - df_sold_calendar: Sold within calendar year (Jan-Dec)
                - df_sold_future: Held in calendar year but sold after Dec 31
                - df_sold_extended: Sold in extended period (Jan - Mar next year)
        """
        if not file_path or not os.path.exists(file_path):
            print("[!] G&L_Expanded.xlsx not found (no sales to report)")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        if calendar_year is None:
            calendar_year = self.calendar_year

        start_date = f"{calendar_year}-01-01"
        end_date = f"{calendar_year}-12-31"
        extended_end = f"{calendar_year + 1}-03-31"

        try:
            print(f"[*] Reading {file_path}...")
            df_gl = pd.read_excel(file_path, sheet_name='G&L_Expanded')
            df_sold_all = df_gl[df_gl['Record Type'] == 'Sell'].copy()

            df_sold_all['Date Acquired'] = pd.to_datetime(df_sold_all['Date Acquired'])
            df_sold_all['Date Sold'] = pd.to_datetime(df_sold_all['Date Sold'])

            # Calendar year sales (Jan 1 - Dec 31) for Table A3
            df_sold_calendar = df_sold_all[
                (df_sold_all['Date Acquired'] <= end_date) &
                (df_sold_all['Date Sold'] >= start_date) &
                (df_sold_all['Date Sold'] <= end_date)
            ].copy()

            # Future sales (held in calendar year but sold after Dec 31)
            df_sold_future = df_sold_all[
                (df_sold_all['Date Acquired'] <= end_date) &
                (df_sold_all['Date Sold'] > end_date)
            ].copy()

            # Extended period sales (Jan - Mar next year) for Capital Gains
            df_sold_extended = df_sold_all[
                (df_sold_all['Date Sold'] >= start_date) &
                (df_sold_all['Date Sold'] <= extended_end)
            ].copy()

            print(f"[OK] Found {len(df_sold_calendar)} calendar year sales, "
                  f"{len(df_sold_future)} future sales, "
                  f"{len(df_sold_extended)} extended period sales")

            return df_sold_calendar, df_sold_future, df_sold_extended

        except Exception as e:
            print(f"[!] ERROR reading G&L: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def parse_transaction_history(self, file_path):
        """
        Parse Transaction_History.csv for dividend data

        Args:
            file_path (str): Path to Transaction History CSV

        Returns:
            DataFrame: Dividend transactions with Date, Symbol, Amount (USD), Amount (INR)
        """
        if not file_path or not os.path.exists(file_path):
            print("[*] Transaction_History.csv not found (no dividends to report)")
            return pd.DataFrame()

        try:
            print(f"[*] Reading {file_path}...")
            df_txn = pd.read_csv(file_path)

            # Filter for dividends only
            df_dividends = df_txn[df_txn['Transaction Type'] == 'Dividend'].copy()

            if df_dividends.empty:
                print("[*] No dividends found in Transaction History")
                return pd.DataFrame()

            # Parse date and amounts
            df_dividends['Date'] = pd.to_datetime(df_dividends['Transaction Date'])
            df_dividends['Symbol'] = df_dividends['Symbol']
            df_dividends['Amount (USD)'] = df_dividends['Amount'].astype(float)

            # Calculate INR amount (will be updated with actual TTBR later)
            df_dividends['Amount (INR)'] = 0.0

            print(f"[OK] Found {len(df_dividends)} dividend transactions")
            return df_dividends[['Date', 'Symbol', 'Amount (USD)', 'Amount (INR)']]

        except Exception as e:
            print(f"[!] ERROR reading Transaction History: {e}")
            return pd.DataFrame()

    def parse_client_statement(self, file_path):
        """
        Parse ClientStatement.pdf to extract account number and ending value

        Args:
            file_path (str): Path to ClientStatement PDF

        Returns:
            tuple: (account_number, ending_value_usd)
        """
        if not file_path or not os.path.exists(file_path):
            print("[!] ClientStatement.pdf not found")
            return None, None

        try:
            import PyPDF2
            print(f"[*] Reading {file_path}...")

            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()

                # Extract account number (E*TRADE format: "146 - 239025 - 205 - 4 - 1")
                account_match = re.search(r'(\d{3})\s*-\s*(\d{6})\s*-\s*\d{3}\s*-\s*\d\s*-\s*\d', text)
                account_number = None
                if account_match:
                    account_number = account_match.group(1) + account_match.group(2)
                    print(f"[OK] Found Account Number: {account_number}")
                else:
                    print(f"[!] Could not extract account number from ClientStatement")

                # Extract "Ending Total Value (as of MM/DD/YY) $XX,XXX.XX"
                match = re.search(r'Ending Total Value.*?\$([0-9,]+\.[0-9]{2})', text)
                ending_value_usd = None
                if match:
                    ending_value_str = match.group(1).replace(',', '')
                    ending_value_usd = float(ending_value_str)
                    print(f"[OK] Found Ending Total Value: ${ending_value_usd:,.2f}")
                else:
                    print(f"[!] Could not find Ending Total Value in ClientStatement")

                return account_number, ending_value_usd

        except ImportError:
            print(f"[!] PyPDF2 not installed. Run: pip install PyPDF2")
            return None, None
        except Exception as e:
            print(f"[!] Error reading ClientStatement: {e}")
            return None, None

    def discover_companies(self, df_open, df_sold_extended):
        """
        Discover unique company symbols from ByStatus and G&L data

        Args:
            df_open (DataFrame): Open positions from ByStatus
            df_sold_extended (DataFrame): Extended period sales from G&L

        Returns:
            list: Unique company symbols
        """
        symbols = set()

        if not df_open.empty:
            symbols.update(df_open['Symbol'].unique())

        if not df_sold_extended.empty:
            symbols.update(df_sold_extended['Symbol'].unique())

        symbols = sorted(list(symbols))
        print(f"[OK] Discovered {len(symbols)} unique companies: {', '.join(symbols)}")
        return symbols

    def extract_pre_fy_acquisition_dates(self, df_open, df_sold_extended):
        """
        Extract acquisition dates that are BEFORE the target calendar year
        Used to ensure TTBR data is loaded for these dates

        Args:
            df_open (DataFrame): Open positions
            df_sold_extended (DataFrame): Extended sales

        Returns:
            list: Unique pre-FY acquisition dates (YYYY-MM-DD strings)
        """
        extra_dates = []

        # From open positions
        if not df_open.empty:
            for _, row in df_open.iterrows():
                if row.get('Sellable Qty.', 0) > 0:
                    acq_date_raw = row.get('Date Acquired')
                    if pd.notna(acq_date_raw):
                        acq_date = pd.to_datetime(acq_date_raw)
                        if acq_date.strftime('%Y-%m-%d') < self.start_date:
                            extra_dates.append(acq_date.strftime('%Y-%m-%d'))

        # From sold positions
        if not df_sold_extended.empty:
            for _, row in df_sold_extended.iterrows():
                acq_date_raw = row.get('Date Acquired')
                if pd.notna(acq_date_raw):
                    acq_date = pd.to_datetime(acq_date_raw)
                    if acq_date.strftime('%Y-%m-%d') < self.start_date:
                        extra_dates.append(acq_date.strftime('%Y-%m-%d'))

        unique_dates = sorted(set(extra_dates))
        if unique_dates:
            print(f"[*] Found {len(unique_dates)} pre-FY acquisition dates: {', '.join(unique_dates[:5])}...")
        return unique_dates
