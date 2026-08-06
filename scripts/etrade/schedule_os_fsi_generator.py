"""
ITR-FA-GENERATOR - Schedule FA Generator for ITR2/ITR3
Copyright (c) 2024-2026 Satvinder Singh
Licensed under GNU General Public License

ScheduleOSFSIGenerator
Handles Schedule OS (Other Sources) and Schedule FSI (Foreign Source Income) calculation
"""

import math
import calendar
import pandas as pd


class ScheduleOSFSIGenerator:
    """Generate Schedule OS and FSI for dividend income and foreign source income"""

    def __init__(self, forex_manager, calendar_year=2025):
        """
        Args:
            forex_manager (ForexManager): For TTBR exchange rates
            calendar_year (int): Calendar year (for FY calculations)
        """
        self.forex_manager = forex_manager
        self.calendar_year = calendar_year

        # Schedule OS uses FINANCIAL YEAR (Apr-Mar), NOT calendar year
        self.fy_start = f"{calendar_year}-04-01"
        self.fy_end = f"{calendar_year + 1}-03-31"
        self.indian_fy = f"{calendar_year}-{str(calendar_year + 1)[-2:]}"
        self.assessment_year = f"{calendar_year + 1}-{str(calendar_year + 2)[-2:]}"

    def calculate_schedule_os(self, df_dividends):
        """
        Calculate Schedule OS (Other Sources) using Rule 115(1)(e).

        Rule 115(1)(e): Last day of month BEFORE dividend month

        Args:
            df_dividends (DataFrame): Dividend data with columns:
                                      ['Symbol', 'Date', 'Amount (USD)', 'TTBR', 'Amount (INR)']

        Returns:
            tuple: (df_schedule_os, df_div_os)
                   df_schedule_os: Schedule OS summary DataFrame
                   df_div_os: Detailed dividend data with Rule 115(1)(e) rates
        """
        # Filter dividends to Financial Year
        if not df_dividends.empty:
            df_div_fy = df_dividends.copy()
            df_div_fy['Date'] = pd.to_datetime(df_div_fy['Date'])
            df_div_fy = df_div_fy[(df_div_fy['Date'] >= self.fy_start) & (df_div_fy['Date'] <= self.fy_end)].copy()
        else:
            df_div_fy = pd.DataFrame(columns=['Symbol', 'Date', 'Amount (USD)', 'TTBR', 'Amount (INR)'])

        # Recalculate dividends using Rule 115(1)(e) for Schedule OS
        div_os_data = []
        for _, row in df_div_fy.iterrows():
            div_date = pd.to_datetime(row['Date'])
            amount_usd = row['Amount (USD)']

            # Rule 115(1)(e): Last day of month BEFORE dividend month
            if div_date.month == 1:
                specified_year = div_date.year - 1
                specified_month = 12
            else:
                specified_year = div_date.year
                specified_month = div_date.month - 1

            last_day = calendar.monthrange(specified_year, specified_month)[1]
            specified_date_str = f"{specified_year}-{specified_month:02d}-{last_day:02d}"

            # Get TTBR for specified date using Rule 115(1)(e)
            ttbr_os = self.forex_manager.get_rule_115_1_e_ttbr(div_date.strftime('%Y-%m-%d'))
            amount_inr_os = math.ceil(amount_usd * ttbr_os)

            div_os_data.append({
                'Symbol': row['Symbol'],
                'Date': div_date.strftime('%Y-%m-%d'),
                'Amount (USD)': amount_usd,
                'Specified Date (Rule 115(1)(e))': specified_date_str,
                'TTBR': round(ttbr_os, 2),
                'Amount (INR)': amount_inr_os
            })

        df_div_os = pd.DataFrame(div_os_data)

        # Calculate quarterly breakup (Section 234C)
        # Quarter 1: Apr 1 - Jun 15
        # Quarter 2: Jun 16 - Sep 15
        # Quarter 3: Sep 16 - Dec 15
        # Quarter 4: Dec 16 - Mar 15
        # Quarter 5: Mar 16 - Mar 31

        quarterly_breakup = {
            'Q1 (Apr 1 - Jun 15)': 0,
            'Q2 (Jun 16 - Sep 15)': 0,
            'Q3 (Sep 16 - Dec 15)': 0,
            'Q4 (Dec 16 - Mar 15)': 0,
            'Q5 (Mar 16 - Mar 31)': 0
        }

        for _, row in df_div_os.iterrows():
            div_date = pd.to_datetime(row['Date'])
            amount = row['Amount (INR)']
            month = div_date.month
            day = div_date.day

            # Determine quarter based on payment date
            if month <= 6 and (month < 6 or day <= 15):
                quarterly_breakup['Q1 (Apr 1 - Jun 15)'] += amount
            elif month <= 9 and (month < 9 or day <= 15):
                quarterly_breakup['Q2 (Jun 16 - Sep 15)'] += amount
            elif month <= 12 and (month < 12 or day <= 15):
                quarterly_breakup['Q3 (Sep 16 - Dec 15)'] += amount
            elif month <= 3 or (month == 3 and day <= 15):
                quarterly_breakup['Q4 (Dec 16 - Mar 15)'] += amount
            else:
                quarterly_breakup['Q5 (Mar 16 - Mar 31)'] += amount

        # Build Schedule OS DataFrame
        total_div_usd = df_div_os['Amount (USD)'].sum() if not df_div_os.empty else 0
        total_div_inr = df_div_os['Amount (INR)'].sum() if not df_div_os.empty else 0

        os_data = {
            'Indian Financial Year': [
                'Assessment Year',
                'Total Dividend Income (USD)',
                'Total Dividend Income (INR Rs.)',
                '',
                'Quarter (Section 234C)',
                '',
                'WARNINGS / NOTES'
            ],
            self.indian_fy: [
                self.assessment_year,
                round(total_div_usd, 2),
                int(total_div_inr),
                '',
                'Dividend Income (INR Rs.)',
                '',
                ''
            ]
        }

        # Add quarterly rows
        for quarter, amount in quarterly_breakup.items():
            os_data['Indian Financial Year'].append(quarter)
            os_data[self.indian_fy].append(int(amount))

        # Add warning if no dividends
        if total_div_inr == 0:
            os_data['Indian Financial Year'].append('')
            os_data[self.indian_fy].append(f"• No dividend activity found in Indian FY {self.indian_fy} (Apr-Mar)")

        df_schedule_os = pd.DataFrame(os_data)

        return df_schedule_os, df_div_os

    def calculate_schedule_fsi(self, df_dividends, df_capital_gains):
        """
        Calculate Schedule FSI (Foreign Source Income).

        Aggregates dividend + capital gains income from Financial Year.

        Args:
            df_dividends (DataFrame): Dividend data (Schedule FA format)
            df_capital_gains (DataFrame): Capital gains data with 'Sale Date' and 'Capital Gain (INR)'

        Returns:
            DataFrame: Schedule FSI summary
        """
        # Calculate total dividends in FY
        if not df_dividends.empty:
            df_div_fy = df_dividends.copy()
            df_div_fy['Date'] = pd.to_datetime(df_div_fy['Date'])
            df_div_fy = df_div_fy[(df_div_fy['Date'] >= self.fy_start) & (df_div_fy['Date'] <= self.fy_end)]
            total_div_inr = int(df_div_fy['Amount (INR)'].sum()) if not df_div_fy.empty else 0
        else:
            total_div_inr = 0

        # Calculate total capital gains in FY
        total_cg_inr = 0
        if not df_capital_gains.empty:
            # Filter capital gains to Financial Year
            df_cg_fy = df_capital_gains.copy()
            df_cg_fy['Sale Date'] = pd.to_datetime(df_cg_fy['Sale Date'])
            df_cg_fy = df_cg_fy[(df_cg_fy['Sale Date'] >= self.fy_start) & (df_cg_fy['Sale Date'] <= self.fy_end)]
            total_cg_inr = int(df_cg_fy['Capital Gain (INR)'].sum()) if not df_cg_fy.empty else 0

        total_foreign_income = int(total_div_inr + total_cg_inr)

        # TODO: Extract NRA withholding from Transaction History
        total_tax_paid_usd = 0
        total_tax_paid_inr = 0

        # Build FSI summary section (only 2 columns)
        fsi_data = {
            'Indian Financial Year': [
                'Assessment Year',
                'Dividend Income (Foreign)',
                'Capital Gains Income (Foreign, per Schedule CG)',
                'Total Foreign Source Income',
                'Total Tax Paid Outside India',
                'Total Tax Relief Available (Schedule TR)',
                '',
                'WARNINGS / NOTES'
            ],
            self.indian_fy: [
                self.assessment_year,
                int(total_div_inr),
                total_cg_inr,
                total_foreign_income,
                total_tax_paid_inr,
                0,  # Tax relief calculated later
                '',
                ''
            ]
        }

        # Add warning notes if applicable
        if total_div_inr == 0 and total_cg_inr == 0:
            fsi_data['Indian Financial Year'].append('')
            fsi_data[self.indian_fy].append(f"• No dividend, NRA withholding, or capital-gains activity found in Indian FY {self.indian_fy} (Apr-Mar)")

        df_schedule_fsi = pd.DataFrame(fsi_data)

        return df_schedule_fsi
