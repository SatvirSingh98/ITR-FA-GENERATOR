"""
Forex Manager
Handles SBI TTBR exchange rate fetching and Rule 115(1)(f) logic
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ForexManager:
    """Manages forex rates and exchange rate calculations"""

    def __init__(self, calendar_year=2025):
        self.calendar_year = calendar_year
        self.forex_data = None
        self.forex_csv_path = "data/SBI_FOREX_CARD_RATES_USD.csv"

    def load_forex_data(self):
        """Load SBI TTBR forex data from CSV"""
        if not os.path.exists(self.forex_csv_path):
            raise FileNotFoundError(
                f"[ERROR] SBI Forex data not found at {self.forex_csv_path}"
            )

        print(f"[*] Reading local SBI forex data from {self.forex_csv_path}...")
        self.forex_data = pd.read_csv(self.forex_csv_path, parse_dates=['Date'])
        print(f"[OK] Loaded {len(self.forex_data)} records from local CSV")

        # Filter for target year
        year_data = self.forex_data[
            self.forex_data['Date'].dt.year == self.calendar_year
        ]
        print(f"[OK] Downloaded {len(year_data)} SBI TTBR records for {self.calendar_year}")

        if len(year_data) > 0:
            min_rate = year_data['TTBR'].min()
            max_rate = year_data['TTBR'].max()
            print(f"[OK] TTBR range: {min_rate:.2f} to {max_rate:.2f}")

        return self.forex_data

    def get_ttbr(self, date, purpose="general"):
        """
        Get TTBR for a specific date

        Args:
            date: datetime object or date string
            purpose: 'general', 'rule_115_1_f' (for capital gains)

        Returns:
            float: TTBR rate
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)

        # For Rule 115(1)(f): use last day of month BEFORE the given month
        if purpose == 'rule_115_1_f':
            date = self._get_rule_115_1_f_date(date)

        # Find closest available date
        forex_row = self.forex_data[self.forex_data['Date'] == date]

        if forex_row.empty:
            # Try nearby dates (weekends, holidays)
            for offset in range(1, 8):
                prev_date = date - timedelta(days=offset)
                forex_row = self.forex_data[self.forex_data['Date'] == prev_date]
                if not forex_row.empty:
                    print(f"[i] Using {prev_date.date()} TTBR for {date.date()} (closest available)")
                    break

        if forex_row.empty:
            raise ValueError(
                f"[ERROR] TTBR not found for {date.date()} or nearby dates. "
                f"Add this date to {self.forex_csv_path}"
            )

        return float(forex_row.iloc[0]['TTBR'])

    def _get_rule_115_1_f_date(self, sale_date):
        """
        Get Rule 115(1)(f) specified date: Last day of month BEFORE sale month

        Args:
            sale_date: datetime object

        Returns:
            datetime: Last day of previous month
        """
        # Go to first day of sale month, then back one day
        first_of_month = sale_date.replace(day=1)
        last_of_prev_month = first_of_month - timedelta(days=1)
        return last_of_prev_month

    def get_rule_115_1_f_ttbr(self, sale_date):
        """
        Get TTBR per Rule 115(1)(f) for capital gains calculation

        Args:
            sale_date: Sale date (datetime or string)

        Returns:
            tuple: (specified_date, ttbr)
        """
        if isinstance(sale_date, str):
            sale_date = pd.to_datetime(sale_date)

        specified_date = self._get_rule_115_1_f_date(sale_date)
        ttbr = self.get_ttbr(specified_date, purpose='general')

        return specified_date, ttbr

    def get_rule_115_1_e_ttbr(self, dividend_date):
        """
        Get TTBR per Rule 115(1)(e) for dividend income (Schedule OS)
        Last day of month BEFORE dividend payment month

        Args:
            dividend_date: Dividend payment date

        Returns:
            tuple: (specified_date, ttbr)
        """
        if isinstance(dividend_date, str):
            dividend_date = pd.to_datetime(dividend_date)

        specified_date = self._get_rule_115_1_f_date(dividend_date)  # Same logic
        ttbr = self.get_ttbr(specified_date, purpose='general')

        return specified_date, ttbr
