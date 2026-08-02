"""
ITR-FA-GENERATOR - SBI Forex Fetcher
Copyright (C) 2025 Satvir Singh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

---

SBI Forex Fetcher
Fetches all 8 USD/INR forex rates from SBI official source.

Rates extracted:
- TT BUY, TT SELL
- BILL BUY, BILL SELL
- FOREX TRAVEL CARD BUY, FOREX TRAVEL CARD SELL
- CN BUY, CN SELL

Priority:
1. Try downloading from SBI official PDF
2. Parse PDF and extract all 8 forex rates
3. Fall back to GitHub CSV for historical data
"""

import io
import os
import re
import logging
from datetime import datetime
from typing import Optional
import pandas as pd
import requests
import PyPDF2


# SBI Official URLs
SBI_DAILY_RATES_URL = "https://sbi.bank.in/documents/16012/1400784/FOREX_CARD_RATES.pdf"
SBI_DAILY_RATES_URL_FALLBACK = "https://bank.sbi/documents/16012/1400784/FOREX_CARD_RATES.pdf"

# GitHub fallback
GITHUB_CSV_URL = "https://raw.githubusercontent.com/sahilgupta/sbi-fx-ratekeeper/main/csv_files/SBI_REFERENCE_RATES_USD.csv"

# Setup logging
logger = logging.getLogger(__name__)


