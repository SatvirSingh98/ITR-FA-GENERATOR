"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

TrancheProcessor - Table A3 Row Generation
Processes holdings and sales into separate Table A3 rows
"""

import pandas as pd


class TrancheProcessor:
    """
    Processes equity holdings and sales into Table A3 rows.

    Responsibilities:
    - Split partial sales into separate rows (holding vs sold portions)
    - Generate Table A3 rows with proper ITR field structure
    - Handle unvested RSUs (optional conservative disclosure)
    - Clean text for ITR filing compliance
    """

    def __init__(self, peak_calculator, dividend_allocator):
        """
        Initialize TrancheProcessor.

        Args:
            peak_calculator: PeakCalculator instance
            dividend_allocator: DividendAllocator instance
        """
        self.peak_calculator = peak_calculator
        self.dividend_allocator = dividend_allocator

    def process_holdings(self, df_open, company_details_cache):
        """
        Process open holdings (ByStatus) into Table A3 tranches.

        Args:
            df_open (DataFrame): Open holdings from E*TRADE ByStatus
            company_details_cache (dict): {symbol: {name, address, zip, country_code, matrix}}

        Returns:
            list: Tranche dicts for dividend allocation
        """
        tranches = []

        if df_open.empty:
            return tranches

        for _, row in df_open.iterrows():
            symbol = row['Symbol']
            qty = int(row['Sellable Qty.'])  # E*TRADE ByStatus uses 'Sellable Qty.'
            acq_date = pd.to_datetime(row['Date Acquired']).strftime('%Y-%m-%d')
            plan_type = str(row.get('Plan Type', ''))

            # Determine nature
            is_espp = 'ESPP' in plan_type
            nature = f"ESPP ({qty} shares)" if is_espp else f"RSU ({qty} shares)"

            # Get unit cost (Section 49(2AA) for ESPP)
            if is_espp and 'Purchase Date FMV' in row and pd.notna(row['Purchase Date FMV']):
                # E*TRADE stores FMV as "$147.95" - need to clean
                fmv_str = str(row['Purchase Date FMV']).replace('$', '').replace(',', '')
                unit_cost_usd = float(fmv_str)
            else:
                # Use cost basis per share
                unit_cost_usd = float(row['Est. Cost Basis (per share):'])

            tranches.append({
                'symbol': symbol,
                'qty': qty,
                'total_qty': qty,
                'acq_date': acq_date,
                'unit_cost_usd': unit_cost_usd,
                'nature': nature,
                'sold_details': [],  # No sales yet (these are open holdings)
                'unvested': False
            })

        return tranches

    def process_sales(self, df_sold, company_details_cache):
        """
        Process sales (G&L) into Table A3 tranches.

        For partial sales, creates TWO rows:
        - Row 1: Holding portion (closing_value > 0)
        - Row 2: Sold portion (closing_value = 0, sale_proceeds > 0)

        Args:
            df_sold (DataFrame): Sales from E*TRADE G&L
            company_details_cache (dict): Company data

        Returns:
            list: Tranche dicts for dividend allocation
        """
        tranches = []

        if df_sold.empty:
            return tranches

        for _, row in df_sold.iterrows():
            symbol = row['Symbol']
            qty_sold = int(row['Quantity'])
            acq_date = pd.to_datetime(row['Date Acquired']).strftime('%Y-%m-%d')
            sell_date = pd.to_datetime(row['Date Sold']).strftime('%Y-%m-%d')
            plan_type = str(row.get('Plan Type', ''))

            is_espp = 'ESPP' in plan_type
            nature = f"ESPP ({qty_sold} shares)" if is_espp else f"RSU ({qty_sold} shares)"

            # Get unit cost
            if is_espp and 'Purchase Date Fair Mkt. Value' in row and pd.notna(row['Purchase Date Fair Mkt. Value']):
                unit_cost_usd = float(row['Purchase Date Fair Mkt. Value'])
            else:
                unit_cost_usd = float(row['Adjusted Cost Basis Per Share'])

            tranches.append({
                'symbol': symbol,
                'qty': qty_sold,
                'total_qty': qty_sold,
                'acq_date': acq_date,
                'unit_cost_usd': unit_cost_usd,
                'nature': nature,
                'sold_details': [{
                    'sell_date': sell_date,
                    'qty_sold': qty_sold
                }],
                'unvested': False
            })

        return tranches

    def generate_table_a3_rows(self, tranches, company_details_cache, dividend_allocations):
        """
        Generate Table A3 rows from tranches with ITR-compliant structure.

        Args:
            tranches (list): Processed tranches
            company_details_cache (dict): Company data
            dividend_allocations (dict): {tranche_index: dividend_inr}

        Returns:
            list: Table A3 row dicts
        """
        rows = []

        for idx, tranche in enumerate(tranches):
            symbol = tranche['symbol']

            if symbol not in company_details_cache:
                print(f"[!] WARNING: Company {symbol} not in cache, skipping")
                continue

            company_info = company_details_cache[symbol]
            df_matrix = company_info['matrix']

            # Check if sold during year
            is_sold = len(tranche['sold_details']) > 0
            sell_date = tranche['sold_details'][0]['sell_date'] if is_sold else None

            # Calculate valuations
            valuations = self.peak_calculator.calculate_tranche_values(
                df_matrix=df_matrix,
                qty=tranche['qty'],
                acq_date=tranche['acq_date'],
                unit_cost_usd=tranche['unit_cost_usd'],
                sell_date=sell_date
            )

            # Get dividend for this tranche
            dividend_inr = dividend_allocations.get(idx, 0)

            # Calculate sale proceeds if sold
            if is_sold:
                sale_data = self.peak_calculator.calculate_sale_proceeds(
                    df_matrix=df_matrix,
                    qty=tranche['qty'],
                    sell_date=sell_date
                )
                sale_proceeds = sale_data['sale_proceeds_inr']
            else:
                sale_proceeds = 0

            # Build ITR-compliant row
            row = {
                'CountryName': company_info['country_name'],
                'CountryCodeExcludingIndia': company_info['country_code'],
                'NameOfEntity': self._clean_text_for_itr(company_info['name']),
                'AddressOfEntity': self._clean_text_for_itr(company_info['address']),
                'ZipCode': str(company_info['zip']),
                'NatureOfEntity': tranche['nature'],
                'InterestAcquiringDate': tranche['acq_date'],
                'InitialValOfInvstmnt': valuations['initial_value'],
                'PeakBalanceDuringPeriod': valuations['peak_value'],
                'ClosingBalance': valuations['closing_value'],
                'TotGrossAmtPaidCredited': round(dividend_inr),
                'TotGrossProceeds': sale_proceeds
            }

            rows.append(row)

        return rows

    def _clean_text_for_itr(self, text):
        """
        Clean text for ITR filing compliance.
        Removes special characters that may cause validation errors.

        Args:
            text (str): Raw text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove common problematic characters
        text = text.replace(',', ' ')
        text = text.replace('.', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('  ', ' ')  # Multiple spaces

        # Limit length (ITR has field limits)
        if len(text) > 100:
            text = text[:100]

        return text.strip()
