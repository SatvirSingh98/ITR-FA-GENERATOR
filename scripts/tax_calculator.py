"""
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
