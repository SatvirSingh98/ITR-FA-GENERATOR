"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

CapitalGainsGenerator
Calculates capital gains for dual-regime tax computation
"""

import pandas as pd
import calendar
from datetime import datetime
import math


class CapitalGainsGenerator:
    """Generate capital gains calculations for both New and Old tax regimes"""

    def __init__(self, forex_manager, tax_calculator):
        """
        Initialize capital gains generator

        Args:
            forex_manager (ForexManager): Forex rate manager instance
            tax_calculator (TaxCalculator): Tax calculator instance
        """
        self.forex_manager = forex_manager
        self.tax_calculator = tax_calculator

    def process_sales(self, df_sold_extended):
        """
        Process all sales and calculate capital gains base data

        Args:
            df_sold_extended (DataFrame): Sales from G&L (extended period)

        Returns:
            list: Capital gains data (without regime-specific tax calculations)
        """
        if df_sold_extended.empty:
            print("[*] No sales to process")
            return []

        capital_gains_data = []

        for _, row in df_sold_extended.iterrows():
            sale_date = pd.to_datetime(row['Date Sold'])
            acq_date = pd.to_datetime(row['Date Acquired'])

            # Extract quantity and nature
            qty = int(row['Quantity Sold'])
            symbol = row['Symbol']
            plan_type = row.get('Plan Type', 'Stock')

            # Determine nature prefix
            if 'RSU' in str(plan_type).upper() or 'RESTRICTED' in str(plan_type).upper():
                nature = f"RSU ({qty} shares)"
            elif 'ESPP' in str(plan_type).upper() or 'EMPLOYEE' in str(plan_type).upper():
                nature = f"ESPP ({qty} shares)"
            else:
                nature = f"Stock ({qty} shares)"

            # Calculate holding period in CALENDAR MONTHS
            holding_months = self.calculate_holding_period(acq_date, sale_date)

            # Determine tax type and section
            if holding_months > 24:
                tax_type = "LTCG"
                tax_section = "Section 112"
            else:
                tax_type = "STCG"
                tax_section = "Section 48"

            # Calculate proceeds and cost basis
            proceeds_usd = float(row['Total Proceeds'])

            # Use correct FMV per Section 49(2AA)
            is_espp = 'ESPP' in str(plan_type).upper() or 'EMPLOYEE' in str(plan_type).upper()
            if is_espp and 'Purchase Date Fair Mkt. Value' in row and pd.notna(row['Purchase Date Fair Mkt. Value']):
                unit_cost_basis = float(row['Purchase Date Fair Mkt. Value'])
            else:
                unit_cost_basis = float(row['Adjusted Cost Basis Per Share'])

            cost_basis_usd = unit_cost_basis * qty

            # Apply Rule 115(1)(f) for exchange rate
            specified_date, specified_ttbr = self.forex_manager.get_rule_115_1_f_ttbr(sale_date)

            # Calculate INR amounts
            gross_proceeds = math.ceil(proceeds_usd * specified_ttbr)
            cost_basis = math.ceil(cost_basis_usd * specified_ttbr)
            capital_gain = gross_proceeds - cost_basis

            # Store base capital gains data
            capital_gains_data.append({
                'Nature': nature,
                'Quantity': qty,
                'Acquisition Date': acq_date.strftime('%Y-%m-%d'),
                'Sale Date': sale_date.strftime('%Y-%m-%d'),
                'Rule 115(1)(f) Specified Date': specified_date.strftime('%Y-%m-%d'),
                'TTBR (INR/USD)': round(specified_ttbr, 2),
                'Holding Period (months)': holding_months,
                'Tax Type': tax_type,
                'Section': tax_section,
                'Cost Basis (INR)': cost_basis,
                'Sale Proceeds (INR)': gross_proceeds,
                'Capital Gain (INR)': capital_gain,
            })

        print(f"[OK] Processed {len(capital_gains_data)} capital gains transactions")
        return capital_gains_data

    def calculate_holding_period(self, acq_date, sale_date):
        """
        Calculate holding period in calendar months

        Args:
            acq_date: Acquisition date (datetime)
            sale_date: Sale date (datetime)

        Returns:
            int: Holding period in months
        """
        return (sale_date.year - acq_date.year) * 12 + (sale_date.month - acq_date.month)

    def calculate_tax_for_regime(self, capital_gains_data, regime='new'):
        """
        Calculate tax and advance tax schedule for a specific regime

        Args:
            capital_gains_data (list): Base capital gains data
            regime (str): 'new' or 'old'

        Returns:
            list: Capital gains with tax amounts and advance tax schedule
        """
        result = []

        for item in capital_gains_data:
            capital_gain = item['Capital Gain (INR)']
            tax_type = item['Tax Type']
            sale_date = item['Sale Date']

            # Calculate tax amount for this regime
            tax_amount = self.tax_calculator.calculate_tax(capital_gain, tax_type, regime)

            # Get appropriate tax rate
            if tax_type == 'LTCG':
                tax_rate = self.tax_calculator.get_ltcg_rate()
            else:
                tax_rate = self.tax_calculator.get_stcg_rate(regime)

            # Calculate advance tax installments
            installments = self.tax_calculator.calculate_advance_tax_installment(tax_amount, sale_date)

            # Build result row
            result.append({
                **item,  # Include all base fields
                'Tax Rate': f"{tax_rate*100}%",
                'Tax Amount (INR)': tax_amount,
                'Adv Tax by Jul 15 (15%)': installments['jul'],
                'Adv Tax by Sep 15 (45%)': installments['sep'],
                'Adv Tax by Dec 15 (75%)': installments['dec'],
                'Adv Tax by Mar 15 (100%)': installments['mar'],
            })

        return result

    def generate_dual_regime_results(self, capital_gains_data):
        """
        Generate capital gains results for BOTH regimes

        Args:
            capital_gains_data (list): Base capital gains data

        Returns:
            tuple: (new_regime_results, old_regime_results)
        """
        new_regime = self.calculate_tax_for_regime(capital_gains_data, regime='new')
        old_regime = self.calculate_tax_for_regime(capital_gains_data, regime='old')

        return new_regime, old_regime

    def create_sale_details_dataframe(self, capital_gains_list):
        """
        Create DataFrame for sale details (for Excel output)

        Args:
            capital_gains_list (list): Capital gains with tax calculations

        Returns:
            DataFrame: Sale details table (empty with columns if no sales)
        """
        if not capital_gains_list:
            # Return empty DataFrame with proper columns (for Excel display)
            return pd.DataFrame(columns=[
                'Nature', 'Quantity', 'Acquisition Date', 'Sale Date',
                'Rule 115(1)(f) Specified Date', 'TTBR (INR/USD)',
                'Holding Period (months)', 'Tax Type', 'Section',
                'Cost Basis (INR)', 'Sale Proceeds (INR)', 'Capital Gain (INR)',
                'Tax Rate', 'Tax Amount (INR)'
            ])

        return pd.DataFrame([{
            'Nature': item['Nature'],
            'Quantity': item['Quantity'],
            'Acquisition Date': item['Acquisition Date'],
            'Sale Date': item['Sale Date'],
            'Rule 115(1)(f) Specified Date': item['Rule 115(1)(f) Specified Date'],
            'TTBR (INR/USD)': item['TTBR (INR/USD)'],
            'Holding Period (months)': item['Holding Period (months)'],
            'Tax Type': item['Tax Type'],
            'Section': item['Section'],
            'Cost Basis (INR)': item['Cost Basis (INR)'],
            'Sale Proceeds (INR)': item['Sale Proceeds (INR)'],
            'Capital Gain (INR)': item['Capital Gain (INR)'],
            'Tax Rate': item['Tax Rate'],
            'Tax Amount (INR)': item['Tax Amount (INR)']
        } for item in capital_gains_list])

    def create_advance_tax_dataframe(self, capital_gains_list):
        """
        Create DataFrame for advance tax schedule (grouped by period)

        Args:
            capital_gains_list (list): Capital gains with tax calculations

        Returns:
            DataFrame: Advance tax schedule (empty with columns if no sales)
        """
        if not capital_gains_list:
            # Return empty DataFrame with proper columns
            return pd.DataFrame(columns=[
                'Sale Period', 'Financial Year', 'Tax Type', 'Total Tax (INR)',
                'By Jul 15', 'By Sep 15', 'By Dec 15', 'By Mar 15', 'Note'
            ])

        # Group sales by period
        grouped_rows = self.tax_calculator.group_sales_by_period(capital_gains_list)

        return pd.DataFrame(grouped_rows)
