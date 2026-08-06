"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

DividendAllocator - Per-Lot Dividend Distribution
Allocates dividend income proportionally across equity tranches
"""

import pandas as pd


class DividendAllocator:
    """
    Allocates dividend income to specific holding tranches.

    Responsibilities:
    - Determine which lots were held on dividend payment date
    - Calculate shares held per lot (accounting for partial sales)
    - Allocate dividend proportionally across lots
    - Track total dividend per lot for Schedule FA reporting
    """

    def __init__(self):
        """Initialize DividendAllocator."""
        pass

    def allocate_dividends(self, tranches, df_dividends):
        """
        Allocate dividends to tranches based on holdings on dividend date.

        Args:
            tranches (list): List of tranche dicts with keys:
                - symbol (str)
                - acq_date (str)
                - total_qty (int)
                - sold_details (list): [{sell_date, qty_sold}, ...]
            df_dividends (DataFrame): Dividend data with columns:
                - Symbol
                - Date (YYYY-MM-DD)
                - Amount_INR

        Returns:
            dict: {tranche_index: total_dividend_inr}
        """
        if df_dividends.empty:
            return {}

        dividend_allocations = {}

        # Process each dividend payment
        for _, div_row in df_dividends.iterrows():
            div_symbol = div_row['Symbol']
            div_date = div_row['Date']
            div_amount_inr = div_row['Amount_INR']

            # Find all tranches of this symbol held on dividend date
            lots_held = []

            for idx, tranche in enumerate(tranches):
                if tranche['symbol'] != div_symbol:
                    continue

                # Check if lot was acquired before dividend date
                if tranche['acq_date'] > div_date:
                    continue

                # Calculate shares held on dividend date
                shares_on_div_date = self._calculate_shares_on_date(
                    tranche, div_date
                )

                if shares_on_div_date > 0:
                    lots_held.append({
                        'index': idx,
                        'shares': shares_on_div_date
                    })

            # Calculate total shares held on dividend date
            total_shares = sum(lot['shares'] for lot in lots_held)

            if total_shares == 0:
                print(f"[!] WARNING: No shares held on {div_date} for {div_symbol} dividend")
                continue

            # Allocate dividend proportionally
            for lot in lots_held:
                idx = lot['index']
                shares = lot['shares']

                # Calculate this lot's share of dividend
                lot_dividend = round((shares / total_shares) * div_amount_inr, 2)

                # Add to running total for this tranche
                if idx not in dividend_allocations:
                    dividend_allocations[idx] = 0
                dividend_allocations[idx] += lot_dividend

        return dividend_allocations

    def _calculate_shares_on_date(self, tranche, target_date):
        """
        Calculate shares held by a tranche on a specific date.

        Args:
            tranche (dict): Tranche with total_qty and sold_details
            target_date (str): Target date (YYYY-MM-DD)

        Returns:
            int: Shares held on target date
        """
        shares = tranche['total_qty']

        # Subtract shares sold before or on target date
        for sale in tranche.get('sold_details', []):
            if sale['sell_date'] <= target_date:
                shares -= sale['qty_sold']

        return max(0, shares)  # Can't be negative

    def format_dividend_summary(self, dividend_allocations, tranches):
        """
        Create a summary of dividend allocations for reporting.

        Args:
            dividend_allocations (dict): {tranche_index: total_dividend}
            tranches (list): List of tranches

        Returns:
            list: [{
                'tranche_index': int,
                'symbol': str,
                'acq_date': str,
                'qty': int,
                'dividend_inr': float
            }]
        """
        summary = []

        for idx, dividend_inr in dividend_allocations.items():
            tranche = tranches[idx]
            summary.append({
                'tranche_index': idx,
                'symbol': tranche['symbol'],
                'acq_date': tranche['acq_date'],
                'qty': tranche['total_qty'],
                'dividend_inr': dividend_inr
            })

        # Sort by symbol, then acquisition date
        summary.sort(key=lambda x: (x['symbol'], x['acq_date']))

        return summary
