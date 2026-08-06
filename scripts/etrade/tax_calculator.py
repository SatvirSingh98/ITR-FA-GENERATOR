"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

Tax Calculator
Handles STCG/LTCG tax rate calculations for both New and Old regimes
"""

import math


class TaxCalculator:
    """Calculate tax rates and amounts for capital gains"""

    # LTCG rate is same for both regimes
    LTCG_RATE = 0.125  # 12.5%

    def __init__(self):
        """Initialize tax calculator"""
        self.stcg_rate_new = 0.312  # Default for backward compatibility
        self.stcg_rate_old = 0.312
        self._new_regime_rates = self._build_new_regime_rates()
        self._old_regime_rates = self._build_old_regime_rates()

    def _build_new_regime_rates(self):
        """Build New Tax Regime STCG rate table"""
        return {
            '1': (0.0, "0% (Nil)"),
            '2': (0.052, "5.2% (5% + 4% cess)"),
            '3': (0.104, "10.4% (10% + 4% cess)"),
            '4': (0.156, "15.6% (15% + 4% cess)"),
            '5': (0.208, "20.8% (20% + 4% cess)"),
            '6': (0.260, "26.0% (25% + 4% cess)"),
            '7': (0.312, "31.2% (30% + 4% cess)"),
            '8': (0.3432, "34.32% (30% + 10% surcharge + 4% cess)"),
            '9': (0.3588, "35.88% (30% + 15% surcharge + 4% cess)"),
            '10': (0.390, "39.0% (30% + 25% surcharge + 4% cess)"),
            '11': (0.390, "39.0% (30% + 25% surcharge + 4% cess)"),
        }

    def _build_old_regime_rates(self):
        """Build Old Tax Regime STCG rate table"""
        return {
            '1': (0.0, "0% (Nil)"),
            '2': (0.052, "5.2% (5% + 4% cess)"),
            '3': (0.208, "20.8% (20% + 4% cess)"),
            '4': (0.312, "31.2% (30% + 4% cess)"),
            '5': (0.312, "31.2% (30% + 4% cess)"),
            '6': (0.312, "31.2% (30% + 4% cess)"),
            '7': (0.312, "31.2% (30% + 4% cess)"),
            '8': (0.3432, "34.32% (30% + 10% surcharge + 4% cess)"),
            '9': (0.3588, "35.88% (30% + 15% surcharge + 4% cess)"),
            '10': (0.390, "39.0% (30% + 25% surcharge + 4% cess)"),
            '11': (0.42744, "42.744% (30% + 37% surcharge + 4% cess)"),
        }

    def calculate_stcg_rates_for_income(self, income_bracket):
        """
        Calculate STCG rates for BOTH regimes based on income bracket

        Args:
            income_bracket (str): Income bracket choice (1-11)

        Returns:
            tuple: (new_rate, old_rate, new_display, old_display)
        """
        bracket = str(income_bracket).strip()

        if bracket not in self._new_regime_rates:
            raise ValueError(f"Invalid income bracket: {bracket}. Must be 1-11")

        new_rate, new_display = self._new_regime_rates[bracket]
        old_rate, old_display = self._old_regime_rates[bracket]

        # Store for backward compatibility
        self.stcg_rate_new = new_rate
        self.stcg_rate_old = old_rate

        return new_rate, old_rate, new_display, old_display

    def calculate_tax(self, capital_gain, tax_type, regime='new'):
        """
        Calculate tax amount for capital gain

        Args:
            capital_gain (float): Capital gain amount in INR
            tax_type (str): 'LTCG' or 'STCG'
            regime (str): 'new' or 'old' (for STCG only)

        Returns:
            int: Tax amount (rounded up)
        """
        if tax_type == 'LTCG':
            rate = self.LTCG_RATE
        else:  # STCG
            rate = self.stcg_rate_new if regime == 'new' else self.stcg_rate_old

        return math.ceil(capital_gain * rate)

    def get_ltcg_rate(self):
        """Get LTCG rate (same for both regimes)"""
        return self.LTCG_RATE

    def get_stcg_rate(self, regime='new'):
        """Get STCG rate for specified regime"""
        return self.stcg_rate_new if regime == 'new' else self.stcg_rate_old

    def calculate_advance_tax_installment(self, tax_amount, sale_date):
        """
        Calculate advance tax installments per Rule 234C based on sale date

        Args:
            tax_amount (int): Total tax amount
            sale_date: Sale date (datetime or string)

        Returns:
            dict: Installments for Jul/Sep/Dec/Mar deadlines
        """
        import pandas as pd

        if isinstance(sale_date, str):
            sale_date = pd.to_datetime(sale_date)

        sale_month = sale_date.month

        # Rule 234C: Advance tax schedule based on sale month
        if sale_month <= 6:  # Apr 1 - Jun 30: All 4 deadlines apply
            return {
                'jul': math.ceil(tax_amount * 0.15),
                'sep': math.ceil(tax_amount * 0.45),
                'dec': math.ceil(tax_amount * 0.75),
                'mar': tax_amount
            }
        elif sale_month <= 8:  # Jul 1 - Aug 31: Jul deadline passed
            return {
                'jul': 0,
                'sep': math.ceil(tax_amount * 0.45),
                'dec': math.ceil(tax_amount * 0.75),
                'mar': tax_amount
            }
        elif sale_month <= 11:  # Sep 1 - Nov 30: Jul/Sep deadlines passed
            return {
                'jul': 0,
                'sep': 0,
                'dec': math.ceil(tax_amount * 0.75),
                'mar': tax_amount
            }
        else:  # Dec 1 - Mar 31: Only Mar 15 deadline applies
            return {
                'jul': 0,
                'sep': 0,
                'dec': 0,
                'mar': tax_amount
            }

    def group_sales_by_period(self, sales_data):
        """
        Group sales by advance tax deadline period

        Args:
            sales_data (list): List of sale dicts with 'Sale Date' and tax info

        Returns:
            list: Grouped rows with period summaries
        """
        import pandas as pd

        if not sales_data:
            return []

        def get_fy_year(date):
            """Get financial year from date"""
            return date.year if date.month >= 4 else date.year - 1

        # Group sales by period
        group1 = []  # Apr 1 - Jul 15
        group2 = []  # Jul 16 - Sep 15
        group3 = []  # Sep 16 - Dec 15
        group4 = []  # Dec 16 - Mar 31

        for item in sales_data:
            sale_date = pd.to_datetime(item['Sale Date'])
            month = sale_date.month
            day = sale_date.day

            if (month >= 4 and month <= 6) or (month == 7 and day <= 15):
                group1.append(item)
            elif (month == 7 and day > 15) or month == 8 or (month == 9 and day <= 15):
                group2.append(item)
            elif (month == 9 and day > 15) or month == 10 or month == 11 or (month == 12 and day <= 15):
                group3.append(item)
            else:  # Dec 16 - Mar 31
                group4.append(item)

        # Build summary rows
        result = []

        if group1:
            fy_year = get_fy_year(pd.to_datetime(group1[0]['Sale Date']))
            result.append({
                'Sale Period': f'Apr 1 - Jul 15, {fy_year}',
                'Financial Year': f'FY {fy_year}-{str(fy_year+1)[-2:]}',
                'Tax Type': 'Advance Tax',
                'Total Tax (INR)': sum(item['Tax Amount (INR)'] for item in group1),
                'By Jul 15': sum(item['Adv Tax by Jul 15 (15%)'] for item in group1),
                'By Sep 15': sum(item['Adv Tax by Sep 15 (45%)'] for item in group1),
                'By Dec 15': sum(item['Adv Tax by Dec 15 (75%)'] for item in group1),
                'By Mar 15': sum(item['Adv Tax by Mar 15 (100%)'] for item in group1),
                'Note': 'All 4 deadlines apply'
            })

        if group2:
            fy_year = get_fy_year(pd.to_datetime(group2[0]['Sale Date']))
            result.append({
                'Sale Period': f'Jul 16 - Sep 15, {fy_year}',
                'Financial Year': f'FY {fy_year}-{str(fy_year+1)[-2:]}',
                'Tax Type': 'Advance Tax',
                'Total Tax (INR)': sum(item['Tax Amount (INR)'] for item in group2),
                'By Jul 15': sum(item['Adv Tax by Jul 15 (15%)'] for item in group2),
                'By Sep 15': sum(item['Adv Tax by Sep 15 (45%)'] for item in group2),
                'By Dec 15': sum(item['Adv Tax by Dec 15 (75%)'] for item in group2),
                'By Mar 15': sum(item['Adv Tax by Mar 15 (100%)'] for item in group2),
                'Note': 'Jul 15 deadline passed'
            })

        if group3:
            fy_year = get_fy_year(pd.to_datetime(group3[0]['Sale Date']))
            result.append({
                'Sale Period': f'Sep 16 - Dec 15, {fy_year}',
                'Financial Year': f'FY {fy_year}-{str(fy_year+1)[-2:]}',
                'Tax Type': 'Advance Tax',
                'Total Tax (INR)': sum(item['Tax Amount (INR)'] for item in group3),
                'By Jul 15': sum(item['Adv Tax by Jul 15 (15%)'] for item in group3),
                'By Sep 15': sum(item['Adv Tax by Sep 15 (45%)'] for item in group3),
                'By Dec 15': sum(item['Adv Tax by Dec 15 (75%)'] for item in group3),
                'By Mar 15': sum(item['Adv Tax by Mar 15 (100%)'] for item in group3),
                'Note': 'Jul/Sep deadlines passed'
            })

        if group4:
            fy_year = get_fy_year(pd.to_datetime(group4[0]['Sale Date']))
            # Handle year transition: Dec-Mar crosses calendar year
            year_display = fy_year if pd.to_datetime(group4[0]['Sale Date']).month >= 4 else fy_year
            result.append({
                'Sale Period': f'Dec 16, {year_display} - Mar 31, {year_display+1}',
                'Financial Year': f'FY {fy_year}-{str(fy_year+1)[-2:]}',
                'Tax Type': 'Advance Tax',
                'Total Tax (INR)': sum(item['Tax Amount (INR)'] for item in group4),
                'By Jul 15': sum(item['Adv Tax by Jul 15 (15%)'] for item in group4),
                'By Sep 15': sum(item['Adv Tax by Sep 15 (45%)'] for item in group4),
                'By Dec 15': sum(item['Adv Tax by Dec 15 (75%)'] for item in group4),
                'By Mar 15': sum(item['Adv Tax by Mar 15 (100%)'] for item in group4),
                'Note': 'Only Mar 15 deadline applies'
            })

        return result
