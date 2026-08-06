"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

MatrixBuilder - Stock Price × TTBR Matrix Construction
Builds daily valuation matrices for equity holdings
"""

import pandas as pd
from datetime import datetime


class MatrixBuilder:
    """
    Builds stock price × TTBR matrices for valuation calculations.

    Responsibilities:
    - Merge stock prices with TTBR exchange rates
    - Calculate per-share INR valuations
    - Handle weekend/holiday date lookups
    - Filter by date ranges
    """

    def __init__(self, forex_manager):
        """
        Initialize MatrixBuilder.

        Args:
            forex_manager: ForexManager instance with TTBR data
        """
        self.forex_manager = forex_manager

    def build_matrix(self, df_prices, symbol):
        """
        Build price × TTBR matrix from stock prices.

        Args:
            df_prices (DataFrame): Stock prices with columns [Date, Stock_Close_USD]
            symbol (str): Stock symbol (for logging)

        Returns:
            DataFrame: Matrix with columns [Date, Stock_Close_USD, TTBR, Valuation_Per_Share_INR]
        """
        if df_prices.empty:
            return pd.DataFrame(columns=['Date', 'Stock_Close_USD', 'TTBR', 'Valuation_Per_Share_INR'])

        # Ensure Date is datetime
        if not pd.api.types.is_datetime64_any_dtype(df_prices['Date']):
            df_prices = df_prices.copy()
            df_prices['Date'] = pd.to_datetime(df_prices['Date'])

        # Merge with TTBR rates
        df_matrix = pd.merge(
            df_prices,
            self.forex_manager.forex_data[['Date', 'TTBR']],
            on='Date',
            how='left'
        )

        # Calculate per-share valuation in INR
        df_matrix['Valuation_Per_Share_INR'] = df_matrix['Stock_Close_USD'] * df_matrix['TTBR']

        return df_matrix

    def get_price_on_date(self, df_matrix, target_date):
        """
        Get stock price and TTBR for a specific date.
        Uses backward search for weekends/holidays.

        Args:
            df_matrix (DataFrame): Price matrix
            target_date (str or datetime): Target date

        Returns:
            dict: {'date': date, 'price_usd': float, 'ttbr': float, 'valuation_inr': float}
                  or None if not found
        """
        if df_matrix.empty:
            return None

        # Ensure target_date is datetime
        if isinstance(target_date, str):
            target_date = pd.to_datetime(target_date)

        # Try exact match first
        exact_row = df_matrix[df_matrix['Date'] == target_date]
        if not exact_row.empty:
            row = exact_row.iloc[0]
            return {
                'date': row['Date'],
                'price_usd': row['Stock_Close_USD'],
                'ttbr': row['TTBR'],
                'valuation_inr': row['Valuation_Per_Share_INR']
            }

        # Backward search for previous trading day
        prior_dates = df_matrix[df_matrix['Date'] < target_date].sort_values('Date', ascending=False)
        if not prior_dates.empty:
            row = prior_dates.iloc[0]
            return {
                'date': row['Date'],
                'price_usd': row['Stock_Close_USD'],
                'ttbr': row['TTBR'],
                'valuation_inr': row['Valuation_Per_Share_INR']
            }

        return None

    def get_ttbr_on_date(self, target_date):
        """
        Get TTBR for a specific date (with backward search).

        Args:
            target_date (str or datetime): Target date

        Returns:
            float: TTBR rate, or None if not found
        """
        if isinstance(target_date, str):
            target_date = pd.to_datetime(target_date)

        # Try exact match
        forex_row = self.forex_manager.forex_data[
            self.forex_manager.forex_data['Date'] == target_date
        ]
        if not forex_row.empty:
            return forex_row['TTBR'].values[0]

        # Backward search
        prior_dates = self.forex_manager.forex_data[
            self.forex_manager.forex_data['Date'] < target_date
        ].sort_values('Date', ascending=False)

        if not prior_dates.empty:
            return prior_dates['TTBR'].values[0]

        return None

    def filter_by_date_range(self, df_matrix, start_date, end_date):
        """
        Filter matrix to a specific date range.

        Args:
            df_matrix (DataFrame): Price matrix
            start_date (str or datetime): Start date (inclusive)
            end_date (str or datetime): End date (inclusive)

        Returns:
            DataFrame: Filtered matrix
        """
        if df_matrix.empty:
            return df_matrix

        # Ensure dates are datetime
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)

        return df_matrix[
            (df_matrix['Date'] >= start_date) &
            (df_matrix['Date'] <= end_date)
        ].copy()
