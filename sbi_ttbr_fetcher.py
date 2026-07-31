"""
SBI TTBR (TT Buying Rate) Fetcher
Fetches USD/INR exchange rates from SBI official source.

Priority:
1. Try downloading from SBI official PDF
2. Parse PDF and extract TT BUY rates
3. Fall back to GitHub CSV if SBI fails
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
    Extract USD/INR TT BUY rates from SBI PDF.
    Returns DataFrame with columns: Date, TTBR
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

        date_str = date_obj.strftime('%Y-%m-%d')

        # Extract USD/INR TT BUY rate
        # Pattern: USD/INR followed by rates
        # Example line: "USD/INR 83.57 84.42 83.50 84.59 83.50 84.59 82.55 84.90"
        # TT BUY is the first number after USD/INR

        currency_line_regex = re.compile(r'USD\/INR\s+([\d.]+)')
        match = re.search(currency_line_regex, reference_page)

        if match:
            tt_buy_rate = float(match.group(1))
            print(f"[OK] Extracted rate: {date_str} -> {tt_buy_rate}")

            # Return as DataFrame in our format
            df = pd.DataFrame({
                'Date': [date_str],
                'TTBR': [tt_buy_rate]
            })
            return df
        else:
            print("[!] Could not find USD/INR rate in PDF")
            return None

    except Exception as e:
        print(f"[!] Error parsing PDF: {e}")
        return None


def download_from_github() -> Optional[pd.DataFrame]:
    """
    Fallback: Download historical rates from GitHub CSV.
    Returns DataFrame with columns: Date, TTBR
    """
    try:
        print(f"[*] Falling back to GitHub CSV...")
        response = requests.get(GITHUB_CSV_URL, timeout=10, verify=False)
        response.raise_for_status()

        # Parse CSV
        df = pd.read_csv(io.StringIO(response.text))

        # Extract Date and TT BUY columns
        # GitHub CSV format: DATE, PDF FILE, TT BUY, TT SELL, ...
        if 'DATE' in df.columns and 'TT BUY' in df.columns:
            # Convert DATE to our format (YYYY-MM-DD)
            df['Date'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M').dt.strftime('%Y-%m-%d')
            df['TTBR'] = df['TT BUY'].astype(float)

            # Keep only Date and TTBR
            result = df[['Date', 'TTBR']].copy()

            print(f"[OK] Downloaded {len(result)} records from GitHub")
            return result
        else:
            print(f"[!] GitHub CSV has unexpected format")
            return None

    except Exception as e:
        print(f"[!] Failed to download from GitHub: {e}")
        return None


def fetch_sbi_ttbr_rates(specific_dates: Optional[list] = None) -> pd.DataFrame:
    """
    Main function to fetch SBI TTBR rates.

    Args:
        specific_dates: Optional list of dates in YYYY-MM-DD format to fetch

    Returns:
        DataFrame with columns: Date, TTBR

    Approach:
    1. Try downloading from SBI PDF (gets today's rate)
    2. Merge with GitHub historical data
    3. Fall back to GitHub only if SBI fails
    """
    print("\n[*] Fetching SBI TTBR rates...")

    # Try SBI PDF first (for latest rate)
    sbi_df = None
    pdf_content = download_sbi_pdf()
    if pdf_content:
        sbi_df = extract_usd_rates_from_pdf(pdf_content)

    # Get historical data from GitHub
    github_df = download_from_github()

    # Combine both sources
    if sbi_df is not None and github_df is not None:
        # Merge: Use SBI for latest date, GitHub for historical
        combined = pd.concat([github_df, sbi_df], ignore_index=True)
        # Remove duplicates, keep the SBI version (last occurrence)
        combined = combined.drop_duplicates(subset='Date', keep='last')
        combined = combined.sort_values('Date').reset_index(drop=True)
        print(f"[OK] Combined SBI + GitHub data: {len(combined)} total records")
        result = combined
    elif sbi_df is not None:
        print(f"[OK] Using SBI data only: {len(sbi_df)} records")
        result = sbi_df
    elif github_df is not None:
        print(f"[OK] Using GitHub data only: {len(github_df)} records")
        result = github_df
    else:
        raise Exception("Failed to fetch TTBR rates from both SBI and GitHub")

    # Filter for specific dates if requested
    if specific_dates:
        result = result[result['Date'].isin(specific_dates)].copy()
        print(f"[i] Filtered to {len(result)} records for requested dates")

    # Ensure proper data types
    result['Date'] = pd.to_datetime(result['Date']).dt.strftime('%Y-%m-%d')
    result['TTBR'] = result['TTBR'].astype(float)

    return result


if __name__ == "__main__":
    # Test the fetcher
    try:
        df = fetch_sbi_ttbr_rates()
        print("\nSample data:")
        print(df.tail(10))

        # Save to CSV for inspection
        output_file = "sbi_ttbr_test.csv"
        df.to_csv(output_file, index=False)
        print(f"\n[OK] Saved to {output_file}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