def download_sbi_pdf() -> Optional[io.BytesIO]:
    """
    Download the latest SBI forex rates PDF.
    Returns BytesIO object or None if failed.
    """
    urls = [SBI_DAILY_RATES_URL, SBI_DAILY_RATES_URL_FALLBACK]

    for url in urls:
        try:
            print(f"[*] Attempting to download SBI PDF from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Verify it's a PDF
            if response.content[:4] == b'%PDF':
                print(f"[OK] Downloaded SBI PDF successfully")
                return io.BytesIO(response.content)
            else:
                print(f"[!] Downloaded file is not a valid PDF")
        except Exception as e:
            print(f"[!] Failed to download from {url}: {e}")

    return None


def extract_date_from_pdf(text: str) -> Optional[datetime]:
    """
    Extract date from PDF text.
    Looks for lines like "Date : 31-Jul-2026" or "Date: 31/07/2026"
    """
    date_line = None
    for line in text.split('\n'):
        if line.strip().lower().startswith('date'):
            date_line = line
            break

    if not date_line:
        return None

    try:
        # Try different date formats
        from dateutil import parser
        parsed_date = parser.parse(date_line, fuzzy=True, dayfirst=True)
        return parsed_date
    except:
        return None


def extract_usd_rates_from_pdf(file_content: io.BytesIO) -> Optional[pd.DataFrame]:
    """
    Extract ALL USD/INR forex rates from SBI PDF.
    Returns DataFrame with columns: DATE, PDF FILE, TT BUY, TT SELL, BILL BUY, BILL SELL,
                                     FOREX TRAVEL CARD BUY, FOREX TRAVEL CARD SELL, CN BUY, CN SELL
    """
    try:
        reader = PyPDF2.PdfReader(file_content, strict=False)

        # Search first 2 pages for reference rates
        reference_page = None
        for page in reader.pages[:2]:
            page_text = page.extract_text()
            if "to be used as reference rates" in page_text.lower():
                reference_page = page_text
                break

        if not reference_page:
            print("[!] Could not find reference rates page in PDF")
            return None

        # Extract date
        date_obj = extract_date_from_pdf(reference_page)
        if not date_obj:
            print("[!] Could not extract date from PDF")
            return None

        date_str = date_obj.strftime('%Y-%m-%d')  # Just date, no time

        # Extract USD/INR rates
        # Pattern: USD/INR followed by 8 rates
        # Example line: "USD/INR 83.57 84.42 83.50 84.59 83.50 84.59 82.55 84.90"
        # Order: TT_BUY TT_SELL BILL_BUY BILL_SELL TC_BUY TC_SELL CN_BUY CN_SELL

        currency_line_regex = re.compile(
            r'USD\/INR\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
        )
        match = re.search(currency_line_regex, reference_page)

        if match:
            tt_buy = float(match.group(1))
            tt_sell = float(match.group(2))
            bill_buy = float(match.group(3))
            bill_sell = float(match.group(4))
            tc_buy = float(match.group(5))
            tc_sell = float(match.group(6))
            cn_buy = float(match.group(7))
            cn_sell = float(match.group(8))

            print(f"[OK] Extracted all rates for {date_str}")
            print(f"     TT BUY: {tt_buy}, TT SELL: {tt_sell}")
            print(f"     BILL BUY: {bill_buy}, BILL SELL: {bill_sell}")
            print(f"     TC BUY: {tc_buy}, TC SELL: {tc_sell}")
            print(f"     CN BUY: {cn_buy}, CN SELL: {cn_sell}")

            # Return as DataFrame without PDF FILE column (we don't store PDFs)
            df = pd.DataFrame({
                'DATE': [date_str],
                'TT BUY': [tt_buy],
                'TT SELL': [tt_sell],
                'BILL BUY': [bill_buy],
                'BILL SELL': [bill_sell],
                'FOREX TRAVEL CARD BUY': [tc_buy],
                'FOREX TRAVEL CARD SELL': [tc_sell],
                'CN BUY': [cn_buy],
                'CN SELL': [cn_sell]
            })
            return df
        else:
            print("[!] Could not find USD/INR rates in PDF")
            return None

    except Exception as e:
        print(f"[!] Error parsing PDF: {e}")
        return None


def download_from_github() -> Optional[pd.DataFrame]:
    """
    Fallback: Download historical rates from GitHub CSV.
    Returns DataFrame with all columns matching GitHub format
    """
    try:
        print(f"[*] Falling back to GitHub CSV...")
        response = requests.get(GITHUB_CSV_URL, timeout=10, verify=False)
        response.raise_for_status()

        # Parse CSV - drop PDF FILE column and clean DATE
        df = pd.read_csv(io.StringIO(response.text))

        # Verify required columns exist
        required_cols = ['DATE', 'TT BUY', 'TT SELL', 'BILL BUY', 'BILL SELL',
                        'FOREX TRAVEL CARD BUY', 'FOREX TRAVEL CARD SELL', 'CN BUY', 'CN SELL']

        if all(col in df.columns for col in required_cols):
            # Drop PDF FILE column if it exists
            if 'PDF FILE' in df.columns:
                df = df.drop(columns=['PDF FILE'])

            # Convert DATE to just date (remove time)
            df['DATE'] = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d')

            print(f"[OK] Downloaded {len(df)} records from GitHub")
            return df
        else:
            print(f"[!] GitHub CSV missing required columns")
            return None

    except Exception as e:
        print(f"[!] Failed to download from GitHub: {e}")
        return None


def fetch_sbi_forex_rates(specific_dates: Optional[list] = None) -> pd.DataFrame:
    """
    Main function to fetch SBI forex rates (all 8 rates).

    Args:
        specific_dates: Optional list of dates in YYYY-MM-DD format to fetch

    Returns:
        DataFrame with columns: DATE, PDF FILE, TT BUY, TT SELL, BILL BUY, BILL SELL,
                                FOREX TRAVEL CARD BUY, FOREX TRAVEL CARD SELL, CN BUY, CN SELL

    Approach:
    1. Try downloading from SBI PDF (gets today's rates)
    2. Merge with GitHub historical data
    3. Fall back to GitHub only if SBI fails
    """
    print("\n[*] Fetching SBI forex rates...")

    # Try SBI PDF first (for latest rates)
    sbi_df = None
    pdf_content = download_sbi_pdf()
    if pdf_content:
        sbi_df = extract_usd_rates_from_pdf(pdf_content)

        # Check if SBI PDF has today's date - if not, don't use it
        if sbi_df is not None:
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            sbi_date = sbi_df['DATE'].iloc[0]

            if sbi_date == today:
                print(f"[OK] SBI PDF has today's date ({today}) - will use it")
            else:
                print(f"[!] SBI PDF has stale date ({sbi_date}), expected today ({today})")
                print(f"[!] Skipping SBI data - PDF not yet updated")
                sbi_df = None

    # Get historical data from GitHub
    github_df = download_from_github()

    # Combine both sources
    if sbi_df is not None and github_df is not None:
        # Merge: Use SBI for latest date, GitHub for historical
        combined = pd.concat([github_df, sbi_df], ignore_index=True)
        # Remove duplicates based on DATE, keep the SBI version (last occurrence)
        combined = combined.drop_duplicates(subset='DATE', keep='last')
        combined = combined.sort_values('DATE').reset_index(drop=True)
        print(f"[OK] Combined SBI + GitHub data: {len(combined)} total records")
        result = combined
    elif sbi_df is not None:
        print(f"[OK] Using SBI data only: {len(sbi_df)} records")
        result = sbi_df
    elif github_df is not None:
        print(f"[OK] Using GitHub data only: {len(github_df)} records")
        result = github_df
    else:
        raise Exception("Failed to fetch forex rates from both SBI and GitHub")

    # Filter for specific dates if requested
    if specific_dates:
        # Convert DATE column to just date for comparison
        result['_date_only'] = pd.to_datetime(result['DATE']).dt.strftime('%Y-%m-%d')
        result = result[result['_date_only'].isin(specific_dates)].copy()
        result = result.drop(columns=['_date_only'])
        print(f"[i] Filtered to {len(result)} records for requested dates")

    return result


if __name__ == "__main__":
    # Test the fetcher
    try:
        df = fetch_sbi_forex_rates()
        print("\nSample data (latest 5 records):")
        print(df.tail(5))

        # Save to CSV in GitHub-compatible format
        output_file = "SBI_FOREX_CARD_RATES_USD.csv"
        df.to_csv(output_file, index=False)
        print(f"\n[OK] Saved to {output_file}")
        print(f"[i] Total records: {len(df)}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
