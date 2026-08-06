"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

PeakCalculator - Initial, Peak, and Closing Value Calculations
Computes Schedule FA valuations for equity holdings
"""

import pandas as pd
from datetime import datetime


class PeakCalculator:
    """
    Calculates Initial, Peak, and Closing values for equity holdings.

    Responsibilities:
    - Calculate initial value (cost basis × TTBR on acquisition date)
    - Find peak value during holding period
    - Calculate closing value (market value × TTBR on Dec 31 or sale date)
    - Handle pre-FY acquisition dates
    """

    def __init__(self, matrix_builder, calendar_year):
        """
        Initialize PeakCalculator.

        Args:
            matrix_builder: MatrixBuilder instance
            calendar_year (int): Calendar year for calculations
        """
        self.matrix_builder = matrix_builder
        self.calendar_year = calendar_year
        self.start_date = f"{calendar_year}-01-01"
        self.end_date = f"{calendar_year}-12-31"

    def calculate_tranche_values(self, df_matrix, qty, acq_date, unit_cost_usd, sell_date=None):
        """
        Calculate Initial, Peak, and Closing values for a holding tranche.

        Args:
            df_matrix (DataFrame): Price × TTBR matrix for the symbol
            qty (int): Quantity of shares
            acq_date (str): Acquisition date (YYYY-MM-DD)
            unit_cost_usd (float): Cost basis per share in USD
            sell_date (str, optional): Sale date if sold during year

        Returns:
            dict: {
                'initial_value': int,        # INR, rounded
                'peak_value': int,           # INR, rounded
                'closing_value': int,        # INR, rounded
                'peak_date': str,            # YYYY-MM-DD
                'peak_price_usd': float,
                'peak_ttbr': float
            }
        """
        if df_matrix.empty:
            return {
                'initial_value': 0,
                'peak_value': 0,
                'closing_value': 0,
                'peak_date': None,
                'peak_price_usd': 0.0,
                'peak_ttbr': 0.0
            }

        # Ensure dates are datetime
        acq_date_dt = pd.to_datetime(acq_date)
        if sell_date:
            sell_date_dt = pd.to_datetime(sell_date)
        else:
            sell_date_dt = None

        # 1. Initial Value (Cost basis at acquisition)
        initial_ttbr = self.matrix_builder.get_ttbr_on_date(acq_date)
        if initial_ttbr is None:
            initial_ttbr = 83.50  # Fallback
            print(f"[!] WARNING: TTBR not found for {acq_date}, using fallback {initial_ttbr}")

        initial_value = round(qty * unit_cost_usd * initial_ttbr)

        # 2. Determine holding window
        # Start from max(acquisition date, FY start)
        # End at min(sale date, FY end) if sold, else FY end
        hold_start = max(self.start_date, acq_date)
        if sell_date_dt and sell_date <= self.end_date:
            hold_end = sell_date
        else:
            hold_end = self.end_date

        # Filter matrix to holding window
        window = self.matrix_builder.filter_by_date_range(df_matrix, hold_start, hold_end)
        if window.empty:
            # Use last available data if window is empty
            window = df_matrix.tail(1)

        # 3. Peak Value during holding window
        if not window.empty:
            peak_idx = window['Valuation_Per_Share_INR'].idxmax()
            peak_row = window.loc[peak_idx]

            peak_date = peak_row['Date'].strftime('%Y-%m-%d')
            peak_price_usd = peak_row['Stock_Close_USD']
            peak_ttbr = peak_row['TTBR']
            peak_value_per_share = peak_row['Valuation_Per_Share_INR']
            peak_value = round(qty * peak_value_per_share)
        else:
            peak_date = None
            peak_price_usd = 0.0
            peak_ttbr = 0.0
            peak_value = 0

        # 4. Closing Value
        if sell_date_dt and sell_date <= self.end_date:
            # Sold during year - closing value is 0 (no longer held on Dec 31)
            closing_value = 0
        else:
            # Still holding on Dec 31 - use Dec 31 valuation
            closing_data = self.matrix_builder.get_price_on_date(df_matrix, self.end_date)
            if closing_data:
                closing_value = round(qty * closing_data['valuation_inr'])
            else:
                # Use peak as fallback
                closing_value = peak_value

        return {
            'initial_value': initial_value,
            'peak_value': peak_value,
            'closing_value': closing_value,
            'peak_date': peak_date,
            'peak_price_usd': peak_price_usd,
            'peak_ttbr': peak_ttbr
        }

    def calculate_sale_proceeds(self, df_matrix, qty, sell_date):
        """
        Calculate sale proceeds in INR for a sale transaction.

        Args:
            df_matrix (DataFrame): Price × TTBR matrix for the symbol
            qty (int): Quantity sold
            sell_date (str): Sale date (YYYY-MM-DD)

        Returns:
            dict: {
                'sale_proceeds_inr': int,
                'sale_price_usd': float,
                'sale_ttbr': float
            }
        """
        sale_data = self.matrix_builder.get_price_on_date(df_matrix, sell_date)

        if sale_data:
            sale_proceeds = round(qty * sale_data['valuation_inr'])
            return {
                'sale_proceeds_inr': sale_proceeds,
                'sale_price_usd': sale_data['price_usd'],
                'sale_ttbr': sale_data['ttbr']
            }
        else:
            return {
                'sale_proceeds_inr': 0,
                'sale_price_usd': 0.0,
                'sale_ttbr': 0.0
            }
